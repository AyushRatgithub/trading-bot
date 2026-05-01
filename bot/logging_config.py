"""
logging_config.py – Centralised logging setup.

Writes structured log lines to both the console and a rotating file
(logs/trading_bot.log).  Import ``get_logger`` everywhere; never call
``logging.basicConfig`` in module-level code.
"""

import logging
import logging.handlers
import os

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
LOG_FILE = os.path.join(LOG_DIR, "trading_bot.log")

_CONFIGURED = False


def setup_logging(level: int = logging.DEBUG) -> None:
    """Configure root logger once (idempotent)."""
    global _CONFIGURED
    if _CONFIGURED:
        return
    _CONFIGURED = True

    os.makedirs(LOG_DIR, exist_ok=True)

    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt, datefmt=datefmt)

    root = logging.getLogger()
    root.setLevel(level)

    # --- console handler (INFO+) ---
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    root.addHandler(ch)

    # --- rotating file handler (DEBUG+) ---
    fh = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    root.addHandler(fh)

    # Silence noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger, initialising logging if needed."""
    setup_logging()
    return logging.getLogger(name)
