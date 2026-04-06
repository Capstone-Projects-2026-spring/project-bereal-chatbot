# src/services/mongo_service.py
from __future__ import annotations

import os
from datetime import datetime, timezone

from pymongo import MongoClient

_tracker: "PromptTracker | None" = None


class PromptTracker:
    """
    Tracks prompt usage in the `vibecheck.prompt_stats` MongoDB collection.

    Each document looks like:
        {
            "prompt_id":       "5",
            "prompt":          "If you had to swap jobs...",
            "tags":            ["work_life"],
            "times_asked":     3,
            "times_responded": 0,
            "last_asked_at":   ISODate(...)
        }
    """

    def __init__(self, mongo_uri: str) -> None:
        client = MongoClient(mongo_uri)
        self._col = client["vibecheck"]["prompt_stats"]
        # Maps (team_id, channel_id) -> prompt_id for the most recently posted prompt
        self._active_prompt: dict[tuple[str, str], str] = {}

    def record_prompt_sent(self, prompt_id: str, prompt_text: str, tags: str, channel: str, team_id: str) -> None:
        """
        Upsert the prompt document for this workspace, increment times_asked,
        and mark this channel's active prompt so responses can be counted.
        """
        tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

        self._col.update_one(
            {"team_id": team_id, "prompt_id": str(prompt_id)},
            {
                "$set": {
                    "prompt": prompt_text,
                    "tags": tag_list,
                    "last_asked_at": datetime.now(timezone.utc),
                },
                "$inc": {"times_asked": 1},
                "$setOnInsert": {"times_responded": 0, "team_id": team_id},
            },
            upsert=True,
        )
        self._active_prompt[(team_id, channel)] = str(prompt_id)

    def record_response(self, channel: str, team_id: str) -> None:
        """
        Increment times_responded for whichever prompt is currently active
        in this channel/workspace. No-op if no prompt has been posted yet.
        """
        prompt_id = self._active_prompt.get((team_id, channel))
        if not prompt_id:
            return
        self._col.update_one(
            {"team_id": team_id, "prompt_id": prompt_id},
            {"$inc": {"times_responded": 1}},
        )

    def get_all_stats(self, team_id: str) -> list[dict]:
        """Return prompt stats for a specific workspace, sorted by times_asked descending."""
        return list(self._col.find({"team_id": team_id}, {"_id": 0}).sort("times_asked", -1))


def init_tracker(mongo_uri: str) -> PromptTracker:
    global _tracker
    _tracker = PromptTracker(mongo_uri)
    return _tracker


def get_tracker() -> PromptTracker | None:
    return _tracker


_mongo_client: MongoClient | None = None


def _get_user_interests_col():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(os.getenv("MONGO_URI"))
    return _mongo_client["vibecheck"]["user_interests"]


def save_user_interests(team_id: str, user_id: str, tags: list[str]) -> None:
    """Upsert the interest tags for a user. Tags are purely cosmetic."""
    col = _get_user_interests_col()
    col.update_one(
        {"team_id": team_id, "user_id": user_id},
        {"$set": {"tags": tags, "updated_at": datetime.now(timezone.utc)}},
        upsert=True,
    )


def get_user_interests(team_id: str, user_id: str) -> list[str]:
    """Return the stored interest tags for a user, or an empty list."""
    col = _get_user_interests_col()
    doc = col.find_one({"team_id": team_id, "user_id": user_id})
    return doc.get("tags", []) if doc else []


def get_all_user_interests(team_id: str) -> list[dict]:
    """Return all users with their interest tags for a given workspace."""
    col = _get_user_interests_col()
    return list(col.find({"team_id": team_id}, {"_id": 0, "user_id": 1, "tags": 1}))
