# src/bot/posting.py
from datetime import datetime
from typing import Optional

from services.prompt_service import get_random_prompt_text, mark_prompt_asked
from services.mongo_service import get_tracker


def display_current_time() -> str:
    now = datetime.now()
    return now.strftime("%I:%M:%S %p")


def post_csv_prompt(client, channel: str, prefix_text: Optional[str] = None) -> None:
    prompt_id, prompt_text, tags = get_random_prompt_text()
    mark_prompt_asked(prompt_id)

    tracker = get_tracker()
    if tracker:
        tracker.record_prompt_sent(prompt_id, prompt_text, tags)

    msg = prompt_text
    if prefix_text:
        msg = f"{prefix_text}\n\n{prompt_text}"

    client.chat_postMessage(channel=channel, text=msg)