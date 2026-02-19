import slack
import os
from datetime import datetime
import time
from pathlib import Path
from dotenv import load_dotenv
import random
from preSet_timeLibrary import preSet_time_library

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

def display_current_time():
    """Continuously fetches and prints the current local time every second."""
    now = datetime.now()
    # Format the time as a string (e.g., "10:23:45 AM")
    current_time_str = now.strftime("%I:%M:%S %p")
    print(f"\rCurrent Time: {current_time_str}", end="")
    return current_time_str



token = os.getenv("SLACK_TOKEN")
print("Loaded .env from:", env_path)
client = slack.WebClient(token=token)
client.chat_postMessage(channel="#bot-test", text="bot online")

# Code for setting random time from preset switch case
daily_target_time = None
# Picks a random number from 1 to 11 that matches different given times in the format of "hh:mm:ss AM/PM"
daily_target_time = preSet_time_library(random.randint(1,11)) 
print(f"Randomly selected daily target time: {daily_target_time}\n")
client.chat_postMessage(channel="#bot-test", text="time set for today is " + daily_target_time)

try:
    while True:
        # Displays the current time on console
        current_time = display_current_time()
        if(current_time == "09:30:00 AM"):
            client.chat_postMessage(channel="#bot-test", text="send prompt")
        # If the current time matches the daily target time that was set, a message will be pinged
        if(current_time == daily_target_time):
            client.chat_postMessage(channel="#bot-test", text="random time hit")
            print(f"Random time hit: {daily_target_time}")

        time.sleep(1)
except KeyboardInterrupt:
    client.chat_postMessage(channel="#bot-test", text="bot offline")
    print("Program stopped by user.")
