# src/services/mentor_service.py
import os
import random
from datetime import datetime, timezone
from typing import Optional

from pymongo import MongoClient

_mongo_client = None


def _get_col(team_id: str):
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(os.getenv("MONGO_URI"))
    return _mongo_client["vibecheck"][f"mentor_mentee_{team_id}"]


def get_registration(team_id: str, user_id: str) -> Optional[dict]:
    return _get_col(team_id).find_one({"user_id": user_id}, {"_id": 0})


def upsert_registration(
    team_id: str,
    user_id: str,
    role: str,
    interests: list,
    job_title: str = "",
    years_experience: str = "",
    bio: str = "",
) -> None:
    _get_col(team_id).update_one(
        {"user_id": user_id},
        {"$set": {
            "user_id": user_id,
            "team_id": team_id,
            "role": role,
            "job_title": job_title,
            "years_experience": years_experience,
            "bio": bio,
            "interests": interests,
            "matched_with": None,
            "matched_at": None,
            "group_dm_channel": None,
            "signed_up_at": datetime.now(timezone.utc).isoformat(timespec="seconds") + "Z",
        }},
        upsert=True,
    )


def remove_registration(team_id: str, user_id: str) -> None:
    _get_col(team_id).delete_one({"user_id": user_id})


def clear_pair(team_id: str, user1_id: str, user2_id: str) -> None:
    """Remove the pairing from both users without deleting their registrations."""
    col = _get_col(team_id)
    col.update_one({"user_id": user1_id}, {"$set": {"matched_with": None, "matched_at": None, "group_dm_channel": None}})
    col.update_one({"user_id": user2_id}, {"$set": {"matched_with": None, "matched_at": None, "group_dm_channel": None}})


def get_all_registrations(team_id: str) -> list[dict]:
    """Return all mentor and mentee profiles for the admin panel."""
    return list(_get_col(team_id).find({}, {"_id": 0}).sort("signed_up_at", 1))


def get_all_unmatched(team_id: str) -> tuple[list, list]:
    """Return lists of unmatched mentor and mentee docs."""
    col = _get_col(team_id)
    mentors = list(col.find({"role": "mentor", "matched_with": None}, {"_id": 0}))
    mentees = list(col.find({"role": "mentee", "matched_with": None}, {"_id": 0}))
    return mentors, mentees


def get_all_pairs(team_id: str) -> list[tuple[str, str, Optional[str]]]:
    """Return (mentor_id, mentee_id, group_dm_channel) for all currently matched pairs."""
    col = _get_col(team_id)
    mentors = list(col.find({"role": "mentor", "matched_with": {"$ne": None}}, {"_id": 0}))
    return [(m["user_id"], m["matched_with"], m.get("group_dm_channel")) for m in mentors]


def run_matching(team_id: str, mentors: list, mentees: list) -> list[tuple[str, str, list]]:
    """
    Greedy match mentors to mentees by shared interest count, then by bio similarity.
    Falls back to arbitrary pairing if no shared interests exist.
    Returns list of (mentor_id, mentee_id, shared_tags).
    """
    col = _get_col(team_id)
    used_mentors: set[str] = set()
    used_mentees: set[str] = set()
    pairs: list[tuple[str, str, list]] = []

    # Build scored candidates; shuffle first so ties are broken randomly
    candidates: list[tuple[int, str, str, list]] = []
    for mentor in mentors:
        for mentee in mentees:
            shared = list(set(mentor.get("interests", [])) & set(mentee.get("interests", [])))
            candidates.append((len(shared), mentor["user_id"], mentee["user_id"], shared))

    random.shuffle(candidates)
    candidates.sort(key=lambda x: -x[0])  # stable sort keeps shuffled order within equal scores

    for score, mentor_id, mentee_id, shared in candidates:
        if mentor_id in used_mentors or mentee_id in used_mentees:
            continue
        used_mentors.add(mentor_id)
        used_mentees.add(mentee_id)
        _save_pair(col, mentor_id, mentee_id)
        pairs.append((mentor_id, mentee_id, shared))

    # Pair any leftovers with no shared interests
    remaining_mentors = [m for m in mentors if m["user_id"] not in used_mentors]
    remaining_mentees = [m for m in mentees if m["user_id"] not in used_mentees]
    random.shuffle(remaining_mentors)
    random.shuffle(remaining_mentees)
    for mentor, mentee in zip(remaining_mentors, remaining_mentees):
        _save_pair(col, mentor["user_id"], mentee["user_id"])
        pairs.append((mentor["user_id"], mentee["user_id"], []))

    return pairs


def _save_pair(col, mentor_id: str, mentee_id: str) -> None:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds") + "Z"
    col.update_one({"user_id": mentor_id}, {"$set": {"matched_with": mentee_id, "matched_at": now}})
    col.update_one({"user_id": mentee_id}, {"$set": {"matched_with": mentor_id, "matched_at": now}})
