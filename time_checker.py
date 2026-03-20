import time
import random
from datetime import datetime, timedelta


from services.time_library import preSet_time_library


def display_current_time():
    """Return formatted current local time and print it."""
    now = datetime.now()
    current_time_str = now.strftime("%I:%M:%S %p")
    # printing here to mimic the behaviour in bot.py
    print(f"\rCurrent Time: {current_time_str}", end="")
    return current_time_str


class TimeChecker:

    def __init__(self, client, state):
        self.client = client
        self.state = state
        self.daily_target_time = None
        # response tracking attributes
        self.last_prompt_time = None  # datetime when last prompt was sent
        self.responses = []  # list of event dicts collected during response window

    def run(self):
        self.daily_target_time = preSet_time_library(random.randint(1, 11))
        print(f"Randomly selected daily target time: {self.daily_target_time}\n")

        try:
            channel = self.state.get_active_channel()
            self.client.chat_postMessage(channel=channel, text="time set for today is " + self.daily_target_time)
        except Exception as e:
            print(f"Error posting initial time message: {e}")

        time.sleep(1)  # allow logging to finish before the loop begins

        try:
            while True:
                current_time = display_current_time()
                channel = self.state.get_active_channel()
                if current_time == "8:04:00 AM":
                    try:
                        self.client.chat_postMessage(channel=channel, text="send prompt")
                        # begin collecting responses for a short window
                        self.start_response_collection()
                    except Exception as e:
                        print(f"Error posting 12:00:00 PM message: {e}")

                if current_time == self.daily_target_time:
                    try:
                        self.client.chat_postMessage(channel=channel, text="random time hit")
                        print(f"Random time hit: {self.daily_target_time}")
                        # optional: also treat this as a prompt event
                        self.start_response_collection()
                    except Exception as e:
                        print(f"Error posting random time hit message: {e}")

                time.sleep(1)

        except KeyboardInterrupt:
            try:
                channel = self.state.get_active_channel()
                self.client.chat_postMessage(channel=channel, text="bot offline")
            except Exception as e:
                print(f"Error posting offline message: {e}")
            print(" Program stopped by user.")

    # response collection helpers
    def start_response_collection(self):
        self.last_prompt_time = datetime.now()
        self.responses = []  # clear previous responses

    def is_within_response_window(self, window_seconds: int) -> bool:
        """Return True if a message arriving right now should be treated as a response."""
        return datetime.now() - self.last_prompt_time <= timedelta(seconds=window_seconds)

    def record_response(self, event: dict, window_seconds: int):
        """Record the user id and text from ``event`` when within the window.

        We only retain ``user`` and ``text`` fields to avoid storing the full
        Slack event payload.  Events missing either field are ignored.
        """
        if self.is_within_response_window(window_seconds):
            user = event.get("user")
            text = event.get("text")
            if user is not None and text is not None:
                self.responses.append({"user": user, "text": text})
