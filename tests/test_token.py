"""Tests for the seamless token refresh logic."""

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from viseron_qqbotpy.token import AccessToken, TokenManager


def test_access_token_remaining():
    token = AccessToken("abc", 7200)
    assert token.remaining > 0
    assert token.expired is False


@pytest.mark.asyncio
async def test_get_access_token_fetches_once():
    manager = TokenManager("appid", "secret")
    response = MagicMock()
    response.__aenter__ = AsyncMock(return_value=response)
    response.__aexit__ = AsyncMock(return_value=False)
    response.json = AsyncMock(return_value={"access_token": "tok", "expires_in": "7200"})
    session = MagicMock()
    session.post = MagicMock(return_value=response)

    with patch.object(manager, "_get_session", AsyncMock(return_value=session)):
        token = await manager.get_access_token()
        assert token == "tok"
        again = await manager.get_access_token()
        assert again == "tok"
        assert session.post.call_count == 1


@pytest.mark.asyncio
async def test_refresh_in_final_window():
    manager = TokenManager("appid", "secret")
    # 30 seconds left -> inside the 60 second refresh window.
    manager._token = AccessToken("old", 30)

    response = MagicMock()
    response.__aenter__ = AsyncMock(return_value=response)
    response.__aexit__ = AsyncMock(return_value=False)
    response.json = AsyncMock(return_value={"access_token": "new", "expires_in": "7200"})
    session = MagicMock()
    session.post = MagicMock(return_value=response)

    with patch.object(manager, "_get_session", AsyncMock(return_value=session)):
        token = await manager.get_access_token()

    assert token == "new"
    assert session.post.call_count == 1


@pytest.mark.asyncio
async def test_refresh_failure_keeps_old_token_in_window():
    manager = TokenManager("appid", "secret")
    manager._token = AccessToken("old", 30)

    response = MagicMock()
    response.__aenter__ = AsyncMock(side_effect=RuntimeError("network down"))
    session = MagicMock()
    session.post = MagicMock(return_value=response)

    with patch.object(manager, "_get_session", AsyncMock(return_value=session)):
        token = await manager.get_access_token()

    # The old token is still valid for another ~30 seconds.
    assert token == "old"


@pytest.mark.asyncio
async def test_concurrent_get_refreshes_only_once():
    import asyncio

    manager = TokenManager("appid", "secret")

    async def enter_response(self):
        await asyncio.sleep(0.05)
        return response

    response = MagicMock()
    response.__aenter__ = enter_response
    response.__aexit__ = AsyncMock(return_value=False)
    response.json = AsyncMock(return_value={"access_token": "tok", "expires_in": "7200"})
    session = MagicMock()
    session.post = MagicMock(return_value=response)

    with patch.object(manager, "_get_session", AsyncMock(return_value=session)):
        tokens = await asyncio.gather(*(manager.get_access_token() for _ in range(5)))

    assert tokens == ["tok"] * 5
    assert session.post.call_count == 1
