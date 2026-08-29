"""High-level bot client.

Subclass Client and implement on_* event handlers::

    class MyBot(Client):
        async def on_at_message_create(self, message: Message):
            await message.reply(content="hello")

    bot = MyBot(intents=Intents.default())
    bot.run(appid="...", secret="...")
"""

from __future__ import annotations

import asyncio
import traceback
from types import TracebackType
from typing import Any, Callable, Coroutine, Optional, Type

from .api import BotAPI
from .dispatcher import EventDispatcher
from .flags import Intents
from .gateway import GatewayShard
from .http import HTTPClient
from .logging import get_logger
from .token import TokenManager

__all__ = ["Client"]

_log = get_logger(__name__)


class Client:
    """An asyncio QQ bot client.

    Parameters:
        intents:
            Gateway event subscription mask.
        timeout:
            HTTP request timeout in seconds.
        is_sandbox:
            Use the sandbox API host (mostly for platform debugging).
    """

    def __init__(
        self,
        intents: Intents,
        *,
        timeout: float = 5,
        is_sandbox: bool = False,
    ) -> None:
        if not isinstance(intents, Intents):
            raise TypeError("intents must be an Intents instance")
        self.intents = intents
        self.timeout = timeout
        self.is_sandbox = is_sandbox

        self.api: Optional[BotAPI] = None
        self._token: Optional[TokenManager] = None
        self._http: Optional[HTTPClient] = None
        self._dispatcher: Optional[EventDispatcher] = None
        self._stop_event: Optional[asyncio.Event] = None
        self._tasks: list = []
        self._closed = False
        self._ready = False

    # ------------------------------------------------------------------ #
    # lifecycle
    # ------------------------------------------------------------------ #
    async def __aenter__(self) -> "Client":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        await self.close()

    def run(self, appid: str, secret: str) -> None:
        """Blocking convenience entry point."""
        if not isinstance(appid, str) or not appid.strip():
            raise TypeError("appid 必须是字符串，且不能为空")
        if not isinstance(secret, str) or not secret.strip():
            raise TypeError("secret 必须是字符串，且不能为空")

        try:
            asyncio.run(self.start(appid, secret))
        except KeyboardInterrupt:
            _log.info("[viseron-botpy] 收到 Ctrl+C，机器人已退出")

    async def start(self, appid: str, secret: str, ret_coro: bool = False) -> Optional[Coroutine[Any, Any, None]]:
        """Connect to the gateway and keep running until closed.

        Set ret_coro=True to receive the gateway coroutine instead of awaiting
        it, useful inside an already running event loop.
        """
        if not isinstance(appid, str) or not appid.strip():
            raise TypeError("appid 必须是字符串，且不能为空")
        if not isinstance(secret, str) or not secret.strip():
            raise TypeError("secret 必须是字符串，且不能为空")

        try:
            await self._setup(appid, secret)
            coro = self._run_gateway()
            if ret_coro:
                return coro
            await coro
        except Exception:
            await self.close()
            raise
        return None

    async def _setup(self, appid: str, secret: str) -> None:
        self._closed = False
        self._ready = False
        self._stop_event = asyncio.Event()
        self._token = TokenManager(appid, secret)
        self._http = HTTPClient(self._token, timeout=self.timeout, is_sandbox=self.is_sandbox)
        self.api = BotAPI(self._http)
        self._dispatcher = EventDispatcher(self.ws_dispatch, self.api)

        _log.info("[viseron-botpy] logging in bot %s", appid)
        try:
            self._robot = await self.api.me()
        except Exception as exc:  # noqa: BLE001 - /users/@me is not essential
            _log.warning("[viseron-botpy] could not fetch bot profile: %s", exc)
            self._robot = {}

    async def _run_gateway(self) -> None:
        assert self.api is not None and self._http is not None and self._token is not None
        assert self._dispatcher is not None and self._stop_event is not None

        ws_info = await self._get_ws_info()
        url = ws_info["url"]
        shards = max(int(ws_info.get("shards", 1)), 1)
        session_limit = ws_info.get("session_start_limit") or {}
        max_concurrency = max(int(session_limit.get("max_concurrency", 1)), 1)

        _log.info(
            "[viseron-botpy] gateway url=%s shards=%s max_concurrency=%s",
            url,
            shards,
            max_concurrency,
        )

        interval = max(0.5, 5.0 / max_concurrency)
        for shard_id in range(shards):
            if self._stop_event.is_set():
                break
            shard = GatewayShard(
                shard_id=shard_id,
                shard_count=shards,
                url=url,
                token_manager=self._token,
                intents=self.intents.value,
                dispatcher=self._dispatcher,
                on_error=self._on_gateway_error,
            )
            task = asyncio.create_task(shard.run(self._stop_event), name=f"qqbot-shard-{shard_id}")
            self._tasks.append(task)
            if shard_id + 1 < shards:
                await asyncio.sleep(interval)

        if not self._tasks:
            return

        try:
            await asyncio.gather(*self._tasks)
        except asyncio.CancelledError:
            for task in self._tasks:
                task.cancel()
            await asyncio.gather(*self._tasks, return_exceptions=True)
            if not self._closed:
                raise
        finally:
            if not self._closed:
                await self.close()

    async def _get_ws_info(self) -> dict:
        assert self.api is not None
        # Prefer the sharded endpoint.  Fall back to the generic one when the
        # app has no sharding permission or the endpoint is unavailable.
        try:
            data = await self.api.get_ws_url_shard()
            if isinstance(data, dict) and data.get("url"):
                return data
        except Exception as exc:  # noqa: BLE001
            _log.warning("[viseron-botpy] /gateway/bot failed, falling back to /gateway: %s", exc)

        data = await self.api.get_ws_url()
        if not isinstance(data, dict) or not data.get("url"):
            raise RuntimeError(f"gateway returned invalid data: {data!r}")
        return {"url": data["url"], "shards": 1, "session_start_limit": {"max_concurrency": 1}}

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._ready = False
        if self._stop_event is not None:
            self._stop_event.set()

        for task in self._tasks:
            if not task.done():
                task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()

        if self._http is not None:
            await self._http.close()
        if self._token is not None:
            await self._token.close()

    def is_closed(self) -> bool:
        return self._closed

    @property
    def robot(self) -> Any:
        """Bot profile returned by /users/@me."""
        return getattr(self, "_robot", None)

    # ------------------------------------------------------------------ #
    # event dispatch
    # ------------------------------------------------------------------ #
    def ws_dispatch(self, event: str, *args: Any, **kwargs: Any) -> None:
        method_name = "on_" + event
        method = getattr(self, method_name, None)
        if method is None:
            _log.debug("[viseron-botpy] event %s has no handler %s", event, method_name)
            return
        loop = asyncio.get_running_loop()
        loop.create_task(self._run_event(method, method_name, *args, **kwargs), name=f"qqbot-{method_name}")

    async def _run_event(self, method: Callable[..., Coroutine[Any, Any, Any]], name: str, *args: Any, **kwargs: Any) -> None:
        try:
            await method(*args, **kwargs)
        except asyncio.CancelledError:
            pass
        except Exception:
            try:
                await self.on_error(name, *args, **kwargs)
            except asyncio.CancelledError:
                pass

    async def _on_gateway_error(self, exc: BaseException) -> None:
        _log.error("[viseron-botpy] gateway error: %s", exc)
        await self.on_error("gateway", exc)

    # ------------------------------------------------------------------ #
    # default handlers
    # ------------------------------------------------------------------ #
    async def on_ready(self) -> None:
        """Called after READY is received."""

    async def on_resumed(self) -> None:
        """Called after a session is resumed."""

    async def on_error(self, event_method: str, *args: Any, **kwargs: Any) -> None:
        traceback.print_exc()
