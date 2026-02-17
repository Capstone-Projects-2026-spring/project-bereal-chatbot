import slack
import os
from datetime import datetime
import time
from pathlib import Path
from dotenv import load_dotenv
import random

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

def display_current_time():
    """Continuously fetches and prints the current local time every second."""
    now = datetime.now()
    # Format the time as a string (e.g., "10:23:45 AM")
    current_time_str = now.strftime("%I:%M:%S %p")
    print(f"\rCurrent Time: {current_time_str}", end="")
    return current_time_str

def preSet_time_library(random_number):
# Library of random times that will be chosen at random
    match random_number:
        case 1:
            return "12:0:00 PM"

        case 2:
            return "12:30:00 PM"

        case 3:
            return "01:00:00 PM"

        case 4:
            return "01:30:00 PM"

        case 5:
            return "02:00:00 PM"
        
        case 6:
            return "02:30:00 PM"
        
        case 7:
            return "03:00:00 PM"
        
        case 8:
            return "03:30:00 PM"
        
        case 9:
            return "04:00:00 PM"
        
        case 10:
            return "04:30:00 PM"

        case 11:
            return "05:00:00 PM"


token = os.getenv("SLACK_TOKEN")
print("Loaded .env from:", env_path)
print("test")
client = slack.WebClient(token=token)
client.chat_postMessage(channel="#bot-test", text="bot online")

# code for setting random time from preset switch case
daily_target_time = None
daily_target_time = preSet_time_library(random.randint(1,11)) 
print(f"Randomly selected daily target time: {daily_target_time}\n")
client.chat_postMessage(channel="#bot-test", text="time set for today is " + daily_target_time)

try:
    while True:
        # displays the current time on console
        current_time = display_current_time()
        if(current_time == "09:30:00 AM"):
            client.chat_postMessage(channel="#bot-test", text="send prompt")
        # if the current time matches the daily target time that was set, a message will be pinged
        if(current_time == daily_target_time):
            client.chat_postMessage(channel="#bot-test", text="random time hit")
            print(f"Random time hit: {daily_target_time}")

        time.sleep(1)
except KeyboardInterrupt:
    client.chat_postMessage(channel="#bot-test", text="bot offline")
    print("Program stopped by user.")
