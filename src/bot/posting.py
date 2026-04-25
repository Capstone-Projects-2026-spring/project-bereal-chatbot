# src/bot/posting.py
from datetime import datetime
from typing import Optional

from typing import Optional
from services.prompt_service import get_random_prompt_text, get_random_prompt_by_topic, mark_prompt_asked
from services.mongo_service import get_tracker
import random

def display_current_time() -> str:
    """Return the current local time formatted as HH:MM:SS AM/PM."""
    now = datetime.now()
    return now.strftime("%I:%M:%S %p")


def post_csv_prompt(client, channel: str, team_id: str = "", prefix_text: Optional[str] = None, topic: Optional[str] = None, active_tags: Optional[set] = None, footnote_text: Optional[str] = None, response_type: Optional[str] = "image") -> None:
    """Select a prompt from the CSV, record it as sent, and post it to the channel with a randomized block layout."""
    # "any" means no filter — pass None to the prompt service
    rt = None if response_type == "any" else response_type

    if topic:
        prompt_id, prompt_text, tags = get_random_prompt_by_topic(topic, response_type=rt)
    else:
        prompt_id, prompt_text, tags = get_random_prompt_text(response_type=rt, active_tags=active_tags)

    mark_prompt_asked(prompt_id)

    tracker = get_tracker()
    if tracker:
        tracker.record_prompt_sent(prompt_id, prompt_text, tags, channel, team_id)

    if rt == "image":
        cta = "\n\n:camera: *Reply with a photo — don't think, just post!*"
    elif rt == "text":
        cta = "\n\n:speech_balloon: *Share your answer below!*"
    else:
        cta = ""

    msg = f">{prompt_text}{cta}"
    if prefix_text:
        msg = f"### **{prefix_text.upper()}**\n\n>{prompt_text}{cta}"

    if footnote_text:
        msg += f"\n\n\n```{footnote_text}```"

    msg_block = randomize_message_block(msg)

    resp = client.chat_postMessage(channel=channel, blocks=msg_block, text=msg)
    return resp.get("ts")


def post_custom_prompt(client, prompt_text: str, channel: str, team_id: str = "", prefix_text: Optional[str] = None, footnote_text: Optional[str] = None) -> Optional[str]:
    """Post a user-authored prompt text to the channel."""
    msg = f">{prompt_text}"
    if prefix_text:
        msg = f"### **{prefix_text.upper()}**\n\n>{prompt_text}"
    if footnote_text:
        msg += f"\n\n\n```{footnote_text}```"

    msg_block = randomize_message_block(msg)
    resp = client.chat_postMessage(channel=channel, blocks=msg_block, text=msg)
    return resp.get("ts")


def randomize_message_block(message):
    """Build a Slack Block Kit payload, randomly including a GIF header image 90% of the time."""
    num = random.randint(1,10)
    headerMSGs = [
        ":camera: VIBE CHECK :camera:",
        ":camera_with_flash: VIBE CHECK :camera_with_flash:",
        ":camera: POST YOUR SHOT :camera:",
        ":camera_with_flash: POST YOUR SHOT :camera_with_flash:",
        ":camera: IT'S VIBE CHECK TIME :camera:",
        ":camera_with_flash: IT'S VIBE CHECK TIME :camera_with_flash:",
        ":camera: DROP YOUR PHOTO :camera:",
        ":camera_with_flash: DROP YOUR PHOTO :camera_with_flash:",
        ":camera: SHOW YOUR VIBE :camera:",
        ":camera_with_flash: SHOW YOUR VIBE :camera_with_flash:",
        ":camera: CAPTURE THE MOMENT :camera:",
        ":camera_with_flash: CAPTURE THE MOMENT :camera_with_flash:",
    ]

    image_lists = [
        "https://media1.tenor.com/m/1CcXIDK6YboAAAAC/the-simpsons-bart.gif",
        "https://media1.tenor.com/m/hV2TZljEW1kAAAAd/vibby-vibby-vibes.gif",
        "https://media.tenor.com/y0hD2LSxx_8AAAAi/vibe.gif",
        "https://media.tenor.com/X9mVHTwAHXoAAAAi/vibes-woodstock.gif",
        "https://media1.tenor.com/m/LCpcrdtI0GYAAAAd/vibing-st6.gif",
        "https://media1.tenor.com/m/3fWNoUgRYFEAAAAd/cat-vibe-cat-meme.gif",
        "https://media1.tenor.com/m/Tfm5oTF9Xt0AAAAd/cat-sunglasses.gif",
        "https://media1.tenor.com/m/dEjkUvV_ieoAAAAC/dance-victro.gif",
        "https://media1.tenor.com/m/HCyNMWQv868AAAAC/good-night.gif",
        "https://media.tenor.com/sbfBfp3FeY8AAAAi/oia-uia.gif",
    ]
    msg_block = []
    if num <= 1:
         msg_block = [
          {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": headerMSGs[random.randint(0, len(headerMSGs) - 1)] ,
                        "emoji": True
                    },
                    "level": 2
                },
                {
                    "type": "divider"
                },
                {
                    "type": "markdown",
                    "text": message
                }
            ]
    else:
         msg_block = [
          {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": headerMSGs[random.randint(0, len(headerMSGs) - 1)],
                        "emoji": True
                    },
                    "level": 2
                },
                {
                    "type": "divider"
                },
                {
                    "type": "image",
                    "image_url": image_lists[random.randint(0, len(image_lists) - 1)],
                    "alt_text": "an image relating to the vibes."
                },
                {
                    "type": "markdown",
                    "text": message
                }
            ]
    return msg_block
