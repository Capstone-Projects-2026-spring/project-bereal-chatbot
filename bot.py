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

logging.basicConfig(level=logging.INFO)

# [environment setup]
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)


token = os.getenv("SLACK_TOKEN")
app_token = os.getenv("SLACK_APP_TOKEN")

print("Loaded .env from:", env_path)

client = WebClient(token=token)
bolt_app = App(token=token)

# Global variable for the daily target time
daily_target_time = None



# [display current time function]
def display_current_time():
    """Continuously fetches and prints the current local time every second."""
    now = datetime.now()
    # Format the time as a string (e.g., "10:23:45 AM")
    current_time_str = now.strftime("%I:%M:%S %p")
    print(f"\rCurrent Time: {current_time_str}", end="")
    return current_time_str


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

    try:
        while True:
            # Displays the current time on console
            current_time = display_current_time()
            if current_time == "09:30:00 AM":
                try:
                    client.chat_postMessage(channel="#bot-test", text="send prompt")
                except Exception as e:
                    print(f"Error posting 9:30 AM message: {e}")
            # If the current time matches the daily target time that was set, a message will be pinged
            if current_time == daily_target_time:
                try:
                    client.chat_postMessage(channel="#bot-test", text="random time hit")
                    print(f"Random time hit: {daily_target_time}")
                except Exception as e:
                    print(f"Error posting random time hit message: {e}")

            time.sleep(1)
    except KeyboardInterrupt:
        try:
            client.chat_postMessage(channel="#bot-test", text="bot offline")
        except Exception as e:
            print(f"Error posting offline message: {e}")
        print(" Program stopped by user.")


# [find prompt time command]
@bolt_app.command("/findtime") # only visible to the user that uses this command
def handle_findtime_command(ack, respond):
    try:
        ack()
        respond(f"Today's random scheduled prompt time is {daily_target_time}")

    except Exception as e:
        print(f"Error handling /findtime command: {e}")


def find_time():
    """Return the daily target time."""
    return daily_target_time


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

