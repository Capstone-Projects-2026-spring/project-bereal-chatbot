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
from time_checker import TimeChecker


logging.basicConfig(level=logging.INFO)


# [environment setup]
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)


token = os.getenv("SLACK_TOKEN")
app_token = os.getenv("SLACK_APP_TOKEN")


print("Loaded .env from:", env_path)


client = WebClient(token=token)
bolt_app = App(token=token)

# the TimeChecker instance keeps track of the current target time and
# performs the periodic Slack posts.  It's referenced by command handlers
# below and run in a background thread.
time_checker = TimeChecker(client)




# How long (seconds) the bot should listen for responses after sending a prompt
RESPONSE_WINDOW_SECONDS = int(os.getenv("RESPONSE_WINDOW_SECONDS", "30"))




# [command to find prompt time ]
@bolt_app.command("/findtime") # only visible to the user that uses this command (works when bot is running)
def handle_findtime_command(ack, respond):
    try:
        ack()
        respond(f"Today's random scheduled prompt time is {time_checker.daily_target_time}")
    except Exception as e:
        print(f"Error handling /findtime command: {e}")



# [command to set time of prompt ]
@bolt_app.command("/picktime") # only visible to the user that uses this command (works when bot is running)
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
                    # update the target stored on the time_checker instance
                    time_checker.daily_target_time = preSet_time_library(choice)
                    respond(f"Time set to: {time_checker.daily_target_time}")
                    print(f"Daily target time set to: {time_checker.daily_target_time}")

                else:
                    respond("Must pick a number between 1 and 11 to set the time.")

            except ValueError:
                respond("Please provide a valid number between 1 and 11 to set the time")

    except Exception as e:
        print(f"Error handling /picktime command: {e}")


# [command to re-randomize time of prompt]
@bolt_app.command("/randomtime")
def random_time(ack, respond):
    try:
        ack()
        time_checker.daily_target_time = preSet_time_library(random.randint(1, 11))
        respond(f"New randomly selected daily target time: {time_checker.daily_target_time}")
    
    except Exception as e:
        print(f"Error handling random_time command: {e}")


# listen for messages in the channel so we can collect user responses
@bolt_app.event("message")
def handle_message_event(body, logger=None):
    try:
        event = body.get("event", {})
        if event.get("bot_id"):
            return

        if time_checker.is_within_response_window(RESPONSE_WINDOW_SECONDS):
            time_checker.record_response(event, RESPONSE_WINDOW_SECONDS)
            logging.info(f"Recorded response event: {event.get('text')}")
    except Exception as e:
        print(f"Error handling message event: {e}")


# Keep at bottom of file, runs after all other code is defined
if __name__ == "__main__":
    print("\n[BOOT] Starting bot...")

    try:
        client.chat_postMessage(channel="#bot-test", text="bot online")
    except Exception as e:
        print(f"Error posting 'bot online' message: {e}")

    # Start the time-checking loop in a background thread
    print("[BOOT] Starting background time checker...")
    time_thread = threading.Thread(target=time_checker.run, daemon=True)
    time_thread.start()

    print("[BOOT] Starting Socket Mode handler...")
    handler = SocketModeHandler(bolt_app, app_token)
    handler.start()
