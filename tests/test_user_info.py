"""Offline tests for the 2026-11-16 / 2026-11-17 platform changes.

Covered:
- 20261116: GET /v2/users/{user_openid}/info (get_user_info)
- 20261116: group/c2c events gained member_nickname and union_group_openid
- 20261117: passive-reply window/quota changes are documentation-only, no code

No network: a recording stand-in for HTTPClient captures the built request.
"""

from __future__ import annotations

import pytest

from viseron_qqbotpy.api import BotAPI
from viseron_qqbotpy.models import GroupManageEvent, GroupMemberEvent, GroupMessage, User


class RecordingHTTP:
    def __init__(self) -> None:
        self.calls = []

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
        return {"username": "笑😊心❤️", "avatar": "https://x/y.png", "allow_proactive_msg": False}

    @property
    def last(self):
        assert self.calls, "no request was made"
        return self.calls[-1]


OPENID = "CADF012424CB537DDBC9950A90732538"


@pytest.mark.asyncio
async def test_get_user_info():
    http = RecordingHTTP()
    api = BotAPI(http)

    await api.get_user_info(OPENID)

    call = http.last
    assert call["method"] == "GET"
    assert call["path"] == "/v2/users/{openid}/info"
    assert call["url"] == f"https://api.bot.qq.com/v2/users/{OPENID}/info"
    assert call["path_params"] == {"openid": OPENID}


def test_user_parses_member_nickname():
    user = User.from_payload(
        {
            "member_openid": "M1",
            "username": "小明",
            "avatar": "https://a/b.png",
            "member_nickname": "群里的昵称",
            "union_openid": "U1",
        }
    )
    assert user.member_nickname == "群里的昵称"
    assert user.username == "小明"
    assert user.avatar == "https://a/b.png"


def test_group_message_parses_new_fields():
    msg = GroupMessage.from_payload(
        None,
        "evt-1",
        {
            "id": "MSG1",
            "group_openid": "G1",
            "union_group_openid": "UG1",
            "content": "hi",
            "author": {"member_openid": "M1", "username": "小明", "member_nickname": "群昵称"},
            "mentions": [],
        },
    )
    assert msg.union_group_openid == "UG1"
    # member_nickname is hoisted from author, and also read from top level if present.
    assert msg.member_nickname == "群昵称"


def test_group_message_prefers_top_level_member_nickname():
    msg = GroupMessage.from_payload(
        None,
        None,
        {"author": {"member_nickname": "来自author"}, "member_nickname": "来自顶层"},
    )
    assert msg.member_nickname == "来自顶层"


def test_group_member_event_parses_union_group_openid():
    event = GroupMemberEvent.from_payload(
        None,
        None,
        {"group_openid": "G1", "union_group_openid": "UG1", "member_openid": "M1", "timestamp": 1},
    )
    assert event.union_group_openid == "UG1"


def test_group_manage_event_parses_union_group_openid():
    event = GroupManageEvent.from_payload(
        None,
        None,
        {"group_openid": "G1", "union_group_openid": "UG1", "op_member_openid": "M2"},
    )
    assert event.union_group_openid == "UG1"
