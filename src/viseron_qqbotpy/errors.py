"""Exception hierarchy for the QQ bot SDK.

The platform now returns a structured JSON error body with err_code,
message and trace_id.  All HTTP errors are therefore normalised into
APIError, while the older status-code based exceptions are kept as
subclasses for backwards compatibility.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class ViseronError(RuntimeError):
    """Base class for every error raised by this SDK."""


class TokenError(ViseronError):
    """Raised when an access token cannot be obtained or refreshed."""


class APIError(ViseronError):
    """Raised when the OpenAPI endpoint returns an unsuccessful response."""

    def __init__(
        self,
        status: int,
        message: str,
        *,
        code: Optional[int] = None,
        trace_id: Optional[str] = None,
        data: Any = None,
        url: Optional[str] = None,
    ) -> None:
        self.status = status
        self.code = code
        self.trace_id = trace_id
        self.data = data
        self.url = url
        super().__init__(message)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} status={self.status} code={self.code} "
            f"trace_id={self.trace_id!r} message={str(self)!r}>"
        )

    @classmethod
    def from_response(cls, status: int, payload: Any, url: Optional[str] = None) -> "APIError":
        code: Optional[int] = None
        message: str = f"request failed with HTTP {status}"
        trace_id: Optional[str] = None
        data: Any = payload

        if isinstance(payload, dict):
            code = payload.get("err_code") or payload.get("code")
            trace_id = payload.get("trace_id")
            message = payload.get("message") or payload.get("msg") or message
            data = payload.get("data")
            if code is None and isinstance(payload.get("code"), int):
                code = payload["code"]

        error_cls = _STATUS_ERRORS.get(status, cls)
        return error_cls(status, str(message), code=code, trace_id=trace_id, data=data, url=url)


class AuthenticationFailedError(APIError):
    """HTTP 401 - the access token is missing, invalid, or expired."""


class ForbiddenError(APIError):
    """HTTP 403 - the bot has no permission for the requested resource."""


class NotFoundError(APIError):
    """HTTP 404 - the API or resource was not found."""


class MethodNotAllowedError(APIError):
    """HTTP 405 - the HTTP method is not allowed for this endpoint."""


class RateLimitError(APIError):
    """HTTP 429 - the request was rate limited."""


class ServerError(APIError):
    """HTTP 5xx - the platform returned a server error."""


class WebSocketError(ViseronError):
    """Raised for gateway protocol/connection errors."""

    def __init__(self, message: str, *, close_code: Optional[int] = None) -> None:
        self.close_code = close_code
        super().__init__(message)


_STATUS_ERRORS: Dict[int, type] = {
    401: AuthenticationFailedError,
    403: ForbiddenError,
    404: NotFoundError,
    405: MethodNotAllowedError,
    429: RateLimitError,
    500: ServerError,
    502: ServerError,
    503: ServerError,
    504: ServerError,
}
