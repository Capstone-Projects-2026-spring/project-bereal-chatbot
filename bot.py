# bot.py
from slack_sdk import WebClient
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import os
import time
import random
import logging
import threading
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from preSet_timeLibrary import preSet_time_library

# NEW: pulls prompts from CSV
from pGrab import get_random_prompt_text, mark_prompt_asked

# NEW: registers /forceprompt from a separate file
from force_prompt_command import register_force_prompt_command


logging.basicConfig(level=logging.INFO)


# [environment setup]
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# CHANGED: use SLACK_BOT_TOKEN (matches your .env)
token = os.getenv("SLACK_BOT_TOKEN")
app_token = os.getenv("SLACK_APP_TOKEN")

print("Loaded .env from:", env_path)

client = WebClient(token=token)
bolt_app = App(token=token)

# NEW: hook in /forceprompt
register_force_prompt_command(bolt_app, client)


# Global variable for the daily target time
daily_target_time = None


# [display current time function]
def display_current_time():
    """Return formatted current local time and print it inline."""
    now = datetime.now()
    current_time_str = now.strftime("%I:%M:%S %p")
    print(f"\rCurrent Time: {current_time_str}", end="")
    return current_time_str


def post_csv_prompt(channel="#bot-test", prefix_text=None):
    """Pick a random prompt from the CSV, increment times_asked, and post it."""
    prompt_id, prompt_text = get_random_prompt_text()
    mark_prompt_asked(prompt_id)

    msg = prompt_text
    if prefix_text:
        msg = f"{prefix_text}\n\n{prompt_text}"

    client.chat_postMessage(channel=channel, text=msg)


# [background time-checking loop]
def run_time_checker():
    """Run in a background thread to check time without blocking the bot event loop."""
    global daily_target_time

    # Picks a random number from 1 to 11 that matches different given times in the format of "hh:mm:ss AM/PM"
    daily_target_time = preSet_time_library(random.randint(1, 11))
    print(f"Randomly selected daily target time: {daily_target_time}\n")

    try:
        client.chat_postMessage(channel="#bot-test", text="time set for today is " + daily_target_time)
    except Exception as e:
        print(f"Error posting initial time message: {e}")

    time.sleep(1)  # Wait for logging to finish before displaying current time

    try:
        while True:
            # Displays the current time on console
            current_time = display_current_time()

            # CHANGED: noon now posts a CSV prompt
            if current_time == "12:00:00 PM":
                try:
                    post_csv_prompt(
                        channel="#bot-test",
                        prefix_text="Daily vibe check prompt:"
                    )
                except Exception as e:
                    print(f"Error posting 12:00:00 PM prompt: {e}")

            # CHANGED: random scheduled time now posts a CSV prompt
            if current_time == daily_target_time:
                try:
                    post_csv_prompt(
                        channel="#bot-test",
                        prefix_text=f"Random vibe check prompt (time hit {daily_target_time}):"
                    )
                    print(f"Random time hit: {daily_target_time}")
                except Exception as e:
                    print(f"Error posting random time hit prompt: {e}")

            time.sleep(1)

    except KeyboardInterrupt:
        try:
            client.chat_postMessage(channel="#bot-test", text="bot offline")
        except Exception as e:
            print(f"Error posting offline message: {e}")
        print(" Program stopped by user.")


# [find prompt time command]
@bolt_app.command("/findtime")  # only visible to the user that uses this command (works when bot is running)
def handle_findtime_command(ack, respond):
    try:
        ack()
        respond(f"Today's random scheduled prompt time is {daily_target_time}")
    except Exception as e:
        print(f"Error handling /findtime command: {e}")


# [set time of prompt command]
@bolt_app.command("/picktime")  # only visible to the user that uses this command (works when bot is running)
def pick_time(ack, respond, body):
    try:
        ack()
        text = body.get("text", "").strip()

        if not text:
            # Show options if no argument provided
            time_options = (
                "Available time options:\n"
                "1. 12:00:00 PM\n"
                "2. 12:30:00 PM\n"
                "3. 01:00:00 PM\n"
                "4. 01:30:00 PM\n"
                "5. 02:00:00 PM\n"
                "6. 02:30:00 PM\n"
                "7. 03:00:00 PM\n"
                "8. 03:30:00 PM\n"
                "9. 04:00:00 PM\n"
                "10. 04:30:00 PM\n"
                "11. 05:00:00 PM\n\n"
                "Use `/picktime <number>` to set a specific time (e.g., `/picktime 5` for 02:00:00 PM)"
            )
            respond(time_options)

        else:
            # Parse the number and update daily_target_time
            try:
                choice = int(text)

                if 1 <= choice <= 11:
                    global daily_target_time
                    daily_target_time = preSet_time_library(choice)
                    respond(f"Time set to: {daily_target_time}")
                    print(f"Daily target time set to: {daily_target_time}")
                else:
                    respond("Must pick a number between 1 and 11 to set the time.")

            except ValueError:
                respond("Please provide a valid number between 1 and 11 to set the time")

    except Exception as e:
        print(f"Error handling /picktime command: {e}")


# Keep at bottom of file, runs after all other code is defined
if __name__ == "__main__":
    print("\n[BOOT] Starting bot...")

    try:
        client.chat_postMessage(channel="#bot-test", text="bot online")
    except Exception as e:
        print(f"Error posting 'bot online' message: {e}")

    # Start the time-checking loop in a background thread
    print("[BOOT] Starting background time checker...")
    time_thread = threading.Thread(target=run_time_checker, daemon=True)
    time_thread.start()

    print("[BOOT] Starting Socket Mode handler...")
    handler = SocketModeHandler(bolt_app, app_token)
    handler.start()