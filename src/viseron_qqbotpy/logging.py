"""Logging support for viseron-qqbotpy.

The SDK configures its own logger automatically on first use:

* console output uses the project's default coloured format
* a rotating log file is written to logs/viseron_qqbotpy.log

Applications can override this behaviour with configure_logging().
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

__all__ = ["configure_logging", "get_logger"]

_LOGGER_NAME = "viseron_qqbotpy"
_DEFAULT_LOG_FILE = "logs/viseron_qqbotpy.log"

_CONSOLE_FORMAT = (
    "\033[33m[%(levelname)s]    (%(filename)s:%(lineno)d)%(funcName)s\033[0m    "
    "\033[37m%(message)s\033[0m"
)
_FILE_FORMAT = "[%(levelname)s]    (%(filename)s:%(lineno)d)%(funcName)s    %(message)s"

_configured = False


def get_logger(name: str = _LOGGER_NAME) -> logging.Logger:
    """Return a logger.

    When name is an SDK logger, the default SDK logging setup is applied on
    first use.  Non-SDK names are returned unchanged.
    """
    if name == _LOGGER_NAME or name.startswith(_LOGGER_NAME + "."):
        _ensure_default_config()
    return logging.getLogger(name)


def configure_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    console_format: Optional[str] = None,
    file_format: Optional[str] = None,
    use_console: bool = True,
    use_file: bool = True,
) -> logging.Logger:
    """Configure the SDK logger.

    Parameters:
        level:
            Log level for the SDK logger.
        log_file:
            Log file path.  Defaults to logs/viseron_qqbotpy.log.
        console_format:
            Optional custom console format.  When None, the SDK default is used.
        file_format:
            Optional custom file format.  When None, the SDK default is used.
        use_console:
            Set False to disable console output.
        use_file:
            Set False to disable file logging.

    This function can be called before or after the first SDK log record.
    It replaces any previously installed SDK handlers.
    """
    global _configured
    _configured = True
    return _apply_config(
        level=level,
        log_file=log_file or _DEFAULT_LOG_FILE,
        console_format=console_format or _CONSOLE_FORMAT,
        file_format=file_format or _FILE_FORMAT,
        use_console=use_console,
        use_file=use_file,
    )


def _ensure_default_config() -> None:
    global _configured
    if _configured:
        return
    _configured = True
    _apply_config()


def _apply_config(
    level: int = logging.INFO,
    log_file: str = _DEFAULT_LOG_FILE,
    console_format: str = _CONSOLE_FORMAT,
    file_format: str = _FILE_FORMAT,
    use_console: bool = True,
    use_file: bool = True,
) -> logging.Logger:
    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(level)
    logger.propagate = False

    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    if use_console:
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter(console_format))
        logger.addHandler(console)

    if use_file:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            path,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(logging.Formatter(file_format))
        logger.addHandler(file_handler)

    return logger
