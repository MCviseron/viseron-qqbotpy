"""High-level instruction panel management.

Panel provides an object-oriented wrapper around the /v2/panels endpoints.
PanelStore adds local config persistence and startup synchronisation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .api import BotAPI
from .errors import APIError

__all__ = ["Panel", "PanelItem", "PanelStore", "load_panels"]


@dataclass
class PanelItem:
    """One command or link item inside a panel."""

    type: str
    name: str
    desc: str = ""
    only_admin: bool = False
    url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "type": self.type,
            "name": self.name,
            "desc": self.desc,
            "only_admin": self.only_admin,
        }
        if self.url is not None:
            data["url"] = self.url
        return data


class Panel:
    """A single instruction panel."""

    def __init__(self, api: BotAPI, data: Optional[Dict[str, Any]] = None) -> None:
        self.api = api
        self.panel_id: Optional[str] = None
        self.scope: Optional[str] = None
        self.target_type: Optional[str] = None
        self.items: List[Dict[str, Any]] = []
        self.remark: str = ""
        self.user_openids: List[str] = []
        self.group_openids: List[str] = []
        self.created_at: Optional[str] = None
        self.updated_at: Optional[str] = None
        self.version: Optional[int] = None

        if data is not None:
            self._apply_data(data)

    def _apply_data(self, data: Dict[str, Any]) -> None:
        self.panel_id = data.get("panel_id")
        self.scope = data.get("scope")
        self.target_type = data.get("target_type")
        panel = data.get("panel") or {}
        self.items = panel.get("items") or []
        self.remark = panel.get("remark") or ""
        self.user_openids = data.get("user_openids") or []
        self.group_openids = data.get("group_openids") or []
        self.created_at = data.get("created_at")
        self.updated_at = data.get("updated_at")
        self.version = data.get("version")

    @classmethod
    async def create(
        cls,
        api: BotAPI,
        scope: str,
        target_type: str = "all",
        *,
        items: Optional[List[Dict[str, Any]]] = None,
        remark: str = "",
        user_openids: Optional[List[str]] = None,
        group_openids: Optional[List[str]] = None,
    ) -> "Panel":
        payload: Dict[str, Any] = {
            "scope": scope,
            "target_type": target_type,
            "panel": {"items": items or [], "remark": remark},
        }
        if user_openids:
            payload["user_openids"] = user_openids
        if group_openids:
            payload["group_openids"] = group_openids

        result = await api.create_panel(**payload)

        panel = cls(api)
        panel.panel_id = result.get("panel_id")
        panel.scope = scope
        panel.target_type = target_type
        panel.items = items or []
        panel.remark = remark
        panel.user_openids = user_openids or []
        panel.group_openids = group_openids or []
        return panel

    @classmethod
    async def get(cls, api: BotAPI, panel_id: str) -> "Panel":
        data = await api.get_panel(panel_id)
        return cls(api, data)

    def add_command(self, name: str, *, desc: str = "", only_admin: bool = False) -> None:
        self.items.append(
            PanelItem(type="command", name=name, desc=desc, only_admin=only_admin).to_dict()
        )

    def add_link(
        self,
        name: str,
        *,
        desc: str = "",
        url: str,
        only_admin: bool = False,
    ) -> None:
        self.items.append(
            PanelItem(type="link", name=name, desc=desc, url=url, only_admin=only_admin).to_dict()
        )

    async def save(self) -> None:
        result = await self.api.update_panel(
            panel_id=self.panel_id,
            panel={"items": self.items, "remark": self.remark},
        )
        if isinstance(result, dict) and result.get("version") is not None:
            self.version = result["version"]

    async def delete(self) -> None:
        await self.api.delete_panel(self.panel_id)

    async def add_targets(
        self,
        *,
        users: Optional[List[str]] = None,
        groups: Optional[List[str]] = None,
    ) -> None:
        payload: Dict[str, Any] = {"op": "add"}
        if users:
            payload["user_openids"] = users
        if groups:
            payload["group_openids"] = groups
        await self.api.update_panel_target(panel_id=self.panel_id, **payload)

        if users:
            for user in users:
                if user not in self.user_openids:
                    self.user_openids.append(user)
        if groups:
            for group in groups:
                if group not in self.group_openids:
                    self.group_openids.append(group)

    async def remove_targets(
        self,
        *,
        users: Optional[List[str]] = None,
        groups: Optional[List[str]] = None,
    ) -> None:
        payload: Dict[str, Any] = {"op": "del"}
        if users:
            payload["user_openids"] = users
        if groups:
            payload["group_openids"] = groups
        await self.api.update_panel_target(panel_id=self.panel_id, **payload)

        if users:
            self.user_openids = [u for u in self.user_openids if u not in users]
        if groups:
            self.group_openids = [g for g in self.group_openids if g not in groups]

    async def refresh(self) -> None:
        data = await self.api.get_panel(self.panel_id)
        self._apply_data(data)


class PanelStore:
    """Load panel config from panels/panels.json and sync it to the platform.

    panels/store.json is maintained automatically and stores the mapping from
    scope:key to platform panel_id.
    """

    def __init__(self, api: BotAPI, root_dir: str = "panels") -> None:
        self.api = api
        self.root_dir = Path(root_dir)
        self.config_path = self.root_dir / "panels.json"
        self.store_path = self.root_dir / "store.json"
        self.store: Dict[str, Any] = {"version": 1, "panels": {}}

    def load(self) -> "PanelStore":
        self.root_dir.mkdir(parents=True, exist_ok=True)

        if not self.config_path.exists():
            self.config_path.write_text(
                json.dumps({}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        if self.store_path.exists():
            try:
                loaded = json.loads(self.store_path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict) and isinstance(loaded.get("panels"), dict):
                    self.store = loaded
            except (json.JSONDecodeError, OSError):
                self.store = {"version": 1, "panels": {}}
        else:
            self.save_store()

        return self

    def save_store(self) -> None:
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.store_path.write_text(
            json.dumps(self.store, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _read_config(self) -> Dict[str, Any]:
        try:
            loaded = json.loads(self.config_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
        return loaded if isinstance(loaded, dict) else {}

    def _config_items(self, config_value: Any) -> List[Dict[str, Any]]:
        if isinstance(config_value, list):
            return [item for item in config_value if isinstance(item, dict)]
        if isinstance(config_value, dict):
            return [config_value]
        return []

    async def _find_existing_panel(
        self,
        scope: str,
        target_type: str,
        remark: str,
    ) -> Optional[Panel]:
        panels = await self.api.get_panels(scope)
        if not isinstance(panels, list):
            return None

        for summary in panels:
            if not isinstance(summary, dict):
                continue
            if summary.get("scope") != scope:
                continue
            if target_type and summary.get("target_type") != target_type:
                continue
            if remark and summary.get("panel", {}).get("remark") != remark:
                continue
            panel_id = summary.get("panel_id")
            if panel_id:
                try:
                    return await Panel.get(self.api, panel_id)
                except APIError:
                    continue

        return None

    async def sync_from_config(self) -> None:
        self.load()
        config = self._read_config()

        for scope, config_value in config.items():
            for item in self._config_items(config_value):
                key = item.get("key", "default")
                target_type = item.get("target_type", "all")
                remark = item.get("remark", key)
                items = item.get("items") or []
                user_openids = item.get("user_openids") or []
                group_openids = item.get("group_openids") or []

                panel_id = self.store.setdefault("panels", {}).get(f"{scope}:{key}")
                panel: Optional[Panel] = None

                if panel_id:
                    try:
                        panel = await Panel.get(self.api, panel_id)
                    except APIError:
                        panel = None

                if panel is None:
                    panel = await self._find_existing_panel(scope, target_type, remark)

                if panel is None:
                    panel = await Panel.create(
                        self.api,
                        scope=scope,
                        target_type=target_type,
                        items=items,
                        remark=remark,
                        user_openids=user_openids,
                        group_openids=group_openids,
                    )
                    self.store["panels"][f"{scope}:{key}"] = panel.panel_id
                    self.save_store()
                    continue

                self.store["panels"][f"{scope}:{key}"] = panel.panel_id
                self.save_store()

                if panel.items != items or panel.remark != remark:
                    panel.items = items
                    panel.remark = remark
                    await panel.save()

                if target_type == "specific":
                    add_users = [u for u in user_openids if u not in panel.user_openids]
                    del_users = [u for u in panel.user_openids if u not in user_openids]
                    add_groups = [g for g in group_openids if g not in panel.group_openids]
                    del_groups = [g for g in panel.group_openids if g not in group_openids]

                    if add_users:
                        await panel.add_targets(users=add_users)
                    if del_users:
                        await panel.remove_targets(users=del_users)
                    if add_groups:
                        await panel.add_targets(groups=add_groups)
                    if del_groups:
                        await panel.remove_targets(groups=del_groups)


async def load_panels(api: BotAPI, root_dir: str = "panels") -> PanelStore:
    """Create and load a PanelStore instance."""
    return PanelStore(api, root_dir=root_dir).load()
