# log_setup.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(log_file: str = "bot.log") -> logging.Logger:
    """
    Sets up rotating file logging for:
      - your app logs
      - slack_bolt logs
      - slack_sdk logs
    Returns a logger you can use directly: logging.getLogger("app")
    """
    log_path = Path(log_file).resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Root logger
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Avoid duplicate handlers if you restart in same interpreter/session
    if not root.handlers:
        handler = RotatingFileHandler(
            log_path,
            maxBytes=2_000_000,   # 2MB
            backupCount=5,
            encoding="utf-8",
        )
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        handler.setFormatter(formatter)
        root.addHandler(handler)

    # Make sure Slack libraries also log into the same file
    logging.getLogger("slack_bolt").setLevel(logging.INFO)
    logging.getLogger("slack_sdk").setLevel(logging.INFO)

    return logging.getLogger("app")