# src/services/mongo_service.py
from __future__ import annotations

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
        # Maps channel_id -> prompt_id for the most recently posted prompt
        self._active_prompt: dict[str, str] = {}

    def record_prompt_sent(self, prompt_id: str, prompt_text: str, tags: str, channel: str) -> None:
        """
        Upsert the prompt document, increment times_asked, and mark this
        channel's active prompt so responses can be counted.
        """
        tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

        self._col.update_one(
            {"prompt_id": str(prompt_id)},
            {
                "$set": {
                    "prompt": prompt_text,
                    "tags": tag_list,
                    "last_asked_at": datetime.now(timezone.utc),
                },
                "$inc": {"times_asked": 1},
                "$setOnInsert": {"times_responded": 0},
            },
            upsert=True,
        )
        self._active_prompt[channel] = str(prompt_id)

    def record_response(self, channel: str) -> None:
        """
        Increment times_responded for whichever prompt is currently active
        in this channel. No-op if no prompt has been posted yet.
        """
        prompt_id = self._active_prompt.get(channel)
        if not prompt_id:
            return
        self._col.update_one(
            {"prompt_id": prompt_id},
            {"$inc": {"times_responded": 1}},
        )

    def get_all_stats(self) -> list[dict]:
        """Return all prompt stats sorted by times_asked descending."""
        return list(self._col.find({}, {"_id": 0}).sort("times_asked", -1))


def init_tracker(mongo_uri: str) -> PromptTracker:
    global _tracker
    _tracker = PromptTracker(mongo_uri)
    return _tracker


def get_tracker() -> PromptTracker | None:
    return _tracker
