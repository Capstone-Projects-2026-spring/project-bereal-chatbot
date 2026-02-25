# slack_event_logger.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_slack_logger(
    log_dir: str = ".",
    filename: str = "slack_events.log",
    level: int = logging.INFO,
) -> logging.Logger:
    log_path = Path(log_dir).resolve()
    log_path.mkdir(parents=True, exist_ok=True)
    full_log_file = log_path / filename

    logger = logging.getLogger("slack_events")
    logger.setLevel(level)
    logger.propagate = False

    if not any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
        handler = RotatingFileHandler(
            full_log_file,
            maxBytes=2_000_000,
            backupCount=5,
            encoding="utf-8",
        )
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def install_message_event_logging(app, logger: Optional[logging.Logger] = None):
    if logger is None:
        logger = setup_slack_logger()

    # Helpful: log that the logger was installed (so you know the file is wired up)
    logger.info("Installed Slack message event logger listener")

    @app.event("message")
    def _log_all_messages(event, body, logger=logger):
        team_id = (
            body.get("team_id")
            or (body.get("authorizations") or [{}])[0].get("team_id")
            or "unknown_team"
        )

        channel = event.get("channel", "unknown_channel")
        user = event.get("user", "unknown_user")  # bot messages may not have "user"
        bot_id = event.get("bot_id", "")
        subtype = event.get("subtype", "")
        text = event.get("text", "")
        ts = event.get("ts", "")
        thread_ts = event.get("thread_ts", "")

        safe_text = " ".join((text or "").split())

        logger.info(
            "team=%s channel=%s user=%s bot_id=%s subtype=%s ts=%s thread_ts=%s text=%s",
            team_id, channel, user, bot_id, subtype, ts, thread_ts, safe_text
        )

    # OPTIONAL but super useful for debugging: log any unhandled events too
    @app.middleware  # logs every incoming request body type
    def _log_event_type(next, body, logger=logger):
        event_type = (body.get("event") or {}).get("type", "no_event")
        logger.info("incoming_event_type=%s", event_type)
        return next()

    return logger