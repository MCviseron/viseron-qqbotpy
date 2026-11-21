"""Offline contract tests for the message token / card changes.

Platform changelog:
- 20261028  新增图文卡片消息 (msg_type=8, ``card`` field, type "tuwen")
- 20261026  群聊文本 / markdown 消息支持 <qqbot-at-everyone /> @全部成员
- 文本交互页  <qqbot-at-user id="" />、<qqbot-cmd-enter />、<qqbot-cmd-input />

No network is touched: a recording stand-in for HTTPClient captures the built
request.
"""

from __future__ import annotations

import pytest

from viseron_qqbotpy import AT_EVERYONE, at_user, cmd_enter, cmd_input
from viseron_qqbotpy.api import BotAPI


class RecordingHTTP:
    def __init__(self) -> None:
        self.calls = []

    async def request(self, route, **kwargs):
        self.calls.append({"method": route.method, "path": route.path, "kwargs": kwargs})
        return {"id": "msg-1"}

    @property
    def last(self):
        assert self.calls, "no request was made"
        return self.calls[-1]


GROUP = "B2C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5"
OPENID = "C3D4E5F6A1B2C3D4E5F6A1B2C3D4E5F6"

CARD = {
    "type": "tuwen",
    "content": {
        "title": "iPhone 17 Pro 正式发布",
        "description": "全新 A20 芯片 / 钛金属机身 / 支持卫星通信",
        "url": "https://news.qq.com/rain/a/20261014A05XYZ00",
        "pic_url": "https://inews.gtimg.com/newsapp_bt/0/xxx/1000.jpg",
    },
}


def test_at_everyone_token_value():
    # The platform token is matched literally; a typo silently sends plain text.
    assert AT_EVERYONE == "<qqbot-at-everyone />"


@pytest.mark.asyncio
async def test_group_card_message():
    http = RecordingHTTP()
    api = BotAPI(http)

    await api.post_group_message(
        group_openid=GROUP,
        msg_type=8,
        card=CARD,
        msg_id="ROBOT1.0_ref",
        msg_seq=2,
    )

    call = http.last
    assert call["method"] == "POST"
    assert call["path"] == "/v2/groups/{group_openid}/messages"
    body = call["kwargs"]["json"]
    assert body["msg_type"] == 8
    assert body["card"] == CARD
    assert body["msg_seq"] == 2


@pytest.mark.asyncio
async def test_c2c_card_message():
    http = RecordingHTTP()
    api = BotAPI(http)

    await api.post_c2c_message(openid=OPENID, msg_type=8, card=CARD)

    body = http.last["kwargs"]["json"]
    assert http.last["path"] == "/v2/users/{openid}/messages"
    assert body["msg_type"] == 8
    assert body["card"] == CARD


@pytest.mark.asyncio
async def test_card_is_omitted_when_not_used():
    http = RecordingHTTP()
    api = BotAPI(http)

    await api.post_group_message(group_openid=GROUP, content="hello")

    # _clean() drops the None so a text message never carries an empty card.
    assert "card" not in http.last["kwargs"]["json"]


@pytest.mark.asyncio
async def test_at_everyone_in_text_content():
    http = RecordingHTTP()
    api = BotAPI(http)

    await api.post_group_message(group_openid=GROUP, content=f"{AT_EVERYONE} 开会了")

    body = http.last["kwargs"]["json"]
    assert body["msg_type"] == 0
    assert body["content"] == "<qqbot-at-everyone /> 开会了"


@pytest.mark.asyncio
async def test_at_everyone_in_markdown_content():
    http = RecordingHTTP()
    api = BotAPI(http)

    await api.post_group_message(
        group_openid=GROUP,
        msg_type=2,
        markdown={"content": f"# 通知\n{AT_EVERYONE} 今天 20:00 维护"},
    )

    body = http.last["kwargs"]["json"]
    assert body["msg_type"] == 2
    assert AT_EVERYONE in body["markdown"]["content"]


# --------------------------------------------------------------------------- #
# @用户 (qqbot-at-user) —— 平台文档「文本交互」
# --------------------------------------------------------------------------- #
def test_at_user_token_shape():
    assert at_user("0123456789ABCDEF") == '<qqbot-at-user id="0123456789ABCDEF" />'


@pytest.mark.parametrize("bad", ["", 'a"b', "a<b", "a b", "a\nb"])
def test_at_user_rejects_bad_ids(bad):
    with pytest.raises(ValueError):
        at_user(bad)


@pytest.mark.asyncio
async def test_at_user_inside_group_markdown():
    http = RecordingHTTP()
    api = BotAPI(http)

    await api.post_group_message(
        group_openid=GROUP,
        msg_type=2,
        markdown={"content": f"{at_user('MEMBER_OPENID')} 你的订单已发货"},
    )

    body = http.last["kwargs"]["json"]
    assert body["msg_type"] == 2
    assert '<qqbot-at-user id="MEMBER_OPENID" />' in body["markdown"]["content"]


@pytest.mark.asyncio
async def test_at_user_inside_channel_text():
    http = RecordingHTTP()
    api = BotAPI(http)

    await api.post_message(
        channel_id="CHANNEL",
        content=f"{at_user('USER_OPENID')} 看一下这条",
    )

    body = http.last["kwargs"]["json"]
    assert '<qqbot-at-user id="USER_OPENID" />' in body["content"]


# --------------------------------------------------------------------------- #
# 指令嵌字（<qqbot-cmd-enter /> / <qqbot-cmd-input />）—— 平台文档「文本交互」
# --------------------------------------------------------------------------- #
def test_cmd_enter_urlencodes_text():
    assert cmd_enter("/签到") == '<qqbot-cmd-enter text="%2F%E7%AD%BE%E5%88%B0" />'


def test_cmd_input_defaults_show_to_text():
    token = cmd_input("每日签到")
    assert token.startswith('<qqbot-cmd-input text="%E6%AF%8F%E6%97%A5%E7%AD%BE%E5%88%B0"')
    assert 'show="%E6%AF%8F%E6%97%A5%E7%AD%BE%E5%88%B0"' in token
    assert 'reference="false"' in token


def test_cmd_input_with_show_and_reference():
    token = cmd_input("a b", show="点我", reference=True)
    assert 'text="a%20b"' in token
    assert 'show="%E7%82%B9%E6%88%91"' in token
    assert 'reference="true"' in token


@pytest.mark.parametrize("text", ["", "x" * 101])
def test_cmd_tokens_reject_bad_text(text):
    with pytest.raises(ValueError):
        cmd_enter(text)
    with pytest.raises(ValueError):
        cmd_input(text)
