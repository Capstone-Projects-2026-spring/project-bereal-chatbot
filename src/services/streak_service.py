# src/services/streak_service.py

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path
from threading import Lock
from typing import Optional

from bot.paths import STRUCTURED_JSONL

_lock = Lock()

MILESTONES = {7, 14, 21, 50, 100, 365, 730}


def _response_dates(user_id: str, log_file: Path) -> list[date]:
    if not log_file.exists():
        return []

    days: set[date] = set()
    with log_file.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue

            if row.get("bot_id") or row.get("user_id") != user_id:
                continue

            raw = row.get("ingested_at_utc") or row.get("ts")
            if not raw:
                continue

            try:
                if "T" in str(raw):
                    day = datetime.fromisoformat(str(raw).replace("Z", "+00:00")).date()
                else:
                    day = datetime.fromtimestamp(float(raw)).date()
                days.add(day)
            except (ValueError, OSError):
                continue

    return sorted(days)


def _streak_length(days: list[date], today: Optional[date] = None) -> int:
    if not days:
        return 0

    today = today or date.today()
    yesterday = today - timedelta(days=1)

    if days[-1] < yesterday:
        return 0

    count = 1
    cur = days[-1]
    for prev in reversed(days[:-1]):
        if cur - prev == timedelta(days=1):
            count += 1
            cur = prev
        else:
            break

    return count


def get_user_streak(user_id: str, log_file: Optional[Path] = None) -> int:
    log_file = log_file or STRUCTURED_JSONL
    with _lock:
        days = _response_dates(user_id, log_file)
    return _streak_length(days)


def get_all_streaks(log_file: Optional[Path] = None) -> dict[str, int]:
    log_file = log_file or STRUCTURED_JSONL
    if not log_file.exists():
        return {}

    user_ids: set[str] = set()
    with log_file.open(encoding="utf-8") as f:
        for line in f:
            try:
                row = json.loads(line.strip())
                uid = row.get("user_id")
                if uid and not row.get("bot_id"):
                    user_ids.add(uid)
            except json.JSONDecodeError:
                continue

    return {uid: get_user_streak(uid, log_file) for uid in user_ids}


def _streak_emoji(streak: int) -> str:
    if streak >= 365:
        return "🐐"
    if streak >= 100:
        return "🏆"
    if streak >= 50:
        return "💀🔥"
    if streak >= 21:
        return "🔥🔥"
    return "🔥"


def check_and_announce_streak(
    user_id: str,
    user_name: str,
    client,
    channel: str,
    log_file: Optional[Path] = None,
) -> None:
    streak = get_user_streak(user_id, log_file)

    if streak not in MILESTONES:
        return

    emoji = _streak_emoji(streak)

    if streak == 730:
        label = "2-year"
    elif streak == 365:
        label = "1-year"
    else:
        label = f"{streak}-day"

    msg = f"{emoji} *{user_name}* just hit a *{label} streak*. {emoji}"
    try:
        client.chat_postMessage(channel=channel, text=msg)
    except Exception as e:
        print(f"[streaks] couldn't post milestone: {e}")


def register_streak_command(app, client) -> None:
    @app.command("/streak")
    def handle_streak(ack, command, respond):
        ack()
        sub = (command.get("text") or "").strip().lower()
        user_id = command.get("user_id", "")
        user_name = command.get("user_name", user_id)

        if sub == "leaderboard":
            _leaderboard(client, respond)
        else:
            _personal(user_id, user_name, respond)


def _personal(user_id: str, user_name: str, respond) -> None:
    streak = get_user_streak(user_id)

    if streak == 0:
        respond(f"No streak yet, *{user_name}*. Respond to today's prompt to get started.")
        return

    if streak < 7:
        respond(f"Day *{streak}* — keep going, *{user_name}*. First milestone is 7 days.")
        return

    emoji = _streak_emoji(streak)
    respond(f"{emoji} *{streak}-day streak*, {user_name}.")


def _leaderboard(client, respond) -> None:
    leaders = sorted(
        ((uid, s) for uid, s in get_all_streaks().items() if s > 0),
        key=lambda x: x[1],
        reverse=True,
    )[:10]

    if not leaders:
        respond("Nobody has an active streak yet.")
        return

    lines = ["*Streak Leaderboard*\n"]
    medals = ["🥇", "🥈", "🥉"]
    for i, (uid, streak) in enumerate(leaders):
        try:
            info = client.users_info(user=uid)
            profile = info["user"].get("profile", {})
            name = profile.get("display_name") or profile.get("real_name") or uid
        except Exception:
            name = uid
        medal = medals[i] if i < 3 else f"{i + 1}."
        lines.append(f"{medal} *{name}* — {streak} days {_streak_emoji(streak)}")

    respond("\n".join(lines))