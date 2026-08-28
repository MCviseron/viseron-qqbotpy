"""Helpers for the #子频道 jump syntax used in QQ messages."""

from __future__ import annotations

import re
from typing import List, Tuple

__all__ = ["escape_channel_jump", "parse_channel_jump"]

_JUMP_RE = re.compile(r"<#([^>]+)>")


def escape_channel_jump(channel_id: str) -> str:
    """Wrap a channel id in the jump syntax."""
    return f"<#{channel_id}>"


def parse_channel_jump(content: str) -> List[Tuple[str, str]]:
    """Return (raw, channel_id) pairs found in message content."""
    return [(match.group(0), match.group(1)) for match in _JUMP_RE.finditer(content)]
