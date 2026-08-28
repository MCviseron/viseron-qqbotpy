"""Async HTTP client for the QQ OpenAPI.

The legacy botpy implementation created a fresh session for token requests,
mutated routes, and had a broken retry path.  This version keeps a single
session, separates URL construction from request state, and normalises errors.
"""

from __future__ import annotations

import asyncio
from json.decoder import JSONDecodeError
from typing import Any, ClassVar, Dict, Optional, Union

import aiohttp
from aiohttp import ClientResponse, ClientSession, TCPConnector

from .errors import APIError
from .logging import get_logger
from .token import TokenManager

__all__ = ["HTTPClient", "Route"]

_log = get_logger(__name__)

API_BASE_URL = "https://api.bot.qq.com"
SANDBOX_BASE_URL = "https://sandbox.api.bot.qq.com"
TRACE_ID_HEADER = "X-Tps-trace-ID"

SUCCESS_STATUSES = (200, 202, 204)
_RETRY_STATUSES = {429, 500, 502, 503, 504}


class Route:
    """An HTTP route with path parameters.

    Example::

        Route("POST", "/guilds/{guild_id}/channels", guild_id="123")
    """

    def __init__(self, method: str, path: str, **path_params: Any) -> None:
        self.method = method.upper()
        self.path = path
        self.path_params = path_params

    def url(self, base_url: str) -> str:
        base = base_url.rstrip("/")
        path = self.path.format_map(self.path_params) if self.path_params else self.path
        return f"{base}{path}"

    def __repr__(self) -> str:
        return f"<Route {self.method} {self.path}>"


class HTTPClient:
    """Shared aiohttp client with automatic Authorization headers."""

    def __init__(
        self,
        token_manager: TokenManager,
        *,
        timeout: Union[int, float] = 5,
        is_sandbox: bool = False,
        session: Optional[ClientSession] = None,
    ) -> None:
        self._token = token_manager
        self.timeout = timeout
        self.base_url = SANDBOX_BASE_URL if is_sandbox else API_BASE_URL
        self._session = session
        self._owns_session = session is None

    async def _get_session(self) -> ClientSession:
        if self._session is None or self._session.closed:
            connector = TCPConnector(limit=100, ttl_dns_cache=300)
            self._session = ClientSession(connector=connector)
            self._owns_session = True
        return self._session

    async def request(self, route: Route, *, retry: int = 0, **kwargs: Any) -> Any:
        """Perform an HTTP request and return decoded JSON (or None for 204)."""
        if retry > 2:
            raise APIError(0, f"request to {route} failed after multiple retries", url=route.url(self.base_url))

        session = await self._get_session()
        token = await self._token.get_access_token()
        headers = {
            "Authorization": f"QQBot {token}",
        }
        headers.update(kwargs.pop("headers", {}))

        url = route.url(self.base_url)
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        try:
            async with session.request(
                route.method,
                url,
                headers=headers,
                timeout=timeout,
                **kwargs,
            ) as response:
                return await self._handle_response(response)
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError) as exc:
            _log.warning("[viseron-qqbotpy] request retry %s/2 for %s: %s", retry + 1, route, exc)
            await asyncio.sleep(min(0.5 * (2 ** retry), 2.0))
            return await self.request(route, retry=retry + 1, **kwargs)

    async def _handle_response(self, response: ClientResponse) -> Any:
        url = str(response.request_info.url)
        trace_id = response.headers.get(TRACE_ID_HEADER)
        status = response.status

        payload: Any = None
        if status != 204:
            try:
                if response.headers.get("content-type", "").startswith("application/json"):
                    payload = await response.json()
                else:
                    text = await response.text()
                    payload = _safe_json(text)
            except (JSONDecodeError, ValueError):
                payload = await response.text()

        if status in SUCCESS_STATUSES:
            if status == 204:
                return None
            # 202 is accepted for async work and may still carry an err_code
            # body.  Treat it as success because the platform did accept it.
            return payload

        error = APIError.from_response(status, payload, url=url)
        error.trace_id = error.trace_id or trace_id
        _log.error(
            "[viseron-qqbotpy] API error url=%s status=%s code=%s trace_id=%s message=%s",
            url,
            status,
            error.code,
            error.trace_id,
            error,
        )
        raise error

    async def close(self) -> None:
        if self._owns_session and self._session is not None and not self._session.closed:
            await self._session.close()

    async def __aenter__(self) -> "HTTPClient":
        await self._get_session()
        return self

    async def __aexit__(self, *exc_info) -> None:
        await self.close()


def _safe_json(text: str) -> Any:
    import json

    text = text.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except (JSONDecodeError, ValueError):
        return text
