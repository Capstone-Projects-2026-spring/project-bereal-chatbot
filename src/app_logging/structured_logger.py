# structured_logger.py
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional


def setup_jsonl_logger(
    log_file: str = "slack_messages.jsonl",
    level: int = logging.INFO,
) -> logging.Logger:
    """
    Writes one JSON object per line (JSONL).
    Perfect for piping into pandas / databases.
    """
    log_path = Path(log_file).resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("slack_structured")
    logger.setLevel(level)
    logger.propagate = False

    if not logger.handlers:
        handler = RotatingFileHandler(
            log_path,
            maxBytes=5_000_000,  # 5MB
            backupCount=10,
            encoding="utf-8",
        )
        # We write pure JSON per line (no extra formatter noise)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)

    return logger


class SlackNameCache:
    """
    Caches user/channel lookups to avoid wasting resources.
    """
    def __init__(self, client, ttl_seconds: int = 3600):
        self.client = client
        self.ttl = ttl_seconds
        self._users: Dict[str, Dict[str, Any]] = {}
        self._channels: Dict[str, Dict[str, Any]] = {}

    def _fresh(self, rec: Dict[str, Any]) -> bool:
        return (datetime.utcnow().timestamp() - rec["cached_at"]) < self.ttl

    def user_name(self, user_id: Optional[str]) -> Optional[str]:
        if not user_id:
            return None
        rec = self._users.get(user_id)
        if rec and self._fresh(rec):
            return rec["name"]
        try:
            info = self.client.users_info(user=user_id)
            profile = info["user"].get("profile", {})
            name = (
                profile.get("display_name")
                or profile.get("real_name")
                or info["user"].get("name")
                or user_id
            )
            self._users[user_id] = {"name": name, "cached_at": datetime.utcnow().timestamp()}
            return name
        except Exception:
            self._users[user_id] = {"name": user_id, "cached_at": datetime.utcnow().timestamp()}
            return user_id

    def channel_name(self, channel_id: Optional[str]) -> Optional[str]:
        if not channel_id:
            return None
        rec = self._channels.get(channel_id)
        if rec and self._fresh(rec):
            return rec["name"]
        try:
            info = self.client.conversations_info(channel=channel_id)
            name = info["channel"].get("name") or channel_id
            self._channels[channel_id] = {"name": name, "cached_at": datetime.utcnow().timestamp()}
            return name
        except Exception:
            self._channels[channel_id] = {"name": channel_id, "cached_at": datetime.utcnow().timestamp()}
            return channel_id


def install_structured_message_logging(app, client, log_file: str = "slack_messages.jsonl"):
    """
    Installs a Bolt event handler that writes DB-ready JSONL rows.
    """
    logger = setup_jsonl_logger(log_file=log_file)
    cache = SlackNameCache(client)

    @app.event("message")
    def _on_message(event, body):
        # workspace/team
        team_id = (
            body.get("team_id")
            or (body.get("authorizations") or [{}])[0].get("team_id")
            or None
        )

        channel_id = event.get("channel")
        user_id = event.get("user")
        bot_id = event.get("bot_id")

        row = {
            # ingestion metadata (your system)
            "ingested_at_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",

            # slack ids
            "team_id": team_id,
            "channel_id": channel_id,
            "channel_name": cache.channel_name(channel_id),

            "user_id": user_id,
            "user_name": cache.user_name(user_id),

            "bot_id": bot_id,

            # message fields
            "ts": event.get("ts"),
            "event_ts": body.get("event_id") or body.get("event_time"),  # optional identifiers
            "client_msg_id": event.get("client_msg_id"),
            "subtype": event.get("subtype"),
            "thread_ts": event.get("thread_ts"),

            # content
            "text": event.get("text"),
        }

        # Write as JSON line
        logger.info(json.dumps(row, ensure_ascii=False))

    return logger