"""Minimal command decorator for message content.

Example::

    from viseron_qqbotpy.ext import Commands

    @Commands("ping", "pong")
    async def ping(self, message, params):
        await message.reply(content="pong")
"""

from __future__ import annotations

import shlex
from functools import wraps
from typing import Any, Callable, List, Optional, Sequence, Union

__all__ = ["Commands", "command"]


def _split(content: str) -> List[str]:
    try:
        return shlex.split(content)
    except ValueError:
        return content.split()


class Commands:
    """Decorator that invokes a handler when a message starts with a command."""

    def __init__(self, *names: str, prefix: str = "/") -> None:
        if not names:
            raise ValueError("at least one command name is required")
        self.names = tuple(names)
        self.prefix = prefix

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(instance: Any, message: Any, *args: Any, **kwargs: Any) -> Any:
            content = getattr(message, "content", None) or ""
            parts = _split(content.strip())
            if not parts:
                return None
            first = parts[0]
            matched = False
            for name in self.names:
                if first == self.prefix + name or first == name:
                    matched = True
                    break
            if not matched:
                return None
            params = parts[1:]
            return await func(instance, message, params, *args, **kwargs)

        wrapper.command_names = self.names  # type: ignore[attr-defined]
        wrapper.command_prefix = self.prefix  # type: ignore[attr-defined]
        return wrapper


def command(*names: str, prefix: str = "/") -> Commands:
    """Functional alias for :class:`Commands`."""
    return Commands(*names, prefix=prefix)
