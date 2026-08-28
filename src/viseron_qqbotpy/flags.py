"""Intents and permission flag containers.

The gateway uses bit flags to subscribe to events.  The values below follow
the current API v2 documentation.
"""

from __future__ import annotations

from typing import Any, ClassVar, Dict, Iterator, Tuple, Type, TypeVar

__all__ = ["Intents", "Permission"]

BF = TypeVar("BF", bound="BaseFlags")


class Flag:
    """Descriptor that represents one bit in a :class:`BaseFlags` subclass."""

    def __init__(self, func):
        self.flag = func(None)
        self.__doc__ = func.__doc__

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.has_flag(self.flag)

    def __set__(self, instance, value: bool) -> None:
        instance.set_flag(self.flag, value)

    def __repr__(self) -> str:
        return f"<Flag value={self.flag}>"


class BaseFlags:
    value: int
    VALID_FLAGS: ClassVar[Dict[str, int]]
    DEFAULT_VALUE: ClassVar[int] = 0

    __slots__ = ("value",)

    def __init__(self, **kwargs: bool) -> None:
        self.value = self.DEFAULT_VALUE
        for key, value in kwargs.items():
            if key not in self.VALID_FLAGS:
                raise TypeError(f"{key!r} is not a valid flag name.")
            self.set_flag(self.VALID_FLAGS[key], value)

    @classmethod
    def _from_value(cls, value: int):
        self = cls.__new__(cls)
        self.value = value
        return self

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.value == other.value

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.value)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} value={self.value}>"

    def __iter__(self) -> Iterator[Tuple[str, bool]]:
        for name, value in self.VALID_FLAGS.items():
            yield name, self.has_flag(value)

    def has_flag(self, bit: int) -> bool:
        return (self.value & bit) == bit

    def set_flag(self, bit: int, toggle: bool) -> None:
        if toggle is True:
            self.value |= bit
        elif toggle is False:
            self.value &= ~bit
        else:
            raise TypeError(f"Value to set for {self.__class__.__name__} must be a bool.")


def _collect_flags(cls: Type[BF]) -> Type[BF]:
    cls.VALID_FLAGS = {
        name: desc.flag
        for name, desc in cls.__dict__.items()
        if isinstance(desc, Flag)
    }
    return cls


@_collect_flags
class Intents(BaseFlags):
    """Gateway event subscription flags.

    Use :meth:`Intents.default` for public-domain bots and
    :meth:`Intents.all` when the bot has private-domain permissions.
    """

    __slots__ = ()

    @classmethod
    def all(cls) -> "Intents":
        """Enable every known intent."""
        self = cls.none()
        for name in self.VALID_FLAGS:
            self.set_flag(self.VALID_FLAGS[name], True)
        return self

    @classmethod
    def none(cls) -> "Intents":
        """Disable every intent."""
        self = cls.__new__(cls)
        self.value = 0
        return self

    @classmethod
    def default(cls) -> "Intents":
        """Enable public-domain intents.

        Private-domain intents (guild_messages and forums) are left off.
        """
        self = cls.all()
        self.guild_messages = False
        self.forums = False
        return self

    @Flag
    def guilds(self) -> int:
        """GUILD_CREATE / GUILD_UPDATE / GUILD_DELETE / CHANNEL_*."""
        return 1 << 0

    @Flag
    def guild_members(self) -> int:
        """GUILD_MEMBER_ADD / GUILD_MEMBER_UPDATE / GUILD_MEMBER_REMOVE."""
        return 1 << 1

    @Flag
    def guild_messages(self) -> int:
        """MESSAGE_CREATE / MESSAGE_DELETE. Private-domain only."""
        return 1 << 9

    @Flag
    def guild_message_reactions(self) -> int:
        """MESSAGE_REACTION_ADD / MESSAGE_REACTION_REMOVE."""
        return 1 << 10

    @Flag
    def direct_message(self) -> int:
        """DIRECT_MESSAGE_CREATE / DIRECT_MESSAGE_DELETE."""
        return 1 << 12

    @Flag
    def open_forum_event(self) -> int:
        """Open forum thread/post events."""
        return 1 << 18

    @Flag
    def audio_or_live_channel_member(self) -> int:
        """Audio/live channel member enter/exit events."""
        return 1 << 19

    @Flag
    def group_and_c2c_event(self) -> int:
        """Group and C2C events, including group member changes."""
        return 1 << 25

    @Flag
    def interaction(self) -> int:
        """INTERACTION_CREATE."""
        return 1 << 26

    @Flag
    def message_audit(self) -> int:
        """MESSAGE_AUDIT_PASS / MESSAGE_AUDIT_REJECT."""
        return 1 << 27

    @Flag
    def forums(self) -> int:
        """Forum events. Private-domain only."""
        return 1 << 28

    @Flag
    def audio_action(self) -> int:
        """AUDIO_START / AUDIO_FINISH / AUDIO_ON_MIC / AUDIO_OFF_MIC."""
        return 1 << 29

    @Flag
    def public_guild_messages(self) -> int:
        """AT_MESSAGE_CREATE / PUBLIC_MESSAGE_DELETE."""
        return 1 << 30


@_collect_flags
class Permission(BaseFlags):
    """Sub-channel permission bits used by the channel permission APIs."""

    __slots__ = ()

    @Flag
    def view_permission(self) -> int:
        """Can view the channel."""
        return 1 << 0

    @Flag
    def manager_permission(self) -> int:
        """Can manage the channel."""
        return 1 << 1

    @Flag
    def speak_permission(self) -> int:
        """Can speak in the channel."""
        return 1 << 2

    @Flag
    def live_permission(self) -> int:
        """Can start a live stream in the channel."""
        return 1 << 3
