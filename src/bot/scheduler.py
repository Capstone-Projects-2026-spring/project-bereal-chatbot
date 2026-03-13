# src/bot/scheduler.py
import random
import time

from services.time_library import preSet_time_library
from bot.posting import display_current_time, post_csv_prompt


def run_time_checker(client, default_channel: str, state) -> None:
    """
    Background loop:
    - picks a random daily time (1..11)
    - posts it
    - checks clock every second
    - at 12:00:00 PM posts a daily prompt
    - at random time posts another prompt
    """
    daily_target_time = preSet_time_library(random.randint(1, 11))
    state.set_daily_target_time(daily_target_time)

    print(f"Randomly selected daily target time: {daily_target_time}\n")

    try:
        client.chat_postMessage(channel=default_channel, text="time set for today is " + daily_target_time)
    except Exception as e:
        print(f"Error posting initial time message: {e}")

    time.sleep(1)

    try:
        while True:
            current_time = display_current_time()

            if current_time == "12:00:00 PM":
                try:
                    post_csv_prompt(client, channel=default_channel, prefix_text="Daily vibe check prompt:")
                except Exception as e:
                    print(f"Error posting 12:00:00 PM prompt: {e}")

            daily_target_time = state.get_daily_target_time()
            if daily_target_time and current_time == daily_target_time:
                try:
                    post_csv_prompt(
                        client,
                        channel=default_channel,
                        prefix_text=f"Random vibe check prompt (time hit {daily_target_time}):"
                    )
                    print(f"Random time hit: {daily_target_time}")
                except Exception as e:
                    print(f"Error posting random time hit prompt: {e}")

            time.sleep(1)

    except KeyboardInterrupt:
        try:
            client.chat_postMessage(channel=default_channel, text="bot offline")
        except Exception as e:
            print(f"Error posting offline message: {e}")
        print(" Program stopped by user.")