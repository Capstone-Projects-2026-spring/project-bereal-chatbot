# src/bot/scheduler.py
import random
import time
from datetime import datetime, date

from services.time_library import preSet_time_library
from bot.posting import display_current_time, post_csv_prompt

_FMT = "%I:%M:%S %p"


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
                # Clamp start to be at least one second past 'after'
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

    # Preset library fallback: only pick times that are in the future
    if after:
        candidates = [preSet_time_library(i) for i in range(1, 18)]
       
        # Rebuild after as a comparable datetime on the same dummy date as candidates
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

    # mode_preset and mode_random both ultimately store the target in daily_target_time
    return state.get_daily_target_time()


def run_time_checker(client, default_channel: str, state) -> None:
    """
    Background loop that checks the clock every second and posts prompts at the
    configured time(s). Respects the mode set via the control panel.
    """
    # Pick initial random time — must be in the future relative to now
    daily_target_time = _pick_random_time(
        state.get_random_start_time(),
        state.get_random_end_time(),
        after=datetime.now()
    )
    state.set_daily_target_time(daily_target_time)
    print(f"[SCHEDULER] Initial daily target time: {daily_target_time}")

    try:
        channel = state.get_active_channel() or default_channel
        client.chat_postMessage(channel=channel, text="time set for today is " + daily_target_time)
    except Exception as e:
        print(f"Error posting initial time message: {e}")

    last_reset_date = date.today()
    time.sleep(1)

    try:
        while True:
            current_time = display_current_time()
            channel = state.get_active_channel() or default_channel
            today = date.today()

            # At midnight, reset the random daily time if in random mode
            if today != last_reset_date:
                last_reset_date = today
                mode = state.get_selected_mode()
                if mode == "mode_random" or mode is None:
                    new_time = _pick_random_time(
                        state.get_random_start_time(),
                        state.get_random_end_time(),
                        after=datetime.now()
                    )
                    state.set_daily_target_time(new_time)
                    print(f"[SCHEDULER] New day — daily target time reset to: {new_time}")
                    try:
                        client.chat_postMessage(channel = channel, text=f"time set for today is {new_time}")
                    except Exception as e:
                        print(f"Error posting daily reset message: {e}")

            if state.is_today_active():
                if current_time == "12:00:00 PM":
                    try:
                        post_csv_prompt(client, channel=channel, prefix_text="Daily vibe check prompt:")
                    except Exception as e:
                        print(f"Error posting 12:00:00 PM prompt: {e}")

                target_time = _get_target_time(state)
                if target_time and current_time == target_time:
                    try:
                        post_csv_prompt(
                            client,
                            channel=channel,
                            prefix_text=f"Random vibe check prompt (time hit {target_time}):"
                        )
                        print(f"\n[SCHEDULER] Time hit: {target_time}")
                    except Exception as e:
                        print(f"Error posting time hit prompt: {e}")

            time.sleep(1)

    except KeyboardInterrupt:
        try:
            channel = state.get_active_channel() or default_channel
            client.chat_postMessage(channel=channel, text="bot offline")
        except Exception as e:
            print(f"Error posting offline message: {e}")
        print("Program stopped by user.")
