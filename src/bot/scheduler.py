# src/bot/scheduler.py
import random
import time
from datetime import datetime, date

from slack_sdk import WebClient

from services.time_library import preSet_time_library
from bot.posting import display_current_time, post_csv_prompt, post_custom_prompt

_FMT = "%I:%M:%S %p"
_USER_PROMPT_INVITE_TIME = "09:15:00 AM"  # time to DM the randomly selected user
_USER_PROMPT_INVITE_PROBABILITY = 0.3    # 30% chance each day
_SOCIAL_CONNECTOR_TIME = "02:00:00 PM"   # time to post social connector message
_SOCIAL_CONNECTOR_PROBABILITY = 0.5      # 50% chance each day
_MENTOR_CHECKIN_TIME = "09:00:00 AM"     # time to send weekly mentor-mentee check-in (Mondays only)



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


def _pick_random_channel_user(client, channel: str) -> str | None:
    """Return a random non-bot member of the channel, or None on failure."""
    try:
        members = client.conversations_members(channel=channel)["members"]
        eligible = []
        for user_id in members:
            try:
                info = client.users_info(user=user_id)["user"]
                if not info.get("is_bot") and info.get("id") != "USLACKBOT" and not info.get("deleted"):
                    eligible.append(user_id)
            except Exception:
                pass
        return random.choice(eligible) if eligible else None
    except Exception as e:
        print(f"[SCHEDULER] Could not pick random user: {e}")
        return None



_REMINDER_DELAY_SECONDS = 30  # 30 seconds (testing)


def _send_reminders(client, channel: str, prompt_ts: str) -> None:
    """DM every channel member who hasn't responded 30 minutes after the vibe check prompt."""
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
                text="Hey! You're late to VibeCheck :camera: Drop a photo in the channel — it's not too late! :wave:",
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
                            active_client.chat_postMessage(channel=channel, text=f"!time set for today is {new_time}")
                        except Exception as e:
                            print(f"[SCHEDULER] [{team_id}] Error posting daily reset: {e}")
                    state.set_user_prompt_creator_used_today(False)
                    state.set_social_connector_used_today(False)

                if not state.is_today_active():
                    continue

                # Randomly invite a user to create today's prompt (30% chance, once per day at 9:15 AM)
                if current_time == _USER_PROMPT_INVITE_TIME and not state.get_user_prompt_creator_used_today():
                    state.set_user_prompt_creator_used_today(True)
                    if random.random() < _USER_PROMPT_INVITE_PROBABILITY:
                        selected_user = _pick_random_channel_user(active_client, channel)
                        if selected_user:
                            from commands.user_prompt_command import send_user_prompt_invitation
                            send_user_prompt_invitation(active_client, selected_user, team_id)

                # Social connector: pair two users with shared interests (50% chance, once per day at 2:00 PM)
                if current_time == _SOCIAL_CONNECTOR_TIME and not state.get_social_connector_used_today():
                    state.set_social_connector_used_today(True)
                    if random.random() < _SOCIAL_CONNECTOR_PROBABILITY:
                        from commands.social_connector import send_social_connector_message
                        send_social_connector_message(active_client, channel, team_id)

                # Mentor-mentee weekly check-in: every Monday at 9:00 AM, once per ISO week
                if current_time == _MENTOR_CHECKIN_TIME and datetime.now().weekday() == 0:
                    current_week = datetime.now().isocalendar()[1]
                    if state.get_mentor_checkin_week() != current_week:
                        state.set_mentor_checkin_week(current_week)
                        try:
                            from commands.mentor_mentee_command import send_weekly_checkin
                            send_weekly_checkin(active_client, team_id)
                            print(f"[SCHEDULER] [{team_id}] Sent mentor-mentee weekly check-in (week {current_week})")
                        except Exception as e:
                            print(f"[SCHEDULER] [{team_id}] Error sending mentor check-in: {e}")

                target_time = _get_target_time(state)
                if current_time.endswith(":00 AM") or current_time.endswith(":00 PM"):
                    print(f"[SCHEDULER] [{team_id}] now={current_time!r}  target={target_time!r}  mode={state.get_selected_mode()!r}")
                if target_time and current_time == target_time:
                    try:
                        custom_text = state.get_and_clear_pending_custom_prompt()
                        if custom_text:
                            ts = post_custom_prompt(
                                active_client,
                                custom_text,
                                channel=channel,
                                team_id=team_id,
                                prefix_text="Prompt of the day:",
                                footnote_text=f"user-created vibe check | time hit {target_time}",
                            )
                        else:
                            topic = state.get_and_clear_pending_topic()
                            ts = post_csv_prompt(
                                active_client,
                                channel=channel,
                                team_id=team_id,
                                prefix_text=f"Prompt of the day:",
                                topic=topic,
                                active_tags=state.get_active_tags() or None,
                                footnote_text=f"random vibe check | time hit {target_time}",
                                response_type=state.get_prompt_response_type(),
                            )
                        if ts:
                            state.set_last_prompt_ts(ts, channel=channel)
                        print(f"\n[SCHEDULER] [{team_id}] Time hit: {target_time}")
                    except Exception as e:
                        print(f"[SCHEDULER] [{team_id}] Error posting time hit prompt: {e}")

                prompt_ts = state.get_last_prompt_ts()
                if prompt_ts and not state.get_reminder_sent():
                    elapsed = time.time() - float(prompt_ts)
                    if not state.get_reminder_enabled():
                        print(f"[REMINDER] [{team_id}] Reminders disabled — skipping (elapsed={elapsed:.0f}s)")
                    elif elapsed >= _REMINDER_DELAY_SECONDS:
                        prompt_channel = state.get_last_prompt_channel() or channel
                        print(f"[REMINDER] [{team_id}] {elapsed:.0f}s elapsed — sending reminder DMs to channel {prompt_channel}")
                        _send_reminders(active_client, prompt_channel, prompt_ts)
                        state.set_reminder_sent(True)

            time.sleep(1)

    except KeyboardInterrupt:
        print("Program stopped by user.")
