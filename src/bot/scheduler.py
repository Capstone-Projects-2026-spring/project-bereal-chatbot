# src/bot/scheduler.py
import random
import time
from datetime import datetime, date

from slack_sdk import WebClient

from services.time_library import preSet_time_library
from bot.posting import display_current_time, post_csv_prompt

_FMT = "%I:%M:%S %p"
_REMINDER_DELAY_SECONDS = 600  # 10 minutes


def _pick_random_time(start_str=None, end_str=None, after: datetime = None) -> str:
    """
    Pick a random time within start_str..end_str (HH:MM:SS AM/PM).
    If after is provided, only times strictly after that moment are considered.
    Falls back to the preset library if no range is set or the range is exhausted.
    """
    from datetime import timedelta

    if start_str and end_str:
        try:
            start_dt = datetime.strptime(start_str.strip(), _FMT)
            end_dt = datetime.strptime(end_str.strip(), _FMT)
            if after:
                after_time = after.replace(year=start_dt.year, month=start_dt.month, day=start_dt.day)
                if after_time + timedelta(seconds=1) > start_dt:
                    start_dt = after_time + timedelta(seconds=1)
            if start_dt >= end_dt:
                raise ValueError("No future time available in range")
            delta_seconds = int((end_dt - start_dt).total_seconds())
            random_offset = random.randint(0, delta_seconds)
            return (start_dt + timedelta(seconds=random_offset)).strftime(_FMT)
        except Exception as e:
            print(f"[SCHEDULER] Could not pick from range ({e}), falling back to preset library")

    if after:
        candidates = [preSet_time_library(i) for i in range(1, 18)]
        after_cmp = datetime(2000, 1, 1, after.hour, after.minute, after.second)
        future = [t for t in candidates if datetime.strptime(t, _FMT).replace(year=2000, month=1, day=1) > after_cmp]
        if future:
            return random.choice(future)
        print("[SCHEDULER] No future preset times available today — will try again tomorrow")

    return preSet_time_library(random.randint(1, 17))


def _get_target_time(state) -> str | None:
    """Return the trigger time based on the active mode."""
    mode = state.get_selected_mode()
    if mode == "mode_static":
        return state.get_static_time()
    return state.get_daily_target_time()


def _ensure_initial_time(state) -> None:
    """Pick an initial daily target time for a team state that doesn't have one yet."""
    if state.get_daily_target_time() is None:
        t = _pick_random_time(
            state.get_random_start_time(),
            state.get_random_end_time(),
            after=datetime.now()
        )
        state.set_daily_target_time(t)
        print(f"[SCHEDULER] Initial time picked for new workspace: {t}")


def _send_reminders(client, channel: str, prompt_ts: str) -> None:
    """DM every channel member who hasn't posted since the vibe check prompt."""
    try:
        members = client.conversations_members(channel=channel)["members"]
    except Exception as e:
        print(f"[REMINDER] Could not fetch channel members: {e}")
        return

    try:
        history = client.conversations_history(channel=channel, oldest=prompt_ts, limit=200)
        responded = {m["user"] for m in history.get("messages", []) if "user" in m}
    except Exception as e:
        print(f"[REMINDER] Could not fetch channel history: {e}")
        return

    for user_id in members:
        if user_id in responded:
            continue
        try:
            info = client.users_info(user=user_id)
            if info["user"].get("is_bot") or info["user"].get("id") == "USLACKBOT":
                continue
        except Exception:
            pass
        try:
            client.chat_postMessage(
                channel=user_id,
                text="Hey! You missed the vibe check. It's not too late to share how you're doing! :wave:",
            )
            print(f"[REMINDER] Sent reminder DM to {user_id}")
        except Exception as e:
            print(f"[REMINDER] Could not DM {user_id}: {e}")


def run_time_checker(state_manager, fallback_client, default_channel: str) -> None:
    """
    Background loop that checks the clock every second and posts prompts at the
    configured time for each workspace. Each workspace has its own state.
    """
    last_reset_date = date.today()
    time.sleep(1)

    try:
        while True:
            current_time = display_current_time()
            today = date.today()
            new_day = today != last_reset_date
            if new_day:
                last_reset_date = today

            for team_id, state in state_manager.all_states().items():
                token = state.get_active_token()
                channel = state.get_active_channel() or default_channel

                active_client = WebClient(token=token) if token else fallback_client

                _ensure_initial_time(state)

                if new_day:
                    mode = state.get_selected_mode()
                    if mode == "mode_random" or mode is None:
                        new_time = _pick_random_time(
                            state.get_random_start_time(),
                            state.get_random_end_time(),
                            after=datetime.now()
                        )
                        state.set_daily_target_time(new_time)
                        print(f"[SCHEDULER] [{team_id}] New day — target time reset to: {new_time}")
                        try:
                            active_client.chat_postMessage(channel=channel, text=f"time set for today is {new_time}")
                        except Exception as e:
                            print(f"[SCHEDULER] [{team_id}] Error posting daily reset: {e}")

                if not state.is_today_active():
                    continue

                if current_time == "8:42:00 AM":
                    try:
                        topic = state.get_and_clear_pending_topic()
                        ts = post_csv_prompt(active_client, channel=channel, team_id=team_id, prefix_text="PROMPT OF THE DAY:", topic=topic, active_tags=state.get_active_tags() or None)
                        if ts:
                            state.set_last_prompt_ts(ts)
                    except Exception as e:
                        print(f"[SCHEDULER] [{team_id}] Error posting 12 PM prompt: {e}")

                target_time = _get_target_time(state)
                if target_time and current_time == target_time:
                    try:
                        topic = state.get_and_clear_pending_topic()
                        ts = post_csv_prompt(
                            active_client,
                            channel=channel,
                            team_id=team_id,
                            prefix_text=f"Prompt of the day:",
                            topic=topic,
                            active_tags=state.get_active_tags() or None,
                            footnote_text=f"random vibe check | time hit {target_time}"
                        )
                        if ts:
                            state.set_last_prompt_ts(ts)
                        print(f"\n[SCHEDULER] [{team_id}] Time hit: {target_time}")
                    except Exception as e:
                        print(f"[SCHEDULER] [{team_id}] Error posting time hit prompt: {e}")

                prompt_ts = state.get_last_prompt_ts()
                if prompt_ts and not state.get_reminder_sent():
                    if time.time() - float(prompt_ts) >= _REMINDER_DELAY_SECONDS:
                        print(f"[REMINDER] [{team_id}] 10 min elapsed — sending reminder DMs")
                        _send_reminders(active_client, channel, prompt_ts)
                        state.set_reminder_sent(True)

            time.sleep(1)

    except KeyboardInterrupt:
        print("Program stopped by user.")
