# structured_logger.py
import os
import random
from datetime import datetime
from typing import Any, Dict, Optional
from pymongo import MongoClient
from services.mongo_service import get_tracker
from services.llm_service import get_reaction_emoji


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


def install_structured_message_logging(app, client, cfg=None, log_file: str = None):
    """
    Installs a Bolt event handler that saves messages to MongoDB,
    organized by workspace and channel. Also optionally adds emoji reactions via LLM.
    """
    mongo_client = MongoClient(os.getenv("MONGO_URI"))
    db = mongo_client["vibecheck"]
    installations_col = db["installations"]
    cache = SlackNameCache(client)

    @app.event("message")
    def _on_message(event, body):
        team_id = (
            body.get("team_id")
            or (body.get("authorizations") or [{}])[0].get("team_id")
            or None
        )

        channel_id = event.get("channel")
        user_id = event.get("user")

        # Look up team name to use as collection name
        team_name = None
        if team_id:
            record = installations_col.find_one({"team_id": team_id})
            if record:
                team_name = record.get("team_name")
        collection_name = f"messages_{team_name}" if team_name else f"messages_{team_id or 'unknown'}"
        messages_col = db[collection_name]

        row = {
            "ingested_at_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "team_id": team_id,
            "channel_id": channel_id,
            "channel_name": cache.channel_name(channel_id),
            "user_id": user_id,
            "user_name": cache.user_name(user_id),
            "ts": event.get("ts"),
            "thread_ts": event.get("thread_ts"),
            "subtype": event.get("subtype"),
            "text": event.get("text"),
        }

        try:
            messages_col.insert_one(row)
        except Exception as e:
            print(f"[LOGGER] Failed to save message to MongoDB: {e}")

        # Count this as a response to the active prompt in this channel,
        # but only for real user messages (not bot posts or subtypes).
        # Exclude bot_id to skip reactions on messages from bots (including this bot)
        if user_id and not event.get("subtype") and not event.get("bot_id"):
            tracker = get_tracker()
            if tracker and team_id:
                tracker.record_response(channel_id, team_id)
            
            # Add LLM-generated emoji reaction (if enabled and probabilistically)
            if cfg and cfg.llm_reactions_enabled:
                if random.random() < cfg.llm_reactions_probability:
                    text = event.get("text") or ""
                    timestamp = event.get("ts")
                    # Validate we have both text and timestamp before calling LLM
                    if text and timestamp:
                        emoji = get_reaction_emoji(text)
                        if emoji:
                            try:
                                client.reactions_add(
                                    channel=channel_id,
                                    timestamp=timestamp,
                                    name=emoji
                                )
                                print(f"[REACTION] Added emoji :{emoji}: to message in {cache.channel_name(channel_id)}")
                            except Exception as e:
                                print(f"[REACTION] Failed to add emoji reaction ({emoji}): {e}")

        # check + announce streaks for real user messages
        if user_id and not bot_id and channel_id:
            try:
                from services.streak_service import check_and_announce_streak
                check_and_announce_streak(user_id, cache.user_name(user_id) or user_id, client, channel_id)
            except Exception as e:
                print(f"[streaks] {e}")

    return logger
