# src/bot/posting.py
from datetime import datetime
from typing import Optional

from services.prompt_service import get_random_prompt_text, mark_prompt_asked


def display_current_time() -> str:
    now = datetime.now()
    current_time_str = now.strftime("%I:%M:%S %p")
    print(f"\rCurrent Time: {current_time_str}", end="")
    return current_time_str


def post_csv_prompt(client, channel: str, prefix_text: Optional[str] = None) -> None:
    prompt_id, prompt_text = get_random_prompt_text()
    mark_prompt_asked(prompt_id)

    msg = prompt_text
    if prefix_text:
        msg = f"{prefix_text}\n\n{prompt_text}"

    client.chat_postMessage(channel=channel, text=msg)