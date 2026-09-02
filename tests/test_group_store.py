from datetime import datetime, timedelta, timezone

from viseron_qqbotpy.group_store import GroupStore


def test_group_store_creates_file(tmp_path):
    path = tmp_path / "groups.json"
    store = GroupStore(str(path)).load()
    assert path.exists()
    assert store.data["groups"] == {}


def test_add_ensure_and_remove_group(tmp_path):
    path = tmp_path / "groups.json"
    store = GroupStore(str(path)).load()

    store.add_group("group-1", added_by="user-1")
    assert store.get("group-1")["active"] is True
    assert store.all_active_group_openids() == ["group-1"]

    store.ensure_group("group-1")
    assert store.get("group-1")["last_seen"]

    store.remove_group("group-1")
    assert store.get("group-1")["active"] is False
    assert store.all_active_group_openids() == []


def test_cleanup_stale_inactive_groups(tmp_path):
    path = tmp_path / "groups.json"
    store = GroupStore(str(path), inactive_retention_days=30).load()

    store.add_group("old-group")
    store.remove_group("old-group")

    old_time = (datetime.now(timezone.utc) - timedelta(days=31)).isoformat()
    store.get("old-group")["removed_at"] = old_time
    store.save()

    store.cleanup_stale_inactive_groups()
    assert "old-group" not in store.groups
