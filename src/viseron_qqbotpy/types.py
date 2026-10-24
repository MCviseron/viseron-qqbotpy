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
    "GroupBlacklistUser",
    "GroupMember",
    "GroupMemberBlacklist",
    "GroupMemberList",
    "GroupMemberMuteState",
    "GroupMuteRecurringRule",
    "GroupMuteRule",
    "GroupMuteScheduleRule",
    "GroupRestrictChatSetting",
    "InputNotify",
    "Keyboard",
    "KeyboardContent",
    "MediaInfo",
    "MediaImage",
    "MediaImageComplete",
    "MediaImageList",
    "MediaImagePrepare",
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


class MediaImagePrepare(TypedDict, total=False):
    """Response of POST /v2/media-images/prepare."""

    upload_id: str  # valid for 4 hours
    presigned_url: str  # PUT the image binary here
    expires_in: int  # presigned url lifetime in seconds


class MediaImage(TypedDict, total=False):
    """One entry of GET /v2/media-images."""

    image_id: str
    url: str  # qqbot-media://image/v1/<token>
    file_name: str
    preview_url: str  # short-lived COS link, do not persist
    created_at: int  # unix seconds
    expires_at: int  # unix seconds, extended whenever a message references it


class MediaImageList(TypedDict, total=False):
    images: List[MediaImage]
    next_cursor: str  # empty string means the last page
    total: int  # valid images of the bot, same counter as the 100-image quota


class MediaImageComplete(TypedDict, total=False):
    """Response of POST /v2/media-images/complete."""

    image_id: str
    url: str  # qqbot-media://image/v1/<token>
    ttl: int  # sliding window in seconds (90 days)
    preview_url: str


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


class GroupMember(TypedDict, total=False):
    """One entry of GET /v2/groups/{group_openid}/members."""

    member_openid: str
    username: str
    member_role: str  # member | owner | admin
    bot: bool
    joined_at: str  # RFC3339
    union_openid: str


class GroupMemberList(TypedDict, total=False):
    members: List[GroupMember]
    next_cursor: str  # empty string means the last page


class GroupBlacklistUser(TypedDict, total=False):
    """One entry of GET /v2/groups/{group_openid}/member_blacklist."""

    union_openid: str
    member_openid: str
    username: str
    banned_at: str  # RFC3339
    bot: bool


class GroupMemberBlacklist(TypedDict, total=False):
    users: List[GroupBlacklistUser]
    next_cursor: str


class GroupMuteScheduleRule(TypedDict, total=False):
    """One fixed-time mute window inside a group mute rule."""

    task_id: str
    start_at: str  # RFC3339
    end_at: str  # RFC3339
    enabled: bool


class GroupMuteRecurringRule(TypedDict, total=False):
    """One recurring mute window inside a group mute rule."""

    task_id: str
    weekdays: List[int]  # 1=Monday ... 7=Sunday
    start_time: str  # HH:mm, Beijing time
    end_time: str  # HH:mm, Beijing time; smaller than start_time means overnight
    enabled: bool


class GroupMuteRule(TypedDict, total=False):
    """The group-wide mute configuration."""

    mode: str  # none | always | schedule
    schedule_rules: List[GroupMuteScheduleRule]
    recurring_rules: List[GroupMuteRecurringRule]


class GroupMemberMuteState(TypedDict, total=False):
    member_openid: str
    mute_expire_at: str  # RFC3339
    username: str
    union_openid: str


class GroupRestrictChatSetting(TypedDict, total=False):
    """Response of GET /v2/groups/{group_openid}/restrict_chat_setting."""

    global_rule: GroupMuteRule
    members: List[GroupMemberMuteState]
