"""Tiny YAML config loader used by the examples and extensions."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Union

__all__ = ["load_yaml"]


def load_yaml(path: Union[str, Path]) -> Dict[str, Any]:
    """Load a YAML file into a dict.

    Raises ImportError with a friendly message when PyYAML is not installed.
    """
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover
        raise ImportError("YAML config support requires PyYAML; install viseron-qqbotpy[ext]") from exc

    path = Path(path)
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"config file {path} must contain a mapping")
    return data
