"""Typed payload helpers.

These TypedDict classes are optional; every API method also accepts plain
dicts.  They exist to give editors better autocompletion when constructing
message and event payloads.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict, Union

__all__ = [
    "Action",
    "Ark",
    "ArkKv",
    "Button",
    "C2CMessagePayload",
    "ChannelPayload",
    "DirectMessagePayload",
    "Embed",
    "EmbedField",
    "FileInfo",
    "GuildMemberPayload",
    "GuildPayload",
    "InputNotify",
    "Keyboard",
    "KeyboardContent",
    "MediaInfo",
    "MessageArk",
    "MessageEmbed",
    "MessageMarkdown",
    "MessagePayload",
    "MessageReference",
    "MessageScene",
    "Permission",
    "RenderData",
    "Row",
    "User",
]


class User(TypedDict, total=False):
    id: str
    username: str
    avatar: str
    bot: bool
    union_openid: str
    union_user_account: str
    user_openid: str
    member_openid: str
    member_role: str


class MessageMarkdown(TypedDict, total=False):
    template_id: int
    custom_template_id: str
    content: str
    force_verify_image_resource: bool


class RenderData(TypedDict, total=False):
    label: str
    visited_label: str
    style: int


class Permission(TypedDict, total=False):
    type: int
    specify_user_ids: List[str]
    specify_role_ids: List[str]


class Action(TypedDict, total=False):
    type: int
    permission: Permission
    data: str
    click_limit: int
    unsupport_tips: str
    enter: bool
    reply: bool
    anchor: int


class Button(TypedDict, total=False):
    id: str
    render_data: RenderData
    action: Action


class Row(TypedDict, total=False):
    buttons: List[Button]


class KeyboardContent(TypedDict, total=False):
    rows: List[Row]


class Keyboard(TypedDict, total=False):
    id: str
    content: KeyboardContent


class MessageReference(TypedDict, total=False):
    message_id: str
    ignore_get_message_error: bool


class FileInfo(TypedDict, total=False):
    file_uuid: str
    file_info: str
    ttl: int


class MediaInfo(TypedDict, total=False):
    file_info: str


class InputNotify(TypedDict, total=False):
    input_type: int
    input_second: int


class MessageScene(TypedDict, total=False):
    source: str
    ext: str


class MessageArk(TypedDict, total=False):
    template_id: int
    kv: List["ArkKv"]


class ArkKv(TypedDict, total=False):
    key: str
    value: str
    obj: List["ArkKv"]


class Ark(TypedDict, total=False):
    template_id: int
    kv: List[ArkKv]


class EmbedField(TypedDict, total=False):
    name: str


class Embed(TypedDict, total=False):
    title: str
    prompt: str
    thumbnail: Dict[str, Any]
    fields: List[EmbedField]


class MessageEmbed(TypedDict, total=False):
    title: str
    prompt: str
    thumbnail: Dict[str, Any]
    fields: List[EmbedField]


class MessagePayload(TypedDict, total=False):
    id: str
    channel_id: str
    guild_id: str
    content: str
    author: User
    member: Dict[str, Any]
    mentions: List[User]
    attachments: List[Dict[str, Any]]
    message_reference: MessageReference
    seq: int
    seq_in_channel: int
    timestamp: str
    event_id: str


class DirectMessagePayload(TypedDict, total=False):
    id: str
    channel_id: str
    guild_id: str
    content: str
    author: User
    attachments: List[Dict[str, Any]]
    message_reference: MessageReference
    seq: int
    seq_in_channel: int
    src_guild_id: str
    timestamp: str


class C2CMessagePayload(TypedDict, total=False):
    id: str
    author: User
    content: str
    timestamp: str
    attachments: List[Dict[str, Any]]
    message_reference: MessageReference
    msg_seq: int
    message_scene: MessageScene


class GuildPayload(TypedDict, total=False):
    id: str
    name: str
    icon: str
    owner_id: str
    member_count: int
    max_members: int
    description: str
    joined_at: str


class ChannelPayload(TypedDict, total=False):
    id: str
    guild_id: str
    name: str
    type: int
    sub_type: int
    position: int
    parent_id: str
    owner_id: str
    private_type: int
    speak_permission: int
    application_id: str


class GuildMemberPayload(TypedDict, total=False):
    user: User
    nick: str
    roles: List[str]
    joined_at: str
    guild_id: str
