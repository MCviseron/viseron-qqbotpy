"""Optional APScheduler integration."""

from __future__ import annotations

from typing import Any

__all__ = ["create_scheduler"]


def create_scheduler(**kwargs: Any):
    """Create an AsyncIOScheduler.

    APScheduler is an optional dependency: pip install viseron-qqbotpy[ext]
    """
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
    except ImportError as exc:  # pragma: no cover
        raise ImportError("scheduler support requires APScheduler; install viseron-qqbotpy[ext]") from exc

    return AsyncIOScheduler(**kwargs)
