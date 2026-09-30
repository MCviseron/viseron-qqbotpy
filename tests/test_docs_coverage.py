"""Keep docs/api-reference.md in sync with the BotAPI surface.

Every public coroutine on BotAPI must be mentioned in the API reference, so a
newly added endpoint cannot silently ship undocumented.  The reverse direction
is checked too: a documented name that no longer exists is a stale doc.
"""

from __future__ import annotations

import inspect
import re
from pathlib import Path

from viseron_qqbotpy.api import BotAPI

DOCS = Path(__file__).resolve().parents[1] / "docs" / "api-reference.md"


def _public_api_names() -> set:
    names = set()
    for name, member in inspect.getmembers(BotAPI, predicate=inspect.isfunction):
        if name.startswith("_"):
            continue
        names.add(name)
    return names


def _documented_names(text: str) -> set:
    return set(re.findall(r"^\s*-\s+([a-z_][a-z0-9_]*)\s*\(", text, flags=re.MULTILINE))


def test_every_api_method_is_documented():
    text = DOCS.read_text(encoding="utf-8")
    documented = _documented_names(text)
    missing = sorted(_public_api_names() - documented)
    assert not missing, f"BotAPI methods missing from docs/api-reference.md: {missing}"


def test_no_documented_method_is_missing_from_api():
    text = DOCS.read_text(encoding="utf-8")
    documented = _documented_names(text)
    unknown = sorted(documented - _public_api_names())
    assert not unknown, f"docs/api-reference.md documents unknown methods: {unknown}"


def test_readme_feature_list_mentions_group_member_management():
    readme = (DOCS.parents[1] / "README.md").read_text(encoding="utf-8")
    assert "群成员管理" in readme
