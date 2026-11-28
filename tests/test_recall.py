"""Offline tests for the 2026-11-27 group-recall error codes.

The platform now distinguishes "recalled by another member" (40064009) from
"already recalled by this bot" (40064010).  Both mean the message is gone, so
RECALL_ALREADY_GONE groups them for callers that treat it as success.
"""

from __future__ import annotations

import pytest

from viseron_qqbotpy import RECALL_ALREADY_GONE
from viseron_qqbotpy.api import BotAPI
from viseron_qqbotpy.errors import APIError


class RecordingHTTP:
    def __init__(self) -> None:
        self.calls = []

    async def request(self, route, **kwargs):
        self.calls.append({"method": route.method, "path": route.path, "kwargs": kwargs})
        return None

    @property
    def last(self):
        assert self.calls, "no request was made"
        return self.calls[-1]


def test_recall_already_gone_codes():
    assert RECALL_ALREADY_GONE == frozenset({40064009, 40064010})
    # 40064004 (timeout) must NOT be treated as "already gone".
    assert 40064004 not in RECALL_ALREADY_GONE


@pytest.mark.asyncio
async def test_recall_group_message_builds_delete_route():
    http = RecordingHTTP()
    api = BotAPI(http)

    await api.recall_group_message("GROUP", "MSG1")

    call = http.last
    assert call["method"] == "DELETE"
    assert call["path"] == "/v2/groups/{group_openid}/messages/{message_id}"
    assert call["kwargs"].get("json") is None


def test_api_error_code_is_matchable():
    exc = APIError(400, "操作失败，消息已被其他成员撤回", code=40064009)
    assert exc.code in RECALL_ALREADY_GONE
