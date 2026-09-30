"""Offline contract tests for the group member management APIs.

These tests never touch the network: a recording stand-in for HTTPClient
captures the Route and the keyword arguments each BotAPI method builds, so a
wrong path, verb or field name fails here instead of in production.

Covered platform documentation changes:

- 2026-09-03  群成员管理：获取群成员列表 / 获取群成员信息 / 群成员批量移除 /
              群黑名单查询 / 群黑名单操作
- 2026-09-16  生成分享链接 /v2/generate_url_link 字段修正（url_link ->
              callback_data）
"""

from __future__ import annotations

import pytest

from viseron_qqbotpy.api import BotAPI


class RecordingHTTP:
    """Minimal HTTPClient double that records what BotAPI asks for."""

    def __init__(self, response=None) -> None:
        self.calls = []
        self._response = {"ok": True} if response is None else response

    async def request(self, route, **kwargs):
        self.calls.append(
            {
                "method": route.method,
                "path": route.path,
                "path_params": dict(route.path_params),
                "url": route.url("https://api.bot.qq.com"),
                "kwargs": kwargs,
            }
        )
        return self._response

    @property
    def last(self):
        assert self.calls, "no request was made"
        return self.calls[-1]


GROUP = "30584554AA2BF4E72BD3B8F27A70339D"
MEMBER = "7A3B9C1D5E2F4A6B8C0D1E3F5A7B9C2D"


@pytest.mark.asyncio
async def test_get_group_members():
    http = RecordingHTTP()
    api = BotAPI(http)

    await api.get_group_members(GROUP, cursor="bG1fNmIx")

    call = http.last
    assert call["method"] == "GET"
    assert call["path"] == "/v2/groups/{group_openid}/members"
    assert call["url"] == f"https://api.bot.qq.com/v2/groups/{GROUP}/members"
    assert call["path_params"] == {"group_openid": GROUP}
    assert call["kwargs"]["params"] == {"cursor": "bG1fNmIx"}


@pytest.mark.asyncio
async def test_get_group_members_without_cursor():
    http = RecordingHTTP()
    api = BotAPI(http)

    await api.get_group_members(GROUP)

    # _clean drops the None cursor, so the first page is requested bare.
    assert http.last["kwargs"]["params"] == {}


@pytest.mark.asyncio
async def test_get_group_member():
    http = RecordingHTTP()
    api = BotAPI(http)

    await api.get_group_member(GROUP, MEMBER)

    call = http.last
    assert call["method"] == "GET"
    assert call["path"] == "/v2/groups/{group_openid}/members/{member_openid}"
    assert call["url"] == f"https://api.bot.qq.com/v2/groups/{GROUP}/members/{MEMBER}"
    assert call["path_params"] == {"group_openid": GROUP, "member_openid": MEMBER}


@pytest.mark.asyncio
async def test_batch_remove_group_members_defaults():
    http = RecordingHTTP()
    api = BotAPI(http)

    await api.batch_remove_group_members(GROUP, [MEMBER])

    call = http.last
    assert call["method"] == "POST"
    assert call["path"] == "/v2/groups/{group_openid}/batch_remove_members"
    assert call["kwargs"]["json"] == {
        "member_openids": [MEMBER],
        "add_to_member_blacklist": False,
    }


@pytest.mark.asyncio
async def test_batch_remove_group_members_with_blacklist():
    http = RecordingHTTP()
    api = BotAPI(http)

    await api.batch_remove_group_members(GROUP, [MEMBER, "OTHER"], add_to_member_blacklist=True)

    assert http.last["kwargs"]["json"] == {
        "member_openids": [MEMBER, "OTHER"],
        "add_to_member_blacklist": True,
    }


@pytest.mark.asyncio
async def test_get_group_member_blacklist():
    http = RecordingHTTP()
    api = BotAPI(http)

    await api.get_group_member_blacklist(GROUP, cursor="next", limit=50)

    call = http.last
    assert call["method"] == "GET"
    assert call["path"] == "/v2/groups/{group_openid}/member_blacklist"
    assert call["kwargs"]["params"] == {"cursor": "next", "limit": 50}


@pytest.mark.asyncio
async def test_get_group_member_blacklist_default_limit():
    http = RecordingHTTP()
    api = BotAPI(http)

    await api.get_group_member_blacklist(GROUP)

    assert http.last["kwargs"]["params"] == {"limit": 20}


@pytest.mark.asyncio
async def test_update_group_member_blacklist():
    http = RecordingHTTP()
    api = BotAPI(http)

    await api.update_group_member_blacklist(GROUP, op="add", member_openids=[MEMBER])

    call = http.last
    assert call["method"] == "POST"
    assert call["path"] == "/v2/groups/{group_openid}/member_blacklist"
    assert call["kwargs"]["json"] == {"op": "add", "member_openids": [MEMBER]}


@pytest.mark.asyncio
async def test_create_url_link_uses_callback_data():
    http = RecordingHTTP()
    api = BotAPI(http)

    await api.create_url_link("custom_data_123")

    call = http.last
    assert call["method"] == "POST"
    assert call["path"] == "/v2/generate_url_link"
    assert call["kwargs"]["json"] == {"callback_data": "custom_data_123"}
    assert "url_link" not in call["kwargs"]["json"]


@pytest.mark.asyncio
async def test_create_url_link_accepts_deprecated_alias():
    http = RecordingHTTP()
    api = BotAPI(http)

    await api.create_url_link(url_link="legacy_value")

    assert http.last["kwargs"]["json"] == {"callback_data": "legacy_value"}


@pytest.mark.asyncio
async def test_create_url_link_without_payload():
    http = RecordingHTTP()
    api = BotAPI(http)

    await api.create_url_link()

    assert http.last["kwargs"]["json"] == {}
