"""Live access-token integration test.

Requires APPID/APPSECRET in the environment or the project .env file.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

import pytest

from viseron_qqbotpy.token import TokenManager


def _load_env() -> dict:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    values = {}
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values


@pytest.mark.asyncio
async def test_live_access_token():
    env = _load_env()
    appid = os.getenv("APPID", env.get("APPID", ""))
    secret = os.getenv("APPSECRET", env.get("APPSECRET", ""))
    if not appid or not secret:
        pytest.skip("APPID/APPSECRET not configured")

    async with TokenManager(appid, secret) as manager:
        token = await manager.get_access_token()
        assert token
        assert manager.access_token == token
