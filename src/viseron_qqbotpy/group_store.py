"""Local group membership store.

The SDK can maintain a small groups.json file so a bot remembers which groups
it has joined.  Records are updated from gateway events; inactive records are
kept for a configurable number of days and then removed.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

__all__ = ["GroupStore", "load_group_store"]

_DEFAULT_TIMEZONE = timezone(timedelta(hours=8))


def _now_iso() -> str:
    return datetime.now(_DEFAULT_TIMEZONE).isoformat()


class GroupStore:
    """Persist group membership data to a local JSON file.

    Parameters:
        path:
            JSON file path.  Defaults to ./groups.json.
        inactive_retention_days:
            How many days an inactive (removed) group record is kept before
            being deleted.
    """

    def __init__(self, path: str = "groups.json", *, inactive_retention_days: int = 30) -> None:
        self.path = Path(path)
        self.inactive_retention_days = inactive_retention_days
        self.data: Dict[str, Any] = {"version": 1, "groups": {}}

    def load(self) -> "GroupStore":
        if self.path.exists():
            try:
                loaded = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict) and isinstance(loaded.get("groups"), dict):
                    self.data = loaded
            except (json.JSONDecodeError, OSError):
                self.data = {"version": 1, "groups": {}}
        else:
            self.save()

        self.cleanup_stale_inactive_groups()
        return self

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @property
    def groups(self) -> Dict[str, Dict[str, Any]]:
        return self.data.setdefault("groups", {})

    def get(self, group_openid: str) -> Optional[Dict[str, Any]]:
        return self.groups.get(group_openid)

    def all_active_group_openids(self) -> List[str]:
        return [
            group_openid
            for group_openid, group in self.groups.items()
            if group.get("active", True)
        ]

    def add_group(
        self,
        group_openid: str,
        *,
        added_by: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> None:
        now = _now_iso()
        group = self.groups.setdefault(
            group_openid,
            {
                "group_openid": group_openid,
                "active": True,
            },
        )

        group["active"] = True
        group["group_openid"] = group_openid
        group["added_at"] = timestamp or group.get("added_at") or now
        if added_by is not None:
            group["added_by"] = added_by
        group["last_seen"] = now
        group.pop("removed_at", None)
        self.save()

    def ensure_group(self, group_openid: str) -> None:
        group = self.groups.get(group_openid)
        if group is None or not group.get("active", True):
            self.add_group(group_openid)
            return

        group["last_seen"] = _now_iso()
        self.save()

    def update_group_info(self, group_openid: str, info: Dict[str, Any]) -> None:
        group = self.groups.setdefault(
            group_openid,
            {"group_openid": group_openid, "active": True},
        )
        # 保存平台返回的完整群信息，不额外生成重复别名。
        group.update(info)
        group["group_openid"] = group_openid
        group["last_seen"] = _now_iso()
        self.save()

    def remove_group(self, group_openid: str) -> None:
        group = self.groups.get(group_openid)
        if group is None:
            group = self.groups[group_openid] = {"group_openid": group_openid}
        group["active"] = False
        group["removed_at"] = _now_iso()
        group["last_seen"] = group["removed_at"]
        self.save()

    def cleanup_stale_inactive_groups(self) -> None:
        cutoff = datetime.now(_DEFAULT_TIMEZONE) - timedelta(days=self.inactive_retention_days)
        for group_openid in list(self.groups):
            group = self.groups[group_openid]
            if group.get("active", True):
                continue

            removed_at = group.get("removed_at")
            if not removed_at:
                continue

            try:
                removed_dt = datetime.fromisoformat(removed_at)
            except ValueError:
                continue

            if removed_dt < cutoff:
                del self.groups[group_openid]

        self.save()


def load_group_store(
    path: str = "groups.json",
    *,
    inactive_retention_days: int = 30,
) -> GroupStore:
    """Create and load a GroupStore instance."""
    return GroupStore(path=path, inactive_retention_days=inactive_retention_days).load()
