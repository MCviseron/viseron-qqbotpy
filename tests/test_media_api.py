"""Offline contract tests for the Markdown media asset APIs.

Platform documentation: 变更记录 20261021「新增素材管理」,
https://bot.q.qq.com/wiki/develop/api-v2/server-inter/message/material-management.html

The network is never touched: a recording stand-in for HTTPClient captures the
built Route and payload, and the presigned PUT is replaced by a stub.
"""

from __future__ import annotations

import hashlib
import os

import pytest

from viseron_qqbotpy.api import BotAPI


class RecordingHTTP:
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


def _write_image(tmp_path, name="kline.png", payload=b"\x89PNG\r\n\x1a\nfake"):
    path = tmp_path / name
    path.write_bytes(payload)
    return str(path), payload


@pytest.mark.asyncio
async def test_prepare_media_image():
    http = RecordingHTTP()
    api = BotAPI(http)

    await api.prepare_media_image(
        file_name="kline.png",
        file_size=40156,
        content_type="image/png",
        md5="e10adc3949ba59abbe56e057f20f883e",
        sha1="d5c5d9b5b3d5d9e0a1b2c3d4e5f60718293a4b5c",
    )

    call = http.last
    assert call["method"] == "POST"
    assert call["path"] == "/v2/media-images/prepare"
    assert call["url"] == "https://api.bot.qq.com/v2/media-images/prepare"
    assert call["kwargs"]["json"] == {
        "file_name": "kline.png",
        "file_size": 40156,
        "content_type": "image/png",
        "md5": "e10adc3949ba59abbe56e057f20f883e",
        "sha1": "d5c5d9b5b3d5d9e0a1b2c3d4e5f60718293a4b5c",
    }


@pytest.mark.asyncio
async def test_complete_media_image():
    http = RecordingHTTP()
    api = BotAPI(http)

    await api.complete_media_image(upload_id="upload_1_2", md5="abc123")

    call = http.last
    assert call["method"] == "POST"
    assert call["path"] == "/v2/media-images/complete"
    assert call["kwargs"]["json"] == {"upload_id": "upload_1_2", "md5": "abc123"}


@pytest.mark.asyncio
async def test_get_media_images():
    http = RecordingHTTP()
    api = BotAPI(http)

    await api.get_media_images(cursor="next-token")

    call = http.last
    assert call["method"] == "GET"
    assert call["path"] == "/v2/media-images"
    assert call["kwargs"]["params"] == {"cursor": "next-token"}


@pytest.mark.asyncio
async def test_get_media_images_first_page():
    http = RecordingHTTP()
    api = BotAPI(http)

    await api.get_media_images()

    assert http.last["kwargs"]["params"] == {}


@pytest.mark.asyncio
async def test_delete_media_image():
    http = RecordingHTTP()
    api = BotAPI(http)

    await api.delete_media_image("102083127_3f9a1c4b7d2e8065")

    call = http.last
    assert call["method"] == "DELETE"
    assert call["path"] == "/v2/media-images/{image_id}/delete"
    assert call["path_params"] == {"image_id": "102083127_3f9a1c4b7d2e8065"}
    assert call["url"] == (
        "https://api.bot.qq.com/v2/media-images/102083127_3f9a1c4b7d2e8065/delete"
    )


@pytest.mark.parametrize(
    "name,expected",
    [
        ("a.png", "image/png"),
        ("a.PNG", "image/png"),
        ("a.jpg", "image/jpeg"),
        ("a.jpeg", "image/jpeg"),
        ("a.gif", "image/gif"),
        ("a.webp", "image/webp"),
    ],
)
def test_guess_image_content_type(name, expected):
    assert BotAPI.guess_image_content_type(name) == expected


def test_guess_image_content_type_rejects_unknown():
    with pytest.raises(ValueError):
        BotAPI.guess_image_content_type("chart.bmp")


@pytest.mark.asyncio
async def test_upload_markdown_image_end_to_end(tmp_path, monkeypatch):
    path, payload = _write_image(tmp_path)
    http = RecordingHTTP(response={"upload_id": "u1", "presigned_url": "https://cos/x"})
    api = BotAPI(http)

    put_calls = []

    async def fake_put(presigned_url, file_path, content_type):
        put_calls.append((presigned_url, os.path.basename(file_path), content_type))
        return hashlib.md5(payload).hexdigest()

    monkeypatch.setattr(api, "put_presigned_image", fake_put)

    await api.upload_markdown_image(path)

    # 1st call: prepare
    prepare = http.calls[0]
    assert prepare["path"] == "/v2/media-images/prepare"
    body = prepare["kwargs"]["json"]
    assert body["file_name"] == "kline.png"
    assert body["file_size"] == len(payload)
    assert body["content_type"] == "image/png"
    assert body["md5"] == hashlib.md5(payload).hexdigest()
    assert body["sha1"] == hashlib.sha1(payload).hexdigest()

    # 2nd call: presigned PUT with the matching content type
    assert put_calls == [("https://cos/x", "kline.png", "image/png")]

    # 3rd call: complete, md5 taken from the ETag of the PUT
    complete = http.calls[1]
    assert complete["path"] == "/v2/media-images/complete"
    assert complete["kwargs"]["json"] == {
        "upload_id": "u1",
        "md5": hashlib.md5(payload).hexdigest(),
    }


@pytest.mark.asyncio
async def test_upload_markdown_image_falls_back_to_computed_md5(tmp_path, monkeypatch):
    path, payload = _write_image(tmp_path, "chart.jpg", b"\xff\xd8\xff\xe0jpeg")
    http = RecordingHTTP(response={"upload_id": "u2", "presigned_url": "https://cos/y"})
    api = BotAPI(http)

    async def fake_put(presigned_url, file_path, content_type):
        return None  # storage did not return an ETag

    monkeypatch.setattr(api, "put_presigned_image", fake_put)

    await api.upload_markdown_image(path)

    assert http.calls[0]["kwargs"]["json"]["content_type"] == "image/jpeg"
    assert http.calls[1]["kwargs"]["json"]["md5"] == hashlib.md5(payload).hexdigest()
