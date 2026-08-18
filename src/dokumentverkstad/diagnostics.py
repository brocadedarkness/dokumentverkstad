from __future__ import annotations

from logging import Formatter, INFO, Logger, getLogger
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Callable


def runtime_log_path(runtime_root: str | Path) -> Path:
    return Path(runtime_root) / "logs" / "dokumentverkstad.log"


def configure_runtime_logger(runtime_root: str | Path) -> Logger:
    path = runtime_log_path(runtime_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    logger = getLogger("dokumentverkstad.runtime")
    logger.setLevel(INFO)
    logger.propagate = False
    if not any(
        isinstance(handler, RotatingFileHandler)
        and Path(handler.baseFilename) == path.resolve()
        for handler in logger.handlers
    ):
        handler = RotatingFileHandler(
            path,
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        handler.setFormatter(Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
    return logger


def runtime_log_sink(
    runtime_root: str | Path, terminal: Callable[[str], None] | None = print
) -> Callable[[str], None]:
    logger = configure_runtime_logger(runtime_root)

    def log(message: str) -> None:
        if terminal:
            terminal(message)
        logger.info(message)

    return log
