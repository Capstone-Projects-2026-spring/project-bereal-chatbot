import slack
import os
from datetime import datetime
import time
from pathlib import Path
from dotenv import load_dotenv

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
print("test")
client = slack.WebClient(token=token)

try:
    while True:
        current_time = display_current_time()
        if(current_time == "09:30:00 AM"):
            client.chat_postMessage(channel="#bot-test", text="send prompt")
        
        time.sleep(1)
except KeyboardInterrupt:
    print("Program stopped by user.")
