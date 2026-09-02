"""viseron-qqbotpy: a modern QQ Open Platform bot SDK.

The package exposes the main Client, Intents, event models and exceptions.
"""

from .client import Client
from .api import BotAPI
from .env import load_env
from .http import HTTPClient, Route
from .token import AccessToken, TokenManager
from .flags import Intents, Permission
from .group_store import GroupStore, load_group_store
from .panel import Panel, PanelItem, PanelStore, load_panels
from .errors import (
    APIError,
    AuthenticationFailedError,
    ForbiddenError,
    MethodNotAllowedError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TokenError,
    ViseronError,
    WebSocketError,
)
from .models import (
    AudioAction,
    C2CManageEvent,
    C2CMessage,
    Channel,
    DirectMessage,
    ForumThread,
    GroupJoinRequestEvent,
    GroupManageEvent,
    GroupMemberEvent,
    GroupMessage,
    Guild,
    Interaction,
    Member,
    Message,
    MessageAudit,
    OpenForumThread,
    PublicAudio,
    Reaction,
    SubscribeMessageStatusEvent,
    User,
)
from .logging import configure_logging, get_logger

__all__ = [
    "APIError",
    "AccessToken",
    "AudioAction",
    "BotAPI",
    "AuthenticationFailedError",
    "C2CManageEvent",
    "C2CMessage",
    "Channel",
    "Client",
    "DirectMessage",
    "ForbiddenError",
    "ForumThread",
    "GroupJoinRequestEvent",
    "GroupManageEvent",
    "GroupMemberEvent",
    "GroupMessage",
    "GroupStore",
    "Guild",
    "Intents",
    "HTTPClient",
    "Interaction",
    "load_env",
    "Member",
    "Message",
    "MessageAudit",
    "MethodNotAllowedError",
    "NotFoundError",
    "OpenForumThread",
    "Panel",
    "PanelItem",
    "PanelStore",
    "Permission",
    "PublicAudio",
    "RateLimitError",
    "Reaction",
    "Route",
    "ServerError",
    "SubscribeMessageStatusEvent",
    "TokenError",
    "TokenManager",
    "User",
    "ViseronError",
    "WebSocketError",
    "configure_logging",
    "get_logger",
    "load_group_store",
    "load_panels",
]

__version__ = "0.2.0"
