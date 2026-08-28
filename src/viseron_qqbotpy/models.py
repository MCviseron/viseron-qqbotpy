"""Event models dispatched to user callbacks.

Models are small dataclasses that wrap the gateway payload.  Common fields are
hoisted to attributes for readability; the complete payload is always
available as :attr:`raw` so new platform fields never require an SDK upgrade.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

__all__ = [
    "AudioAction",
    "C2CManageEvent",
    "C2CMessage",
    "Channel",
    "DirectMessage",
    "ForumThread",
    "GroupJoinRequestEvent",
    "GroupManageEvent",
    "GroupMemberEvent",
    "GroupMessage",
    "Guild",
    "Interaction",
    "Member",
    "Message",
    "MessageAudit",
    "OpenForumThread",
    "PublicAudio",
    "Reaction",
    "SubscribeMessageStatusEvent",
    "User",
]


def _str(value: Any) -> Optional[str]:
    return value if isinstance(value, str) else (str(value) if value is not None else None)


@dataclass
class User:
    id: Optional[str] = None
    username: Optional[str] = None
    avatar: Optional[str] = None
    bot: Optional[bool] = None
    union_openid: Optional[str] = None
    union_user_account: Optional[str] = None
    user_openid: Optional[str] = None
    member_openid: Optional[str] = None
    member_role: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_payload(cls, data: Any) -> "User":
        data = data or {}
        return cls(
            id=_str(data.get("id")),
            username=data.get("username"),
            avatar=data.get("avatar"),
            bot=data.get("bot"),
            union_openid=data.get("union_openid"),
            union_user_account=data.get("union_user_account"),
            user_openid=data.get("user_openid"),
            member_openid=data.get("member_openid"),
            member_role=data.get("member_role"),
            raw=dict(data),
        )


@dataclass
class Message:
    """A channel (guild) message event."""

    id: Optional[str] = None
    channel_id: Optional[str] = None
    guild_id: Optional[str] = None
    content: Optional[str] = None
    author: Optional[User] = None
    member: Optional[Dict[str, Any]] = None
    mentions: List[User] = field(default_factory=list)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    message_reference: Optional[Dict[str, Any]] = None
    seq: Optional[int] = None
    seq_in_channel: Optional[int] = None
    timestamp: Optional[str] = None
    event_id: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)
    api: Any = field(default=None, repr=False)

    @classmethod
    def from_payload(cls, api: Any, event_id: Optional[str], data: Dict[str, Any]) -> "Message":
        data = data or {}
        mentions = [User.from_payload(item) for item in data.get("mentions") or []]
        return cls(
            id=_str(data.get("id")),
            channel_id=_str(data.get("channel_id")),
            guild_id=_str(data.get("guild_id")),
            content=data.get("content"),
            author=User.from_payload(data.get("author")),
            member=data.get("member"),
            mentions=mentions,
            attachments=list(data.get("attachments") or []),
            message_reference=data.get("message_reference"),
            seq=data.get("seq"),
            seq_in_channel=data.get("seq_in_channel"),
            timestamp=data.get("timestamp"),
            event_id=event_id,
            raw=dict(data),
            api=api,
        )

    async def reply(self, **kwargs: Any) -> Any:
        if self.api is None:
            raise RuntimeError("message has no attached API client")
        return await self.api.post_message(channel_id=self.channel_id, msg_id=self.id, **kwargs)


@dataclass
class DirectMessage:
    id: Optional[str] = None
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None
    content: Optional[str] = None
    author: Optional[User] = None
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    message_reference: Optional[Dict[str, Any]] = None
    seq: Optional[int] = None
    seq_in_channel: Optional[int] = None
    src_guild_id: Optional[str] = None
    timestamp: Optional[str] = None
    event_id: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)
    api: Any = field(default=None, repr=False)

    @classmethod
    def from_payload(cls, api: Any, event_id: Optional[str], data: Dict[str, Any]) -> "DirectMessage":
        data = data or {}
        return cls(
            id=_str(data.get("id")),
            guild_id=_str(data.get("guild_id")),
            channel_id=_str(data.get("channel_id")),
            content=data.get("content"),
            author=User.from_payload(data.get("author")),
            attachments=list(data.get("attachments") or []),
            message_reference=data.get("message_reference"),
            seq=data.get("seq"),
            seq_in_channel=data.get("seq_in_channel"),
            src_guild_id=_str(data.get("src_guild_id")),
            timestamp=data.get("timestamp"),
            event_id=event_id,
            raw=dict(data),
            api=api,
        )

    async def reply(self, **kwargs: Any) -> Any:
        if self.api is None:
            raise RuntimeError("message has no attached API client")
        return await self.api.post_dms(guild_id=self.guild_id, msg_id=self.id, **kwargs)


@dataclass
class GroupMessage:
    """A group message event (GROUP_AT_MESSAGE_CREATE or GROUP_MESSAGE_CREATE)."""

    id: Optional[str] = None
    group_openid: Optional[str] = None
    content: Optional[str] = None
    author: Optional[User] = None
    mentions: List[User] = field(default_factory=list)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    message_reference: Optional[Dict[str, Any]] = None
    msg_seq: Optional[int] = None
    timestamp: Optional[str] = None
    event_id: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)
    api: Any = field(default=None, repr=False)

    @classmethod
    def from_payload(cls, api: Any, event_id: Optional[str], data: Dict[str, Any]) -> "GroupMessage":
        data = data or {}
        mentions = [User.from_payload(item) for item in data.get("mentions") or []]
        return cls(
            id=_str(data.get("id")),
            group_openid=_str(data.get("group_openid")),
            content=data.get("content"),
            author=User.from_payload(data.get("author")),
            mentions=mentions,
            attachments=list(data.get("attachments") or []),
            message_reference=data.get("message_reference"),
            msg_seq=data.get("msg_seq"),
            timestamp=data.get("timestamp"),
            event_id=event_id,
            raw=dict(data),
            api=api,
        )

    async def reply(self, **kwargs: Any) -> Any:
        if self.api is None:
            raise RuntimeError("message has no attached API client")
        return await self.api.post_group_message(group_openid=self.group_openid, msg_id=self.id, **kwargs)


@dataclass
class C2CMessage:
    id: Optional[str] = None
    content: Optional[str] = None
    author: Optional[User] = None
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    message_reference: Optional[Dict[str, Any]] = None
    msg_seq: Optional[int] = None
    timestamp: Optional[str] = None
    event_id: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)
    api: Any = field(default=None, repr=False)

    @classmethod
    def from_payload(cls, api: Any, event_id: Optional[str], data: Dict[str, Any]) -> "C2CMessage":
        data = data or {}
        return cls(
            id=_str(data.get("id")),
            content=data.get("content"),
            author=User.from_payload(data.get("author")),
            attachments=list(data.get("attachments") or []),
            message_reference=data.get("message_reference"),
            msg_seq=data.get("msg_seq"),
            timestamp=data.get("timestamp"),
            event_id=event_id,
            raw=dict(data),
            api=api,
        )

    async def reply(self, **kwargs: Any) -> Any:
        if self.api is None:
            raise RuntimeError("message has no attached API client")
        openid = self.author.user_openid if self.author else None
        return await self.api.post_c2c_message(openid=openid, msg_id=self.id, **kwargs)


@dataclass
class MessageAudit:
    audit_id: Optional[str] = None
    message_id: Optional[str] = None
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None
    event_id: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)
    api: Any = field(default=None, repr=False)

    @classmethod
    def from_payload(cls, api: Any, event_id: Optional[str], data: Dict[str, Any]) -> "MessageAudit":
        data = data or {}
        return cls(
            audit_id=_str(data.get("audit_id")),
            message_id=_str(data.get("message_id")),
            guild_id=_str(data.get("guild_id")),
            channel_id=_str(data.get("channel_id")),
            event_id=event_id,
            raw=dict(data),
            api=api,
        )


@dataclass
class Guild:
    id: Optional[str] = None
    name: Optional[str] = None
    icon: Optional[str] = None
    owner_id: Optional[str] = None
    op_user_id: Optional[str] = None
    member_count: Optional[int] = None
    max_members: Optional[int] = None
    description: Optional[str] = None
    joined_at: Optional[str] = None
    event_id: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)
    api: Any = field(default=None, repr=False)

    @classmethod
    def from_payload(cls, api: Any, event_id: Optional[str], data: Dict[str, Any]) -> "Guild":
        data = data or {}
        return cls(
            id=_str(data.get("id")),
            name=data.get("name"),
            icon=data.get("icon"),
            owner_id=_str(data.get("owner_id")),
            op_user_id=_str(data.get("op_user_id")),
            member_count=data.get("member_count"),
            max_members=data.get("max_members"),
            description=data.get("description"),
            joined_at=data.get("joined_at"),
            event_id=event_id,
            raw=dict(data),
            api=api,
        )


@dataclass
class Channel:
    id: Optional[str] = None
    guild_id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[int] = None
    sub_type: Optional[int] = None
    owner_id: Optional[str] = None
    op_user_id: Optional[str] = None
    position: Optional[int] = None
    parent_id: Optional[str] = None
    private_type: Optional[int] = None
    speak_permission: Optional[int] = None
    application_id: Optional[str] = None
    event_id: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)
    api: Any = field(default=None, repr=False)

    @classmethod
    def from_payload(cls, api: Any, event_id: Optional[str], data: Dict[str, Any]) -> "Channel":
        data = data or {}
        return cls(
            id=_str(data.get("id")),
            guild_id=_str(data.get("guild_id")),
            name=data.get("name"),
            type=data.get("type"),
            sub_type=data.get("sub_type"),
            owner_id=_str(data.get("owner_id")),
            op_user_id=_str(data.get("op_user_id")),
            position=data.get("position"),
            parent_id=_str(data.get("parent_id")),
            private_type=data.get("private_type"),
            speak_permission=data.get("speak_permission"),
            application_id=_str(data.get("application_id")),
            event_id=event_id,
            raw=dict(data),
            api=api,
        )


@dataclass
class Member:
    user: Optional[User] = None
    nick: Optional[str] = None
    roles: List[str] = field(default_factory=list)
    joined_at: Optional[str] = None
    guild_id: Optional[str] = None
    event_id: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)
    api: Any = field(default=None, repr=False)

    @classmethod
    def from_payload(cls, api: Any, event_id: Optional[str], data: Dict[str, Any]) -> "Member":
        data = data or {}
        return cls(
            user=User.from_payload(data.get("user")),
            nick=data.get("nick"),
            roles=list(data.get("roles") or []),
            joined_at=data.get("joined_at"),
            guild_id=_str(data.get("guild_id")),
            event_id=event_id,
            raw=dict(data),
            api=api,
        )


@dataclass
class Reaction:
    user_id: Optional[str] = None
    channel_id: Optional[str] = None
    guild_id: Optional[str] = None
    emoji: Optional[Dict[str, Any]] = None
    target: Optional[Dict[str, Any]] = None
    event_id: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)
    api: Any = field(default=None, repr=False)

    @classmethod
    def from_payload(cls, api: Any, event_id: Optional[str], data: Dict[str, Any]) -> "Reaction":
        data = data or {}
        return cls(
            user_id=_str(data.get("user_id")),
            channel_id=_str(data.get("channel_id")),
            guild_id=_str(data.get("guild_id")),
            emoji=data.get("emoji"),
            target=data.get("target"),
            event_id=event_id,
            raw=dict(data),
            api=api,
        )


@dataclass
class Interaction:
    id: Optional[str] = None
    type: Optional[int] = None
    scene: Optional[str] = None
    chat_type: Optional[int] = None
    application_id: Optional[str] = None
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None
    user_openid: Optional[str] = None
    group_openid: Optional[str] = None
    group_member_openid: Optional[str] = None
    timestamp: Optional[str] = None
    version: Optional[int] = None
    data: Optional[Dict[str, Any]] = None
    event_id: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)
    api: Any = field(default=None, repr=False)

    @classmethod
    def from_payload(cls, api: Any, event_id: Optional[str], data: Dict[str, Any]) -> "Interaction":
        data = data or {}
        return cls(
            id=_str(data.get("id")),
            type=data.get("type"),
            scene=data.get("scene"),
            chat_type=data.get("chat_type"),
            application_id=_str(data.get("application_id")),
            guild_id=_str(data.get("guild_id")),
            channel_id=_str(data.get("channel_id")),
            user_openid=data.get("user_openid"),
            group_openid=data.get("group_openid"),
            group_member_openid=data.get("group_member_openid"),
            timestamp=data.get("timestamp"),
            version=data.get("version"),
            data=data.get("data"),
            event_id=event_id,
            raw=dict(data),
            api=api,
        )


@dataclass
class AudioAction:
    channel_id: Optional[str] = None
    guild_id: Optional[str] = None
    audio_url: Optional[str] = None
    text: Optional[str] = None
    event_id: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)
    api: Any = field(default=None, repr=False)

    @classmethod
    def from_payload(cls, api: Any, event_id: Optional[str], data: Dict[str, Any]) -> "AudioAction":
        data = data or {}
        return cls(
            channel_id=_str(data.get("channel_id")),
            guild_id=_str(data.get("guild_id")),
            audio_url=data.get("audio_url"),
            text=data.get("text"),
            event_id=event_id,
            raw=dict(data),
            api=api,
        )


@dataclass
class PublicAudio:
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None
    channel_type: Optional[int] = None
    user_id: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)
    api: Any = field(default=None, repr=False)

    @classmethod
    def from_payload(cls, api: Any, data: Dict[str, Any]) -> "PublicAudio":
        data = data or {}
        return cls(
            guild_id=_str(data.get("guild_id")),
            channel_id=_str(data.get("channel_id")),
            channel_type=data.get("channel_type"),
            user_id=_str(data.get("user_id")),
            raw=dict(data),
            api=api,
        )


@dataclass
class ForumThread:
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None
    author_id: Optional[str] = None
    thread_info: Optional[Dict[str, Any]] = None
    event_id: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)
    api: Any = field(default=None, repr=False)

    @classmethod
    def from_payload(cls, api: Any, event_id: Optional[str], data: Dict[str, Any]) -> "ForumThread":
        data = data or {}
        return cls(
            guild_id=_str(data.get("guild_id")),
            channel_id=_str(data.get("channel_id")),
            author_id=_str(data.get("author_id")),
            thread_info=data.get("thread_info"),
            event_id=event_id,
            raw=dict(data),
            api=api,
        )


@dataclass
class OpenForumThread:
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None
    author_id: Optional[str] = None
    thread_info: Optional[Dict[str, Any]] = None
    event_id: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)
    api: Any = field(default=None, repr=False)

    @classmethod
    def from_payload(cls, api: Any, event_id: Optional[str], data: Dict[str, Any]) -> "OpenForumThread":
        data = data or {}
        return cls(
            guild_id=_str(data.get("guild_id")),
            channel_id=_str(data.get("channel_id")),
            author_id=_str(data.get("author_id")),
            thread_info=data.get("thread_info"),
            event_id=event_id,
            raw=dict(data),
            api=api,
        )


@dataclass
class GroupManageEvent:
    timestamp: Optional[str] = None
    group_openid: Optional[str] = None
    op_member_openid: Optional[str] = None
    event_id: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)
    api: Any = field(default=None, repr=False)

    @classmethod
    def from_payload(cls, api: Any, event_id: Optional[str], data: Dict[str, Any]) -> "GroupManageEvent":
        data = data or {}
        return cls(
            timestamp=data.get("timestamp"),
            group_openid=_str(data.get("group_openid")),
            op_member_openid=data.get("op_member_openid"),
            event_id=event_id,
            raw=dict(data),
            api=api,
        )


@dataclass
class C2CManageEvent:
    timestamp: Optional[str] = None
    openid: Optional[str] = None
    event_id: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)
    api: Any = field(default=None, repr=False)

    @classmethod
    def from_payload(cls, api: Any, event_id: Optional[str], data: Dict[str, Any]) -> "C2CManageEvent":
        data = data or {}
        return cls(
            timestamp=data.get("timestamp"),
            openid=data.get("openid"),
            event_id=event_id,
            raw=dict(data),
            api=api,
        )


@dataclass
class GroupMemberEvent:
    timestamp: Optional[str] = None
    group_openid: Optional[str] = None
    member_openid: Optional[str] = None
    user_openid: Optional[str] = None
    event_id: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)
    api: Any = field(default=None, repr=False)

    @classmethod
    def from_payload(cls, api: Any, event_id: Optional[str], data: Dict[str, Any]) -> "GroupMemberEvent":
        data = data or {}
        return cls(
            timestamp=data.get("timestamp"),
            group_openid=_str(data.get("group_openid")),
            member_openid=data.get("member_openid"),
            user_openid=data.get("user_openid"),
            event_id=event_id,
            raw=dict(data),
            api=api,
        )


@dataclass
class GroupJoinRequestEvent:
    group_openid: Optional[str] = None
    join_request_id: Optional[str] = None
    member_openid: Optional[str] = None
    union_openid: Optional[str] = None
    username: Optional[str] = None
    apply_at: Optional[str] = None
    apply_source: Optional[str] = None
    invited_by: Optional[str] = None
    bot: Optional[bool] = None
    verify_info: Optional[Dict[str, Any]] = None
    auto_approved: Optional[Dict[str, Any]] = None
    event_id: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)
    api: Any = field(default=None, repr=False)

    @classmethod
    def from_payload(cls, api: Any, event_id: Optional[str], data: Dict[str, Any]) -> "GroupJoinRequestEvent":
        data = data or {}
        return cls(
            group_openid=_str(data.get("group_openid")),
            join_request_id=_str(data.get("join_request_id")),
            member_openid=data.get("member_openid"),
            union_openid=data.get("union_openid"),
            username=data.get("username"),
            apply_at=data.get("apply_at"),
            apply_source=data.get("apply_source"),
            invited_by=data.get("invited_by"),
            bot=data.get("bot"),
            verify_info=data.get("verify_info"),
            auto_approved=data.get("auto_approved"),
            event_id=event_id,
            raw=dict(data),
            api=api,
        )


@dataclass
class SubscribeMessageStatusEvent:
    group_openid: Optional[str] = None
    openid: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    event_id: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)
    api: Any = field(default=None, repr=False)

    @classmethod
    def from_payload(cls, api: Any, event_id: Optional[str], data: Dict[str, Any]) -> "SubscribeMessageStatusEvent":
        data = data or {}
        return cls(
            group_openid=_str(data.get("group_openid")),
            openid=data.get("openid"),
            result=data.get("result"),
            event_id=event_id,
            raw=dict(data),
            api=api,
        )
