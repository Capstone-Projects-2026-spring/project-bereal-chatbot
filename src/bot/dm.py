# src/bot/scheduler.py
import random
import time
from datetime import datetime, date

from slack_sdk import WebClient

from services.time_library import preSet_time_library
from bot.posting import display_current_time, post_csv_prompt, post_custom_prompt
def load_prompts():
    prompts = []
    with open(PROMPTS_CSV, "r") as f:
        for line in f:
            prompt = line.strip()
            if prompt:
                prompts.append(prompt)
    return prompts

# whenever a user doesnt respond to a vibecheck, we log that in a jsonl file with the following format:

# {
#     "timestamp": "2023-08-01T12:00:00Z",
#     "user_id": "U12345678",
#     "prompt": "How are you feeling today?",
#     "response": null
# } 
def log_no_response(user_id, prompt):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user_id": user_id,
        "prompt": prompt,
        "response": None
    }

def send_dm(client: WebClient, user_id: str, prompt: str):
    try:
        response = client.chat_postMessage(
            channel=user_id,
            text=prompt
        )
        return response
    except Exception as e:
        print(f"Error sending DM to {user_id}: {e}")
        return None
