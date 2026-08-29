"""WebSocket gateway client.

The legacy implementation hard-coded the heartbeat interval and pushed
sessions back into a pool after every disconnect.  This implementation:

* uses the heartbeat interval from OpCode 10 Hello,
* owns a single shard connection and performs bounded reconnects,
* preserves the session for OpCode 6 Resume when the close code allows it.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

import aiohttp
from aiohttp import WSMsgType, ClientWebSocketResponse

from .dispatcher import EventDispatcher
from .logging import get_logger
from .token import TokenManager

__all__ = ["GatewayShard"]

_log = get_logger(__name__)

# OpCodes
OP_DISPATCH = 0
OP_HEARTBEAT = 1
OP_IDENTIFY = 2
OP_RESUME = 6
OP_RECONNECT = 7
OP_INVALID_SESSION = 9
OP_HELLO = 10
OP_HEARTBEAT_ACK = 11

# Close codes that allow a resume with the existing session.
_RESUME_CLOSE_CODES = {4008, 4009}
# Close codes that are fatal and must not be retried.
_FATAL_CLOSE_CODES = {4914, 4915}


@dataclass
class GatewayShard:
    """One WebSocket shard.

    Parameters:
        shard_id / shard_count:
            Shard coordinates, e.g. [0, 1] when sharding is disabled.
        url:
            Gateway URL returned by /gateway or /gateway/bot.
        token_manager:
            Token source used for both Identify and Resume.
        intents:
            Integer intent bitmask.
        dispatcher:
            EventDispatcher used for incoming events.
        on_error:
            Optional async callback invoked for connection/protocol errors.
    """

    shard_id: int
    shard_count: int
    url: str
    token_manager: TokenManager
    intents: int
    dispatcher: EventDispatcher
    on_error: Optional[Callable[..., Any]] = None

    session_id: Optional[str] = None
    seq: Optional[int] = None
    heartbeat_interval: float = 45.0
    max_reconnect_delay: float = 30.0

    _ws: Optional[ClientWebSocketResponse] = field(default=None, init=False, repr=False)
    _heartbeat_task: Optional[asyncio.Task] = field(default=None, init=False, repr=False)
    _reconnect_requested: bool = field(default=False, init=False, repr=False)
    _close_code: Optional[int] = field(default=None, init=False, repr=False)

    async def run(self, stop_event: asyncio.Event) -> None:
        """Connect and reconnect until stop_event is set."""
        delay = 1.0
        while not stop_event.is_set():
            try:
                await self._connect_once(stop_event)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001 - report and retry
                if self.on_error is not None:
                    await self.on_error(exc)
                else:
                    _log.error("[viseron_qqbotpy] gateway error: %s", exc)

            if stop_event.is_set():
                break
            if self._close_code in _FATAL_CLOSE_CODES:
                _log.error("[viseron_qqbotpy] fatal gateway close code %s, stopping shard", self._close_code)
                break

            if self._close_code not in _RESUME_CLOSE_CODES:
                # Invalid session, bad shard, bad intent, seq error etc. all
                # require a fresh identify.
                self.session_id = None
                self.seq = None

            await asyncio.sleep(delay)
            delay = min(delay * 2, self.max_reconnect_delay)

    async def _connect_once(self, stop_event: asyncio.Event) -> None:
        self._close_code = None
        self._reconnect_requested = False
        self._ws = None
        self._heartbeat_task = None

        timeout = aiohttp.ClientTimeout(total=30)
        session = aiohttp.ClientSession(timeout=timeout)
        try:
            async with session.ws_connect(self.url) as ws:
                self._ws = ws
                _log.info("[viseron_qqbotpy] shard [%s/%s] connected", self.shard_id, self.shard_count)
                async for message in ws:
                    if stop_event.is_set():
                        return
                    if message.type == WSMsgType.TEXT:
                        await self._handle_text(message.data)
                    elif message.type == WSMsgType.ERROR:
                        exc = ws.exception()
                        if exc is not None:
                            raise exc
                    elif message.type in (WSMsgType.CLOSE, WSMsgType.CLOSED):
                        self._close_code = ws.close_code
                        _log.info(
                            "[viseron_qqbotpy] shard [%s/%s] closed code=%s",
                            self.shard_id,
                            self.shard_count,
                            self._close_code,
                        )
                        return
                    elif message.type == WSMsgType.CLOSING:
                        continue

                    if self._reconnect_requested:
                        _log.info("[viseron_qqbotpy] server requested reconnect")
                        return
        finally:
            if self._reconnect_requested and self._close_code is None:
                # OpCode 7 reconnect should try Resume with the current session.
                self._close_code = 4009

            if self._heartbeat_task is not None:
                self._heartbeat_task.cancel()
                self._heartbeat_task = None

            self._ws = None
            if not session.closed:
                await session.close()

    async def _handle_text(self, raw: str) -> None:
        payload = json.loads(raw)
        op = payload.get("op")
        data = payload.get("d")
        seq = payload.get("s")

        if seq is not None:
            self.seq = int(seq)

        if op == OP_HELLO:
            heartbeat_ms = (data or {}).get("heartbeat_interval", 45000)
            self.heartbeat_interval = max(float(heartbeat_ms) / 1000.0, 1.0)
            if self.session_id:
                await self._send_resume()
            else:
                await self._send_identify()
            self._start_heartbeat()
            return

        if op == OP_HEARTBEAT_ACK:
            _log.debug("[viseron_qqbotpy] heartbeat ack")
            return

        if op == OP_RECONNECT:
            _log.info("[viseron_qqbotpy] server asked to reconnect")
            self._reconnect_requested = True
            return

        if op == OP_INVALID_SESSION:
            _log.warning("[viseron_qqbotpy] invalid session")
            self.session_id = None
            self.seq = None
            self._reconnect_requested = True
            return

        if op == OP_DISPATCH:
            event_type = payload.get("t")
            if not event_type:
                return
            self._dispatch_event(event_type, payload)
            return

        if op == OP_HEARTBEAT:
            # Server heartbeat; reply with our latest sequence number.
            await self._send_heartbeat()

    def _dispatch_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        event = event_type.lower()
        if event == "ready":
            data = payload.get("d", {})
            self.session_id = data.get("session_id")
            shard = data.get("shard") or [self.shard_id, self.shard_count]
            if isinstance(shard, list) and len(shard) >= 2:
                self.shard_id = int(shard[0])
                self.shard_count = int(shard[1])
        elif event == "resumed":
            _log.info("[viseron_qqbotpy] shard [%s/%s] resumed", self.shard_id, self.shard_count)

        parser = self.dispatcher.parsers.get(event)
        if parser is not None:
            parser(payload)
        else:
            _log.debug("[viseron_qqbotpy] no parser for event %s", event_type)

    async def _send_identify(self) -> None:
        token = await self.token_manager.get_access_token()
        payload = {
            "op": OP_IDENTIFY,
            "d": {
                "token": f"QQBot {token}",
                "intents": self.intents,
                "shard": [self.shard_id, self.shard_count],
                "properties": {
                    "$os": "python",
                    "$browser": "viseron_qqbotpy",
                    "$device": "viseron_qqbotpy",
                },
            },
        }
        await self._send_json(payload)

    async def _send_resume(self) -> None:
        token = await self.token_manager.get_access_token()
        payload = {
            "op": OP_RESUME,
            "d": {
                "token": f"QQBot {token}",
                "session_id": self.session_id,
                "seq": self.seq,
            },
        }
        await self._send_json(payload)

    async def _send_heartbeat(self) -> None:
        await self._send_json({"op": OP_HEARTBEAT, "d": self.seq})

    def _start_heartbeat(self) -> None:
        if self._heartbeat_task is not None and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def _heartbeat_loop(self) -> None:
        try:
            while True:
                await asyncio.sleep(self.heartbeat_interval)
                try:
                    await self._send_heartbeat()
                except Exception as exc:  # noqa: BLE001 - heartbeat is best-effort
                    _log.debug("[viseron_qqbotpy] heartbeat send failed: %s", exc)
        except asyncio.CancelledError:
            pass

    async def _send_json(self, payload: Dict[str, Any]) -> None:
        ws = self._ws
        if ws is None or ws.closed:
            return
        await ws.send_json(payload)
