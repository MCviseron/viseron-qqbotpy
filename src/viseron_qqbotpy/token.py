"""Access token management with seamless refresh.

The platform grants access tokens that are valid for 7200 seconds.  During the
final 60 seconds of a token's life, requesting a new token returns a *new*
value while the old value remains valid.  TokenManager exploits this window to
switch to a fresh token without ever invalidating an in-flight request.

Implementation notes:

* Only one refresh runs at a time (per manager).
* When the current token enters the refresh window, callers transparently
  trigger a refresh.  If the refresh fails, the still-valid old token is
  returned so the request can proceed.
* When the token is already expired, a failed refresh propagates.
"""

from __future__ import annotations

import asyncio
import time
from typing import Optional

import aiohttp

from .errors import TokenError
from .logging import get_logger

__all__ = ["AccessToken", "TokenManager"]

_log = get_logger(__name__)

TOKEN_URL = "https://api.bot.qq.com/app/getAppAccessToken"
DEFAULT_REFRESH_WINDOW = 60
DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=20)


class AccessToken:
    """An access token and the wall-clock instant at which it expires."""

    __slots__ = ("value", "expires_at")

    def __init__(self, value: str, expires_in: float, *, now: Optional[float] = None) -> None:
        self.value = value
        self.expires_at = (time.time() if now is None else now) + float(expires_in)

    @property
    def remaining(self) -> float:
        return self.expires_at - time.time()

    @property
    def expired(self) -> bool:
        return self.remaining <= 0

    def __repr__(self) -> str:
        return f"<AccessToken expires_at={self.expires_at:.0f} remaining={self.remaining:.0f}s>"


class TokenManager:
    """Fetches, caches and seamlessly refreshes a QQ bot access token.

    Parameters:
        app_id:
            Bot AppID from the QQ open platform.
        secret:
            Bot AppSecret.
        session:
            Optional shared aiohttp session.  If omitted a private session is
            created lazily and closed by :meth:`close`.
        refresh_window:
            How many seconds before expiry a new token may be fetched.
    """

    def __init__(
        self,
        app_id: str,
        secret: str,
        *,
        session: Optional[aiohttp.ClientSession] = None,
        refresh_window: int = DEFAULT_REFRESH_WINDOW,
    ) -> None:
        if not isinstance(app_id, str) or not app_id.strip():
            raise TypeError("app_id 必须是字符串，且不能为空")
        if not isinstance(secret, str) or not secret.strip():
            raise TypeError("secret 必须是字符串，且不能为空")

        self.app_id = app_id.strip()
        self.secret = secret.strip()
        self.refresh_window = refresh_window
        self._session = session
        self._owns_session = session is None
        self._token: Optional[AccessToken] = None
        self._lock = asyncio.Lock()

    @property
    def access_token(self) -> Optional[str]:
        """Return the cached token value, or None before the first fetch."""
        return self._token.value if self._token else None

    async def get_access_token(self) -> str:
        """Return a valid access token, refreshing it when necessary.

        This method is safe to call concurrently from many HTTP requests.
        """
        if self._token is None or self._token.expired:
            async with self._lock:
                # Another coroutine may have refreshed while we waited.
                if self._token is None or self._token.expired:
                    await self._refresh()
        elif self._token.remaining <= self.refresh_window:
            async with self._lock:
                # Re-check inside the lock to avoid duplicate refreshes.
                if self._token is not None and not self._token.expired and self._token.remaining <= self.refresh_window:
                    try:
                        await self._refresh()
                    except Exception as exc:  # noqa: BLE001 - old token is still valid
                        _log.warning("[viseron_qqbotpy] token refresh failed, keeping old token: %s", exc)

        assert self._token is not None
        return self._token.value

    async def refresh(self) -> str:
        """Force a token refresh and return the new token value."""
        async with self._lock:
            await self._refresh()
        assert self._token is not None
        return self._token.value

    async def _refresh(self) -> None:
        session = await self._get_session()
        try:
            async with session.post(
                TOKEN_URL,
                json={"appId": self.app_id, "clientSecret": self.secret},
                timeout=DEFAULT_TIMEOUT,
            ) as response:
                payload = await response.json(content_type=None)
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as exc:
            raise TokenError(f"access token request failed: {exc}") from exc

        if not isinstance(payload, dict) or "access_token" not in payload or "expires_in" not in payload:
            raise TokenError(f"invalid access token response: {payload!r}")

        value = payload["access_token"]
        if not isinstance(value, str) or not value:
            raise TokenError("access token response contained an empty token")

        try:
            expires_in = float(payload["expires_in"])
        except (TypeError, ValueError) as exc:
            raise TokenError(f"invalid expires_in value: {payload.get('expires_in')!r}") from exc

        self._token = AccessToken(value, expires_in)
        _log.info("[viseron_qqbotpy] access_token refreshed, expires_in=%s", expires_in)

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
            self._owns_session = True
        return self._session

    @property
    def authorization(self) -> str:
        """Return the Authorization header value for the current token.

        This is a synchronous convenience; call :meth:`get_access_token`
        first unless the token has already been cached.
        """
        token = self.access_token
        if not token:
            raise TokenError("access token has not been fetched yet")
        return f"QQBot {token}"

    async def close(self) -> None:
        if self._owns_session and self._session is not None and not self._session.closed:
            await self._session.close()

    async def __aenter__(self) -> "TokenManager":
        return self

    async def __aexit__(self, *exc_info) -> None:
        await self.close()
