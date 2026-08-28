"""Small .env file loader.

Python's os.getenv does **not** read .env files automatically.  Use
load_env() at startup, or pass the values directly as strings.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional, Union

__all__ = ["load_env"]


def load_env(path: Optional[Union[str, Path]] = None, *, override: bool = False) -> Dict[str, str]:
    """Load a simple .env file into os.environ and return the parsed values.

    Both KEY=VALUE and KEY:VALUE lines are accepted.  Quotes around values are
    stripped.  The default path is the current working directory's .env file.

    Parameters:
        path:
            Optional explicit .env path.
        override:
            When False, existing environment variables are kept.  When True,
            values from the file replace existing environment variables.
    """
    env_path = Path(path) if path is not None else Path.cwd() / ".env"
    values: Dict[str, str] = {}

    if not env_path.exists():
        return values

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if "=" in line:
            key, value = line.split("=", 1)
        elif ":" in line:
            key, value = line.split(":", 1)
        else:
            continue

        key = key.strip()
        value = value.strip()
        if not key:
            continue

        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]

        values[key] = value

    for key, value in values.items():
        if override or key not in os.environ:
            os.environ[key] = value

    return values
