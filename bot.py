from slack_sdk import WebClient
import logging
import os
from datetime import datetime
import time
from pathlib import Path
from dotenv import load_dotenv
import random
from preSet_timeLibrary import preSet_time_library

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

logging.basicConfig(level=logging.INFO)

def display_current_time():
    """Return formatted current local time and print it inline."""
    now = datetime.now()
    current_time_str = now.strftime("%I:%M:%S %p")
    print(f"\rCurrent Time: {current_time_str}", end="")
    return current_time_str



token = os.getenv("SLACK_TOKEN")
print("Loaded .env from:", env_path)
client = WebClient(token=token)
client.chat_postMessage(channel="#bot-test", text="bot online")

# How long (seconds) the bot should listen for responses after sending a prompt
RESPONSE_WINDOW_SECONDS = int(os.getenv("RESPONSE_WINDOW_SECONDS", "60"))


def listen_for_responses(channel_id: str, duration: int = RESPONSE_WINDOW_SECONDS, after_ts: str | None = None):
    """Poll channel history for `duration` seconds and collect user messages (excluding the bot).

    `channel_id` must be a Slack channel id (e.g. "C123..."). If `after_ts` is provided,
    only messages with timestamp > after_ts are considered. Returns list of dicts {user,text,ts}.
    """
    if not channel_id:
        logging.warning("No channel_id provided to listener")
        return []

    # get bot user id so we can ignore messages from the bot itself
    try:
        auth = client.auth_test()
        bot_user_id = auth.get("user_id")
    except Exception:
        bot_user_id = None

    start_time = time.time()
    end_time = start_time + duration
    last_seen = float(after_ts) if after_ts else start_time
    collected = []
    logging.info("Listening for responses in %s for %s seconds...", channel_id, duration)
    while time.time() < end_time:
        try:
            resp = client.conversations_history(channel=channel_id, oldest=str(last_seen), limit=100)
            messages = resp.get("messages", [])
            # Slack returns newest-first; iterate reversed to process in order
            for msg in reversed(messages):
                ts = float(msg.get("ts", 0))
                if ts <= last_seen:
                    continue
                user = msg.get("user")
                text = msg.get("text", "")
                if user and user != bot_user_id:
                    collected.append({"user": user, "text": text, "ts": ts})
                    print(f"Received message from {user}: {text}")
                last_seen = max(last_seen, ts)
        except Exception as e:
            logging.debug("Error fetching history: %s", e)
        time.sleep(1)

    logging.info("Finished listening; collected %d messages.", len(collected))
    try:
        client.chat_postMessage(channel=channel_id, text=f"Collected {len(collected)} responses in {duration} seconds.")
    except Exception:
        logging.debug("Could not post summary message.")
    return collected

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
        if current_time == "06:18:00 PM":
            # Post the prompt and then listen for replies using the returned channel id and ts
            resp = client.chat_postMessage(channel="#bot-test", text="send prompt")
            posted = getattr(resp, "data", None) or (resp if isinstance(resp, dict) else None)
            after_ts = None
            posted_channel_id = None
            if isinstance(posted, dict):
                after_ts = posted.get("ts")
                posted_channel_id = posted.get("channel")

            # normalize ts to a float-like string when possible
            try:
                after_ts = str(float(after_ts)) if after_ts else None
            except Exception:
                after_ts = None

            if posted_channel_id:
                listen_for_responses(posted_channel_id, duration=RESPONSE_WINDOW_SECONDS, after_ts=after_ts)
            else:
                # fallback: poll by channel name (best-effort) if id not available
                logging.info("No channel_id in post response; falling back to polling by name")
                # Try to use conversations_list only if needed (may require extra scopes)
                try:
                    # try to resolve channel id via listing public channels
                    clist = client.conversations_list(types="public_channel")
                    for c in clist.get("channels", []):
                        if c.get("name") == "bot-test":
                            listen_for_responses(c.get("id"), duration=RESPONSE_WINDOW_SECONDS, after_ts=after_ts)
                            break
                except Exception:
                    logging.debug("Could not resolve channel id via conversations_list")
        # If the current time matches the daily target time that was set, a message will be pinged
        if(current_time == daily_target_time):
            client.chat_postMessage(channel="#bot-test", text="random time hit")
            print(f"Random time hit: {daily_target_time}")

        time.sleep(1)
except KeyboardInterrupt:
    client.chat_postMessage(channel="#bot-test", text="bot offline")
    print("Program stopped by user.")
