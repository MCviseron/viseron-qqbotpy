"""Gateway event parser/dispatcher.

Parser methods are discovered by name: parse_guild_create handles the
GUILD_CREATE event and dispatches to Client.on_guild_create.  The raw gateway
message is passed in so the event id can be forwarded to the model.
"""

from __future__ import annotations

import inspect
from typing import Any, Callable, Dict

from . import models
from .logging import get_logger

__all__ = ["EventDispatcher"]

_log = get_logger(__name__)


class EventDispatcher:
    def __init__(self, dispatch: Callable[..., None], api: Any) -> None:
        self._dispatch = dispatch
        self.api = api
        self.parsers: Dict[str, Callable[[Dict[str, Any]], None]] = {}
        for attr, func in inspect.getmembers(self):
            if attr.startswith("parse_") and callable(func):
                self.parsers[attr[6:].lower()] = func

    # system events -------------------------------------------------- #
    def parse_ready(self, payload: Dict[str, Any]) -> None:
        self._dispatch("ready")

    def parse_resumed(self, payload: Dict[str, Any]) -> None:
        self._dispatch("resumed")

    # guild/channel -------------------------------------------------- #
    def parse_guild_create(self, payload: Dict[str, Any]) -> None:
        self._dispatch("guild_create", models.Guild.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_guild_update(self, payload: Dict[str, Any]) -> None:
        self._dispatch("guild_update", models.Guild.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_guild_delete(self, payload: Dict[str, Any]) -> None:
        self._dispatch("guild_delete", models.Guild.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_channel_create(self, payload: Dict[str, Any]) -> None:
        self._dispatch("channel_create", models.Channel.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_channel_update(self, payload: Dict[str, Any]) -> None:
        self._dispatch("channel_update", models.Channel.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_channel_delete(self, payload: Dict[str, Any]) -> None:
        self._dispatch("channel_delete", models.Channel.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    # members -------------------------------------------------------- #
    def parse_guild_member_add(self, payload: Dict[str, Any]) -> None:
        self._dispatch("guild_member_add", models.Member.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_guild_member_update(self, payload: Dict[str, Any]) -> None:
        self._dispatch("guild_member_update", models.Member.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_guild_member_remove(self, payload: Dict[str, Any]) -> None:
        self._dispatch("guild_member_remove", models.Member.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    # messages ------------------------------------------------------- #
    def parse_message_create(self, payload: Dict[str, Any]) -> None:
        self._dispatch("message_create", models.Message.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_message_delete(self, payload: Dict[str, Any]) -> None:
        self._dispatch("message_delete", models.Message.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_at_message_create(self, payload: Dict[str, Any]) -> None:
        self._dispatch("at_message_create", models.Message.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_public_message_delete(self, payload: Dict[str, Any]) -> None:
        self._dispatch("public_message_delete", models.Message.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_direct_message_create(self, payload: Dict[str, Any]) -> None:
        self._dispatch("direct_message_create", models.DirectMessage.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_direct_message_delete(self, payload: Dict[str, Any]) -> None:
        self._dispatch("direct_message_delete", models.DirectMessage.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    # group / c2c ---------------------------------------------------- #
    def parse_group_at_message_create(self, payload: Dict[str, Any]) -> None:
        self._dispatch("group_at_message_create", models.GroupMessage.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_group_message_create(self, payload: Dict[str, Any]) -> None:
        self._dispatch("group_message_create", models.GroupMessage.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_c2c_message_create(self, payload: Dict[str, Any]) -> None:
        self._dispatch("c2c_message_create", models.C2CMessage.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_group_add_robot(self, payload: Dict[str, Any]) -> None:
        self._dispatch("group_add_robot", models.GroupManageEvent.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_group_del_robot(self, payload: Dict[str, Any]) -> None:
        self._dispatch("group_del_robot", models.GroupManageEvent.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_group_msg_reject(self, payload: Dict[str, Any]) -> None:
        self._dispatch("group_msg_reject", models.GroupManageEvent.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_group_msg_receive(self, payload: Dict[str, Any]) -> None:
        self._dispatch("group_msg_receive", models.GroupManageEvent.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_group_member_add(self, payload: Dict[str, Any]) -> None:
        self._dispatch("group_member_add", models.GroupMemberEvent.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_group_member_remove(self, payload: Dict[str, Any]) -> None:
        self._dispatch("group_member_remove", models.GroupMemberEvent.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_group_join_request(self, payload: Dict[str, Any]) -> None:
        self._dispatch("group_join_request", models.GroupJoinRequestEvent.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_friend_add(self, payload: Dict[str, Any]) -> None:
        self._dispatch("friend_add", models.C2CManageEvent.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_friend_del(self, payload: Dict[str, Any]) -> None:
        self._dispatch("friend_del", models.C2CManageEvent.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_c2c_msg_reject(self, payload: Dict[str, Any]) -> None:
        self._dispatch("c2c_msg_reject", models.C2CManageEvent.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_c2c_msg_receive(self, payload: Dict[str, Any]) -> None:
        self._dispatch("c2c_msg_receive", models.C2CManageEvent.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_subscribe_message_status(self, payload: Dict[str, Any]) -> None:
        self._dispatch("subscribe_message_status", models.SubscribeMessageStatusEvent.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    # interaction / audit / reactions -------------------------------- #
    def parse_interaction_create(self, payload: Dict[str, Any]) -> None:
        self._dispatch("interaction_create", models.Interaction.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_message_audit_pass(self, payload: Dict[str, Any]) -> None:
        self._dispatch("message_audit_pass", models.MessageAudit.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_message_audit_reject(self, payload: Dict[str, Any]) -> None:
        self._dispatch("message_audit_reject", models.MessageAudit.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_message_reaction_add(self, payload: Dict[str, Any]) -> None:
        self._dispatch("message_reaction_add", models.Reaction.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_message_reaction_remove(self, payload: Dict[str, Any]) -> None:
        self._dispatch("message_reaction_remove", models.Reaction.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    # audio / forum --------------------------------------------------- #
    def parse_audio_start(self, payload: Dict[str, Any]) -> None:
        self._dispatch("audio_start", models.AudioAction.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_audio_finish(self, payload: Dict[str, Any]) -> None:
        self._dispatch("audio_finish", models.AudioAction.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_audio_on_mic(self, payload: Dict[str, Any]) -> None:
        self._dispatch("audio_on_mic", models.AudioAction.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_audio_off_mic(self, payload: Dict[str, Any]) -> None:
        self._dispatch("audio_off_mic", models.AudioAction.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_audio_or_live_channel_member_enter(self, payload: Dict[str, Any]) -> None:
        self._dispatch("audio_or_live_channel_member_enter", models.PublicAudio.from_payload(self.api, payload.get("d", {})))

    def parse_audio_or_live_channel_member_exit(self, payload: Dict[str, Any]) -> None:
        self._dispatch("audio_or_live_channel_member_exit", models.PublicAudio.from_payload(self.api, payload.get("d", {})))

    def parse_forum_thread_create(self, payload: Dict[str, Any]) -> None:
        self._dispatch("forum_thread_create", models.ForumThread.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_forum_thread_update(self, payload: Dict[str, Any]) -> None:
        self._dispatch("forum_thread_update", models.ForumThread.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_forum_thread_delete(self, payload: Dict[str, Any]) -> None:
        self._dispatch("forum_thread_delete", models.ForumThread.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_forum_post_create(self, payload: Dict[str, Any]) -> None:
        self._dispatch("forum_post_create", payload.get("d", {}))

    def parse_forum_post_delete(self, payload: Dict[str, Any]) -> None:
        self._dispatch("forum_post_delete", payload.get("d", {}))

    def parse_forum_reply_create(self, payload: Dict[str, Any]) -> None:
        self._dispatch("forum_reply_create", payload.get("d", {}))

    def parse_forum_reply_delete(self, payload: Dict[str, Any]) -> None:
        self._dispatch("forum_reply_delete", payload.get("d", {}))

    def parse_forum_publish_audit_result(self, payload: Dict[str, Any]) -> None:
        self._dispatch("forum_publish_audit_result", payload.get("d", {}))

    def parse_open_forum_thread_create(self, payload: Dict[str, Any]) -> None:
        self._dispatch("open_forum_thread_create", models.OpenForumThread.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_open_forum_thread_update(self, payload: Dict[str, Any]) -> None:
        self._dispatch("open_forum_thread_update", models.OpenForumThread.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_open_forum_thread_delete(self, payload: Dict[str, Any]) -> None:
        self._dispatch("open_forum_thread_delete", models.OpenForumThread.from_payload(self.api, payload.get("id"), payload.get("d", {})))

    def parse_open_forum_post_create(self, payload: Dict[str, Any]) -> None:
        self._dispatch("open_forum_post_create", payload.get("d", {}))

    def parse_open_forum_post_delete(self, payload: Dict[str, Any]) -> None:
        self._dispatch("open_forum_post_delete", payload.get("d", {}))

    def parse_open_forum_reply_create(self, payload: Dict[str, Any]) -> None:
        self._dispatch("open_forum_reply_create", payload.get("d", {}))

    def parse_open_forum_reply_delete(self, payload: Dict[str, Any]) -> None:
        self._dispatch("open_forum_reply_delete", payload.get("d", {}))
