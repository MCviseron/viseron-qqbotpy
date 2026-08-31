"""High-level asynchronous API client for the QQ bot platform.

Every method returns the decoded JSON body (or None for 204 responses).  No
method invents default values; optional fields are omitted when they are
None.
"""

from __future__ import annotations

import hashlib
import json
import os
from io import BufferedReader
from typing import Any, BinaryIO, Dict, List, Optional, Union

import aiohttp
from aiohttp import FormData

from .http import HTTPClient, Route
from .logging import get_logger

__all__ = ["BotAPI"]

_log = get_logger(__name__)

JsonDict = Dict[str, Any]


def _clean(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Drop None values so optional fields are never sent as JSON null."""
    return {key: value for key, value in payload.items() if value is not None}


def _encode(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return value


class BotAPI:
    """A namespace of OpenAPI methods.

    Direct use::

        api = BotAPI(http_client)
        await api.get_guild("guild_id")
    """

    def __init__(self, http: HTTPClient) -> None:
        self._http = http

    # ------------------------------------------------------------------ #
    # request helpers
    # ------------------------------------------------------------------ #
    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        form: Optional[FormData] = None,
        **path_params: Any,
    ) -> Any:
        route = Route(method, path, **path_params)
        kwargs: Dict[str, Any] = {}
        if params:
            kwargs["params"] = _clean(params)
        if json is not None:
            kwargs["json"] = _clean(json)
        if form is not None:
            kwargs["data"] = form
        return await self._http.request(route, **kwargs)

    async def _get(self, path: str, *, params: Optional[Dict[str, Any]] = None, **path_params: Any) -> Any:
        return await self._request("GET", path, params=params, **path_params)

    async def _post(self, path: str, *, json: Optional[Dict[str, Any]] = None, form: Optional[FormData] = None, **path_params: Any) -> Any:
        return await self._request("POST", path, json=json, form=form, **path_params)

    async def _put(self, path: str, *, json: Optional[Dict[str, Any]] = None, **path_params: Any) -> Any:
        return await self._request("PUT", path, json=json, **path_params)

    async def _patch(self, path: str, *, json: Optional[Dict[str, Any]] = None, **path_params: Any) -> Any:
        return await self._request("PATCH", path, json=json, **path_params)

    async def _delete(self, path: str, *, json: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None, **path_params: Any) -> Any:
        return await self._request("DELETE", path, json=json, params=params, **path_params)

    @staticmethod
    def _read_file(file_image: Union[bytes, bytearray, memoryview, BinaryIO, str]) -> bytes:
        if isinstance(file_image, (bytes, bytearray, memoryview)):
            return bytes(file_image)
        if isinstance(file_image, BufferedReader):
            return file_image.read()
        if hasattr(file_image, "read"):
            return file_image.read()
        if isinstance(file_image, str):
            with open(file_image, "rb") as handle:
                return handle.read()
        raise TypeError(f"unsupported file_image type: {type(file_image)!r}")

    @staticmethod
    def _message_form(file_image: Union[bytes, bytearray, memoryview, BinaryIO, str], fields: Dict[str, Any]) -> FormData:
        form = FormData()
        for key, value in fields.items():
            if key == "file_image":
                continue
            if value is None:
                continue
            form.add_field(key, _encode(value))
        form.add_field("file_image", BotAPI._read_file(file_image), filename="image.png")
        return form

    # ------------------------------------------------------------------ #
    # guilds / channels
    # ------------------------------------------------------------------ #
    async def get_guild(self, guild_id: str) -> Any:
        """Get a guild by id."""
        return await self._get("/guilds/{guild_id}", guild_id=guild_id)

    async def get_channels(self, guild_id: str) -> Any:
        """Get the channel list of a guild."""
        return await self._get("/guilds/{guild_id}/channels", guild_id=guild_id)

    async def get_channel(self, channel_id: str) -> Any:
        """Get a channel by id."""
        return await self._get("/channels/{channel_id}", channel_id=channel_id)

    async def create_channel(
        self,
        guild_id: str,
        name: str,
        type: int,
        sub_type: int,
        **fields: Any,
    ) -> Any:
        """Create a channel in a guild."""
        payload = {"name": name, "type": int(type), "sub_type": int(sub_type), **fields}
        return await self._post("/guilds/{guild_id}/channels", json=payload, guild_id=guild_id)

    async def update_channel(self, channel_id: str, **fields: Any) -> Any:
        """Update a channel."""
        return await self._patch("/channels/{channel_id}", json=fields, channel_id=channel_id)

    async def delete_channel(self, channel_id: str) -> Any:
        """Delete a channel."""
        return await self._delete("/channels/{channel_id}", channel_id=channel_id)

    async def get_online_nums(self, channel_id: str) -> Any:
        """Get the online member count of an audio/live channel."""
        return await self._get("/channels/{channel_id}/online_nums", channel_id=channel_id)

    async def get_channel_user_permissions(self, channel_id: str, user_id: str) -> Any:
        return await self._get(
            "/channels/{channel_id}/members/{user_id}/permissions",
            channel_id=channel_id,
            user_id=user_id,
        )

    async def update_channel_user_permissions(
        self, channel_id: str, user_id: str, add: Any = None, remove: Any = None
    ) -> Any:
        payload = {
            "add": str(getattr(add, "value", add)) if add is not None else None,
            "remove": str(getattr(remove, "value", remove)) if remove is not None else None,
        }
        return await self._put(
            "/channels/{channel_id}/members/{user_id}/permissions",
            json=payload,
            channel_id=channel_id,
            user_id=user_id,
        )

    async def get_channel_role_permissions(self, channel_id: str, role_id: str) -> Any:
        return await self._get(
            "/channels/{channel_id}/roles/{role_id}/permissions",
            channel_id=channel_id,
            role_id=role_id,
        )

    async def update_channel_role_permissions(
        self, channel_id: str, role_id: str, add: Any = None, remove: Any = None
    ) -> Any:
        payload = {
            "add": str(getattr(add, "value", add)) if add is not None else None,
            "remove": str(getattr(remove, "value", remove)) if remove is not None else None,
        }
        return await self._put(
            "/channels/{channel_id}/roles/{role_id}/permissions",
            json=payload,
            channel_id=channel_id,
            role_id=role_id,
        )

    # ------------------------------------------------------------------ #
    # roles / members
    # ------------------------------------------------------------------ #
    async def get_guild_roles(self, guild_id: str) -> Any:
        return await self._get("/guilds/{guild_id}/roles", guild_id=guild_id)

    async def create_guild_role(self, guild_id: str, **fields: Any) -> Any:
        return await self._post("/guilds/{guild_id}/roles", json=fields, guild_id=guild_id)

    async def update_guild_role(self, guild_id: str, role_id: str, **fields: Any) -> Any:
        return await self._patch("/guilds/{guild_id}/roles/{role_id}", json=fields, guild_id=guild_id, role_id=role_id)

    async def delete_guild_role(self, guild_id: str, role_id: str) -> Any:
        return await self._delete("/guilds/{guild_id}/roles/{role_id}", guild_id=guild_id, role_id=role_id)

    async def create_guild_role_member(
        self, guild_id: str, role_id: str, user_id: str, channel_id: Optional[str] = None
    ) -> Any:
        payload = {"channel": {"id": channel_id}} if channel_id else None
        return await self._put(
            "/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
            json=payload,
            guild_id=guild_id,
            role_id=role_id,
            user_id=user_id,
        )

    async def delete_guild_role_member(
        self, guild_id: str, role_id: str, user_id: str, channel_id: Optional[str] = None
    ) -> Any:
        payload = {"channel": {"id": channel_id}} if channel_id else None
        return await self._delete(
            "/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
            json=payload,
            guild_id=guild_id,
            role_id=role_id,
            user_id=user_id,
        )

    async def get_guild_member(self, guild_id: str, user_id: str) -> Any:
        return await self._get("/guilds/{guild_id}/members/{user_id}", guild_id=guild_id, user_id=user_id)

    async def get_guild_members(self, guild_id: str, after: str = "0", limit: int = 1) -> Any:
        return await self._get(
            "/guilds/{guild_id}/members",
            params={"after": after, "limit": limit},
            guild_id=guild_id,
        )

    async def delete_guild_member(
        self,
        guild_id: str,
        user_id: str,
        add_blacklist: bool = False,
        delete_history_msg_days: int = 0,
    ) -> Any:
        if delete_history_msg_days not in (0, 3, 7, 15, 30, -1):
            delete_history_msg_days = 0
        payload = {"add_blacklist": add_blacklist, "delete_history_msg_days": delete_history_msg_days}
        return await self._delete(
            "/guilds/{guild_id}/members/{user_id}",
            json=payload,
            guild_id=guild_id,
            user_id=user_id,
        )

    async def get_guild_role_members(self, guild_id: str, role_id: str, start_index: str = "0", limit: int = 1) -> Any:
        return await self._get(
            "/guilds/{guild_id}/roles/{role_id}/members",
            params={"start_index": start_index, "limit": limit},
            guild_id=guild_id,
            role_id=role_id,
        )

    async def get_voice_members(self, channel_id: str) -> Any:
        """Get voice channel members (legacy endpoint, may be restricted)."""
        return await self._get("/channels/{channel_id}/voice/members", channel_id=channel_id)

    # ------------------------------------------------------------------ #
    # mute / message frequency settings
    # ------------------------------------------------------------------ #
    async def mute_all(self, guild_id: str, mute_end_timestamp: Optional[str] = None, mute_seconds: Optional[str] = None) -> Any:
        payload = {"mute_end_timestamp": mute_end_timestamp, "mute_seconds": mute_seconds}
        return await self._patch("/guilds/{guild_id}/mute", json=payload, guild_id=guild_id)

    async def cancel_mute_all(self, guild_id: str) -> Any:
        payload = {"mute_end_timestamp": "0", "mute_seconds": "0"}
        return await self._patch("/guilds/{guild_id}/mute", json=payload, guild_id=guild_id)

    async def mute_member(
        self, guild_id: str, user_id: str, mute_end_timestamp: Optional[str] = None, mute_seconds: Optional[str] = None
    ) -> Any:
        payload = {"mute_end_timestamp": mute_end_timestamp, "mute_seconds": mute_seconds}
        return await self._patch(
            "/guilds/{guild_id}/members/{user_id}/mute",
            json=payload,
            guild_id=guild_id,
            user_id=user_id,
        )

    async def mute_multi_member(
        self,
        guild_id: str,
        user_ids: List[str],
        mute_end_timestamp: Optional[str] = None,
        mute_seconds: Optional[str] = None,
    ) -> Any:
        payload = {
            "mute_end_timestamp": mute_end_timestamp,
            "mute_seconds": mute_seconds,
            "user_ids": user_ids,
        }
        return await self._patch("/guilds/{guild_id}/mute", json=payload, guild_id=guild_id)

    async def cancel_mute_multi_member(self, guild_id: str, user_ids: List[str]) -> Any:
        payload = {"mute_end_timestamp": "0", "mute_seconds": "0", "user_ids": user_ids}
        return await self._patch("/guilds/{guild_id}/mute", json=payload, guild_id=guild_id)

    async def get_message_setting(self, guild_id: str) -> Any:
        return await self._get("/guilds/{guild_id}/message/setting", guild_id=guild_id)

    # ------------------------------------------------------------------ #
    # channel messages
    # ------------------------------------------------------------------ #
    async def get_message(self, channel_id: str, message_id: str) -> Any:
        return await self._get(
            "/channels/{channel_id}/messages/{message_id}",
            channel_id=channel_id,
            message_id=message_id,
        )

    async def post_message(
        self,
        channel_id: str,
        content: Optional[str] = None,
        embed: Optional[Any] = None,
        ark: Optional[Any] = None,
        message_reference: Optional[Any] = None,
        image: Optional[str] = None,
        file_image: Optional[Union[bytes, bytearray, memoryview, BinaryIO, str]] = None,
        msg_id: Optional[str] = None,
        event_id: Optional[str] = None,
        markdown: Optional[Any] = None,
        keyboard: Optional[Any] = None,
        **fields: Any,
    ) -> Any:
        """Send a message to a guild channel.

        Use either JSON fields (content/embed/ark/image/markdown/keyboard) or
        file_image for a multipart upload.  file_image accepts bytes, a
        file-like object, or a local path.
        """
        payload = {
            "content": content,
            "embed": embed,
            "ark": ark,
            "message_reference": message_reference,
            "image": image,
            "msg_id": msg_id,
            "event_id": event_id,
            "markdown": markdown,
            "keyboard": keyboard,
            **fields,
        }
        if file_image is not None:
            form = self._message_form(file_image, payload)
            return await self._post("/channels/{channel_id}/messages", form=form, channel_id=channel_id)
        return await self._post("/channels/{channel_id}/messages", json=payload, channel_id=channel_id)

    async def recall_message(self, channel_id: str, message_id: str, hidetip: bool = False) -> Any:
        return await self._delete(
            "/channels/{channel_id}/messages/{message_id}",
            params={"hidetip": str(hidetip).lower()},
            channel_id=channel_id,
            message_id=message_id,
        )

    async def patch_guild_message(
        self,
        channel_id: str,
        patch_msg_id: str,
        msg_id: Optional[str] = None,
        event_id: Optional[str] = None,
        markdown: Optional[Any] = None,
        keyboard: Optional[Any] = None,
        **fields: Any,
    ) -> Any:
        """Patch a channel message (legacy/compat endpoint)."""
        payload = {
            "msg_id": msg_id,
            "event_id": event_id,
            "markdown": markdown,
            "keyboard": keyboard,
            **fields,
        }
        return await self._patch(
            "/channels/{channel_id}/messages/{patch_msg_id}",
            json=payload,
            channel_id=channel_id,
            patch_msg_id=patch_msg_id,
        )

    async def create_dms(self, guild_id: str, user_id: str) -> Any:
        """Create a direct message session."""
        payload = {"recipient_id": user_id, "source_guild_id": guild_id}
        return await self._post("/users/@me/dms", json=payload)

    async def post_dms(
        self,
        guild_id: str,
        content: Optional[str] = None,
        embed: Optional[Any] = None,
        ark: Optional[Any] = None,
        message_reference: Optional[Any] = None,
        image: Optional[str] = None,
        file_image: Optional[Union[bytes, bytearray, memoryview, BinaryIO, str]] = None,
        msg_id: Optional[str] = None,
        event_id: Optional[str] = None,
        markdown: Optional[Any] = None,
        keyboard: Optional[Any] = None,
        **fields: Any,
    ) -> Any:
        """Send a direct message."""
        payload = {
            "content": content,
            "embed": embed,
            "ark": ark,
            "message_reference": message_reference,
            "image": image,
            "msg_id": msg_id,
            "event_id": event_id,
            "markdown": markdown,
            "keyboard": keyboard,
            **fields,
        }
        if file_image is not None:
            form = self._message_form(file_image, payload)
            return await self._post("/dms/{guild_id}/messages", form=form, guild_id=guild_id)
        return await self._post("/dms/{guild_id}/messages", json=payload, guild_id=guild_id)

    async def put_reaction(self, channel_id: str, message_id: str, emoji_type: int, emoji_id: str) -> Any:
        return await self._put(
            "/channels/{channel_id}/messages/{message_id}/reactions/{type}/{id}",
            channel_id=channel_id,
            message_id=message_id,
            type=int(emoji_type),
            id=emoji_id,
        )

    async def delete_reaction(self, channel_id: str, message_id: str, emoji_type: int, emoji_id: str) -> Any:
        return await self._delete(
            "/channels/{channel_id}/messages/{message_id}/reactions/{type}/{id}",
            channel_id=channel_id,
            message_id=message_id,
            type=int(emoji_type),
            id=emoji_id,
        )

    async def get_reaction_users(
        self,
        channel_id: str,
        message_id: str,
        emoji_type: int,
        emoji_id: str,
        cookie: Optional[str] = None,
        limit: int = 20,
    ) -> Any:
        params: Dict[str, Any] = {"limit": limit}
        if cookie:
            params["cookie"] = cookie
        return await self._get(
            "/channels/{channel_id}/messages/{message_id}/reactions/{type}/{id}",
            params=params,
            channel_id=channel_id,
            message_id=message_id,
            type=int(emoji_type),
            id=emoji_id,
        )

    async def put_pin(self, channel_id: str, message_id: str) -> Any:
        return await self._put(
            "/channels/{channel_id}/pins/{message_id}",
            json={},
            channel_id=channel_id,
            message_id=message_id,
        )

    async def delete_pin(self, channel_id: str, message_id: str) -> Any:
        return await self._delete(
            "/channels/{channel_id}/pins/{message_id}",
            channel_id=channel_id,
            message_id=message_id,
        )

    async def get_pins(self, channel_id: str) -> Any:
        return await self._get("/channels/{channel_id}/pins", channel_id=channel_id)

    # ------------------------------------------------------------------ #
    # interactions / schedules / forums / audio / announces
    # ------------------------------------------------------------------ #
    async def on_interaction_result(self, interaction_id: str, code: int) -> Any:
        return await self._put("/interactions/{interaction_id}", json={"code": code}, interaction_id=interaction_id)

    async def get_schedules(self, channel_id: str, since: Optional[str] = None) -> Any:
        return await self._get(
            "/channels/{channel_id}/schedules",
            params={"since": since} if since else None,
            channel_id=channel_id,
        )

    async def get_schedule(self, channel_id: str, schedule_id: str) -> Any:
        return await self._get(
            "/channels/{channel_id}/schedules/{schedule_id}",
            channel_id=channel_id,
            schedule_id=schedule_id,
        )

    async def create_schedule(
        self,
        channel_id: str,
        name: str,
        start_timestamp: str,
        end_timestamp: str,
        jump_channel_id: str,
        remind_type: str,
    ) -> Any:
        payload = {
            "schedule": {
                "name": name,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "jump_channel_id": jump_channel_id,
                "remind_type": remind_type,
            }
        }
        return await self._post("/channels/{channel_id}/schedules", json=payload, channel_id=channel_id)

    async def update_schedule(
        self,
        channel_id: str,
        schedule_id: str,
        name: str,
        start_timestamp: str,
        end_timestamp: str,
        jump_channel_id: str,
        remind_type: str,
    ) -> Any:
        payload = {
            "schedule": {
                "name": name,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "jump_channel_id": jump_channel_id,
                "remind_type": remind_type,
            }
        }
        return await self._patch(
            "/channels/{channel_id}/schedules/{schedule_id}",
            json=payload,
            channel_id=channel_id,
            schedule_id=schedule_id,
        )

    async def delete_schedule(self, channel_id: str, schedule_id: str) -> Any:
        return await self._delete(
            "/channels/{channel_id}/schedules/{schedule_id}",
            channel_id=channel_id,
            schedule_id=schedule_id,
        )

    async def get_threads(self, channel_id: str) -> Any:
        return await self._get("/channels/{channel_id}/threads", channel_id=channel_id)

    async def get_thread_detail(self, channel_id: str, thread_id: str) -> Any:
        return await self._get(
            "/channels/{channel_id}/threads/{thread_id}",
            channel_id=channel_id,
            thread_id=thread_id,
        )

    async def post_thread(self, channel_id: str, title: str, content: str, format: int) -> Any:
        payload = {"title": title, "content": content, "format": int(format)}
        return await self._put("/channels/{channel_id}/threads", json=payload, channel_id=channel_id)

    async def delete_thread(self, channel_id: str, thread_id: str) -> Any:
        return await self._delete(
            "/channels/{channel_id}/threads/{thread_id}",
            channel_id=channel_id,
            thread_id=thread_id,
        )

    async def update_audio(self, channel_id: str, audio_control: Any) -> Any:
        return await self._post("/channels/{channel_id}/audio", json=audio_control, channel_id=channel_id)

    async def on_microphone(self, channel_id: str) -> Any:
        return await self._put("/channels/{channel_id}/mic", channel_id=channel_id)

    async def off_microphone(self, channel_id: str) -> Any:
        return await self._delete("/channels/{channel_id}/mic", channel_id=channel_id)

    async def create_announce(self, guild_id: str, channel_id: str, message_id: str) -> Any:
        payload = {"channel_id": channel_id, "message_id": message_id}
        return await self._post("/guilds/{guild_id}/announces", json=payload, guild_id=guild_id)

    async def create_recommend_announce(self, guild_id: str, announces_type: int, recommend_channels: List[Any]) -> Any:
        payload = {"announces_type": int(announces_type), "recommend_channels": recommend_channels}
        return await self._post("/guilds/{guild_id}/announces", json=payload, guild_id=guild_id)

    async def delete_announce(self, guild_id: str, message_id: str = "all") -> Any:
        return await self._delete(
            "/guilds/{guild_id}/announces/{message_id}",
            guild_id=guild_id,
            message_id=message_id,
        )

    # ------------------------------------------------------------------ #
    # permissions / users / gateway
    # ------------------------------------------------------------------ #
    async def get_permissions(self, guild_id: str) -> Any:
        data = await self._get("/guilds/{guild_id}/api_permission", guild_id=guild_id)
        return data.get("apis") if isinstance(data, dict) else data

    async def post_permission_demand(self, guild_id: str, channel_id: str, api_identify: Any, desc: str) -> Any:
        payload = {"channel_id": channel_id, "api_identify": api_identify, "desc": desc}
        return await self._post("/guilds/{guild_id}/api_permission/demand", json=payload, guild_id=guild_id)

    async def me(self) -> Any:
        return await self._get("/users/@me")

    async def me_guilds(self, guild_id: Optional[str] = None, limit: int = 100, desc: bool = False) -> Any:
        params: Dict[str, Any] = {"limit": limit}
        if guild_id:
            params["before" if desc else "after"] = guild_id
        return await self._get("/users/@me/guilds", params=params)

    async def get_ws_url(self) -> Any:
        """Get the generic WebSocket gateway URL."""
        return await self._get("/gateway")

    async def get_ws_url_shard(self) -> Any:
        """Get the sharded WebSocket gateway URL and session limits."""
        return await self._get("/gateway/bot")

    # ------------------------------------------------------------------ #
    # v2 group / C2C messages and media
    # ------------------------------------------------------------------ #
    async def post_group_message(
        self,
        group_openid: str,
        msg_type: int = 0,
        content: Optional[str] = None,
        markdown: Optional[Any] = None,
        keyboard: Optional[Any] = None,
        msg_id: Optional[str] = None,
        event_id: Optional[str] = None,
        msg_seq: int = 1,
        media: Optional[Any] = None,
        message_reference: Optional[Any] = None,
        is_wakeup: Optional[bool] = None,
        **fields: Any,
    ) -> Any:
        payload = {
            "msg_type": int(msg_type),
            "content": content,
            "markdown": markdown,
            "keyboard": keyboard,
            "msg_id": msg_id,
            "event_id": event_id,
            "msg_seq": msg_seq,
            "media": media,
            "message_reference": message_reference,
            "is_wakeup": is_wakeup,
            **fields,
        }
        return await self._post("/v2/groups/{group_openid}/messages", json=payload, group_openid=group_openid)

    async def recall_group_message(self, group_openid: str, message_id: str) -> Any:
        return await self._delete(
            "/v2/groups/{group_openid}/messages/{message_id}",
            group_openid=group_openid,
            message_id=message_id,
        )

    async def post_group_file(
        self,
        group_openid: str,
        file_type: int,
        url: Optional[str] = None,
        srv_send_msg: bool = False,
        file_name: Optional[str] = None,
        upload_id: Optional[str] = None,
    ) -> Any:
        payload = {
            "file_type": int(file_type),
            "url": url,
            "srv_send_msg": srv_send_msg,
            "file_name": file_name,
            "upload_id": upload_id,
        }
        return await self._post("/v2/groups/{group_openid}/files", json=payload, group_openid=group_openid)

    async def post_group_upload_prepare(
        self,
        group_id: str,
        file_type: int,
        file_size: str,
        file_name: str,
        md5: str,
        sha1: str,
        md5_10m: str,
    ) -> Any:
        payload = {
            "file_type": int(file_type),
            "file_size": file_size,
            "file_name": file_name,
            "md5": md5,
            "sha1": sha1,
            "md5_10m": md5_10m,
        }
        return await self._post("/v2/groups/{group_id}/upload_prepare", json=payload, group_id=group_id)

    async def post_group_upload_part_finish(
        self,
        group_id: str,
        upload_id: str,
        part_index: int,
        block_size: str,
        md5: str,
    ) -> Any:
        payload = {
            "upload_id": upload_id,
            "part_index": int(part_index),
            "block_size": block_size,
            "md5": md5,
        }
        return await self._post("/v2/groups/{group_id}/upload_part_finish", json=payload, group_id=group_id)

    async def get_group_info(self, group_openid: str) -> Any:
        return await self._get("/v2/groups/{group_openid}/info", group_openid=group_openid)

    async def get_group_bot_state(self, group_openid: str) -> Any:
        return await self._get("/v2/groups/{group_openid}/bot_state", group_openid=group_openid)

    async def get_group_join_request_list(self, group_openid: str, cursor: Optional[str] = None, limit: int = 10) -> Any:
        return await self._get(
            "/v2/groups/{group_openid}/join_request_list",
            params={"cursor": cursor, "limit": limit},
            group_openid=group_openid,
        )

    async def approve_group_join_request(
        self,
        group_openid: str,
        member_openid: str,
        op: str,
        join_request_id: str,
        reject_reason: Optional[str] = None,
        add_to_member_blacklist: Optional[bool] = None,
    ) -> Any:
        payload = {
            "op": op,
            "join_request_id": join_request_id,
            "reject_reason": reject_reason,
            "add_to_member_blacklist": add_to_member_blacklist,
        }
        return await self._post(
            "/v2/groups/{group_openid}/approval_join_request/{member_openid}",
            json=payload,
            group_openid=group_openid,
            member_openid=member_openid,
        )

    async def get_group_restrict_chat_setting(self, group_openid: str) -> Any:
        return await self._get("/v2/groups/{group_openid}/restrict_chat_setting", group_openid=group_openid)

    async def set_group_restrict_chat_setting(self, group_openid: str, members: List[Any]) -> Any:
        return await self._post(
            "/v2/groups/{group_openid}/restrict_chat_setting",
            json={"members": members},
            group_openid=group_openid,
        )

    async def post_c2c_message(
        self,
        openid: str,
        msg_type: int = 0,
        content: Optional[str] = None,
        markdown: Optional[Any] = None,
        keyboard: Optional[Any] = None,
        msg_id: Optional[str] = None,
        event_id: Optional[str] = None,
        msg_seq: int = 1,
        media: Optional[Any] = None,
        message_reference: Optional[Any] = None,
        is_wakeup: Optional[bool] = None,
        **fields: Any,
    ) -> Any:
        payload = {
            "msg_type": int(msg_type),
            "content": content,
            "markdown": markdown,
            "keyboard": keyboard,
            "msg_id": msg_id,
            "event_id": event_id,
            "msg_seq": msg_seq,
            "media": media,
            "message_reference": message_reference,
            "is_wakeup": is_wakeup,
            **fields,
        }
        return await self._post("/v2/users/{openid}/messages", json=payload, openid=openid)

    async def recall_c2c_message(self, openid: str, message_id: str) -> Any:
        return await self._delete("/v2/users/{openid}/messages/{message_id}", openid=openid, message_id=message_id)

    async def post_c2c_file(
        self,
        openid: str,
        file_type: int,
        url: Optional[str] = None,
        srv_send_msg: bool = False,
        file_name: Optional[str] = None,
        upload_id: Optional[str] = None,
    ) -> Any:
        payload = {
            "file_type": int(file_type),
            "url": url,
            "srv_send_msg": srv_send_msg,
            "file_name": file_name,
            "upload_id": upload_id,
        }
        return await self._post("/v2/users/{openid}/files", json=payload, openid=openid)

    async def post_c2c_upload_prepare(
        self,
        user_id: str,
        file_type: int,
        file_size: str,
        file_name: str,
        md5: str,
        sha1: str,
        md5_10m: str,
    ) -> Any:
        payload = {
            "file_type": int(file_type),
            "file_size": file_size,
            "file_name": file_name,
            "md5": md5,
            "sha1": sha1,
            "md5_10m": md5_10m,
        }
        return await self._post("/v2/users/{user_id}/upload_prepare", json=payload, user_id=user_id)

    async def post_c2c_upload_part_finish(
        self,
        user_id: str,
        upload_id: str,
        part_index: int,
        block_size: str,
        md5: str,
    ) -> Any:
        payload = {
            "upload_id": upload_id,
            "part_index": int(part_index),
            "block_size": block_size,
            "md5": md5,
        }
        return await self._post("/v2/users/{user_id}/upload_part_finish", json=payload, user_id=user_id)

    async def post_c2c_stream_message(self, openid: str, **fields: Any) -> Any:
        """Send a streaming C2C message."""
        return await self._post("/v2/users/{openid}/stream_messages", json=fields, openid=openid)

    # ------------------------------------------------------------------ #
    # join approval strategies / menu / panels / share links
    # ------------------------------------------------------------------ #
    async def get_group_join_approval_strategies(self, cursor: Optional[str] = None, limit: int = 10) -> Any:
        return await self._get("/v2/groups/join_approval_strategy", params={"cursor": cursor, "limit": limit})

    async def create_group_join_approval_strategy(self, **fields: Any) -> Any:
        return await self._post("/v2/groups/join_approval_strategy", json=fields)

    async def delete_group_join_approval_strategy(self, strategy_id: str) -> Any:
        return await self._delete("/v2/groups/join_approval_strategy/{strategy_id}", strategy_id=strategy_id)

    async def update_group_join_approval_strategy(self, strategy_id: str, **fields: Any) -> Any:
        return await self._patch("/v2/groups/join_approval_strategy/{strategy_id}", json=fields, strategy_id=strategy_id)

    async def execute_group_join_approval_strategy(self, strategy_id: str) -> Any:
        return await self._post("/v2/groups/join_approval_strategy/{strategy_id}/execute", strategy_id=strategy_id)

    async def update_group_join_approval_strategy_whitelist(self, strategy_id: str, **fields: Any) -> Any:
        return await self._post(
            "/v2/groups/join_approval_strategy/{strategy_id}/whitelist_users",
            json=fields,
            strategy_id=strategy_id,
        )

    async def get_menu(self) -> Any:
        return await self._get("/v2/menu")

    async def update_menu(self, menu: Any) -> Any:
        return await self._put("/v2/menu", json={"menu": menu})

    async def get_panels(self) -> Any:
        return await self._get("/v2/panels")

    async def create_panel(self, **fields: Any) -> Any:
        return await self._post("/v2/panels", json=fields)

    async def delete_panel(self, panel_id: str) -> Any:
        return await self._delete("/v2/panels/{panel_id}", panel_id=panel_id)

    async def get_panel(self, panel_id: str) -> Any:
        return await self._get("/v2/panels/{panel_id}", panel_id=panel_id)

    async def update_panel(self, panel_id: str, panel: Any) -> Any:
        return await self._put("/v2/panels/{panel_id}", json={"panel": panel}, panel_id=panel_id)

    async def update_panel_target(self, panel_id: str, **fields: Any) -> Any:
        return await self._put("/v2/panels/{panel_id}/target", json=fields, panel_id=panel_id)

    async def create_url_link(self, url_link: str) -> Any:
        return await self._post("/v2/generate_url_link", json={"url_link": url_link})

    # ------------------------------------------------------------------ #
    # high-level chunked media upload
    # ------------------------------------------------------------------ #
    @staticmethod
    def _compute_file_digests(file_path: str):
        """Return (file_size, md5, sha1, md5_10m) for a local file."""
        prefix_size = 10002432
        with open(file_path, "rb") as handle:
            prefix = handle.read(prefix_size)

        md5_10m = hashlib.md5(prefix).hexdigest()
        md5 = hashlib.md5()
        sha1 = hashlib.sha1()
        file_size = 0

        with open(file_path, "rb") as handle:
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                file_size += len(chunk)
                md5.update(chunk)
                sha1.update(chunk)

        return file_size, md5.hexdigest(), sha1.hexdigest(), md5_10m

    async def _upload_chunks(self, file_path: str, parts: List[Any], on_part) -> None:
        async with aiohttp.ClientSession() as session:
            with open(file_path, "rb") as handle:
                for part in parts:
                    index = part["index"]
                    url = part["presigned_url"]
                    block_size = int(part["block_size"])

                    data = handle.read(block_size)
                    if not data:
                        break

                    async with session.put(url, data=data) as response:
                        response.raise_for_status()

                    part_md5 = hashlib.md5(data).hexdigest()
                    await on_part(index=index, size=len(data), part_md5=part_md5)

    async def upload_group_media(
        self,
        group_openid: str,
        file_path: str,
        file_type: int,
        srv_send_msg: bool = False,
    ) -> Any:
        """Upload a local file to group chat using the chunked upload flow.

        group_openid is the group OpenID.  It is used for both the chunked
        upload endpoints and the final files endpoint.
        """
        file_size, md5, sha1, md5_10m = self._compute_file_digests(file_path)

        prepare = await self.post_group_upload_prepare(
            group_id=group_openid,
            file_type=file_type,
            file_size=str(file_size),
            file_name=os.path.basename(file_path),
            md5=md5,
            sha1=sha1,
            md5_10m=md5_10m,
        )

        upload_id = prepare["upload_id"]
        parts = prepare.get("parts", [])

        async def finish_part(index: int, size: int, part_md5: str) -> None:
            await self.post_group_upload_part_finish(
                group_id=group_openid,
                upload_id=upload_id,
                part_index=index,
                block_size=str(size),
                md5=part_md5,
            )

        await self._upload_chunks(file_path, parts, finish_part)

        return await self.post_group_file(
            group_openid=group_openid,
            file_type=file_type,
            upload_id=upload_id,
            file_name=os.path.basename(file_path),
            srv_send_msg=srv_send_msg,
        )

    async def upload_c2c_media(
        self,
        user_openid: str,
        file_path: str,
        file_type: int,
        srv_send_msg: bool = False,
    ) -> Any:
        """Upload a local file to C2C chat using the chunked upload flow.

        user_openid is the user OpenID.  It is used for both the chunked
        upload endpoints and the final files endpoint.
        """
        file_size, md5, sha1, md5_10m = self._compute_file_digests(file_path)

        prepare = await self.post_c2c_upload_prepare(
            user_id=user_openid,
            file_type=file_type,
            file_size=str(file_size),
            file_name=os.path.basename(file_path),
            md5=md5,
            sha1=sha1,
            md5_10m=md5_10m,
        )

        upload_id = prepare["upload_id"]
        parts = prepare.get("parts", [])

        async def finish_part(index: int, size: int, part_md5: str) -> None:
            await self.post_c2c_upload_part_finish(
                user_id=user_openid,
                upload_id=upload_id,
                part_index=index,
                block_size=str(size),
                md5=part_md5,
            )

        await self._upload_chunks(file_path, parts, finish_part)

        return await self.post_c2c_file(
            openid=user_openid,
            file_type=file_type,
            upload_id=upload_id,
            file_name=os.path.basename(file_path),
            srv_send_msg=srv_send_msg,
        )
