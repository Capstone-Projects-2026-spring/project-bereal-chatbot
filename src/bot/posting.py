# src/bot/posting.py
from datetime import datetime
from typing import Optional

from services.prompt_service import get_random_prompt_text, mark_prompt_asked

_last_printed_minute: str = ""


def display_current_time() -> str:
    global _last_printed_minute
    now = datetime.now()
    current_time_str = now.strftime("%I:%M:%S %p")
    current_minute = now.strftime("%I:%M %p")
    if current_minute != _last_printed_minute:
        print(f"[SCHEDULER] Current Time: {current_time_str}")
        _last_printed_minute = current_minute
    return current_time_str


def post_csv_prompt(client, channel: str, prefix_text: Optional[str] = None) -> None:
    prompt_id, prompt_text = get_random_prompt_text()
    mark_prompt_asked(prompt_id)

    msg = prompt_text
    if prefix_text:
        msg = f"{prefix_text}\n\n{prompt_text}"

    client.chat_postMessage(channel=channel, text=msg)