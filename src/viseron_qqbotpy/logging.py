"""Small logging helper shared by the SDK.

Applications that want a custom format can configure the
"viseron_qqbotpy" logger themselves.  The library never calls basicConfig.
"""

from __future__ import annotations

import logging

__all__ = ["get_logger"]

_LOGGER_NAME = "viseron_qqbotpy"


def get_logger(name: str = _LOGGER_NAME) -> logging.Logger:
    return logging.getLogger(name)
