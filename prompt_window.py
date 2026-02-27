from slack_sdk import WebClient
from datetime import datetime, timedelta
import threading
import os
from pathlib import Path
from dotenv import load_dotenv


env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

token = os.getenv("SLACK_TOKEN")
client = WebClient(token=token)


# Global variables for the prompt response window
prompt_window_open = False
prompt_deadline = None


# send prompt and start countdown
def send_prompt_with_countdown(channel="#bot-test", window_minutes=60):
    """Opens the response window for however long window_minutes is set to."""
    global prompt_window_open, prompt_deadline

    prompt_window_open = True
    prompt_deadline = datetime.now() + timedelta(minutes=window_minutes)

    try:
        client.chat_postMessage(
            channel=channel,
            text=f" You have {window_minutes} minutes to respond."
        )
    except Exception as e:
        print(f"Error posting prompt: {e}")

    # Schedule reminders at the halfway point and 10 minutes before close
    halfway = (window_minutes // 2) * 60
    ten_min_warning = (window_minutes - 10) * 60

    threading.Timer(halfway, send_reminder, args=(window_minutes // 2, channel)).start()
    threading.Timer(ten_min_warning, send_reminder, args=(10, channel)).start()
    threading.Timer(window_minutes * 60, close_prompt_window, args=(channel,)).start()


def send_reminder(minutes_left, channel="#bot-test"):
    """Posts a reminder with how much time is left."""
    if not prompt_window_open:
        return
    try:
        client.chat_postMessage(
            channel=channel,
            text=f"{minutes_left} minutes left to respond."
        )
    except Exception as e:
        print(f"Error posting reminder: {e}")


def close_prompt_window(channel="#bot-test"):
    """Closes the response window and notifies the channel."""
    global prompt_window_open
    prompt_window_open = False
    try:
        client.chat_postMessage(
            channel=channel,
            text="Time's up. The response window is now closed."
        )
    except Exception as e:
        print(f"Error posting window closed message: {e}")


def is_window_open():
    """Returns whether the response window is currently open."""
    return prompt_window_open


# [get deadline]
def get_deadline():
    if prompt_deadline:
        return prompt_deadline.strftime("%I:%M %p")
    return None