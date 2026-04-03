# src/bot/posting.py
from datetime import datetime
from typing import Optional

from typing import Optional
from services.prompt_service import get_random_prompt_text, get_random_prompt_by_topic, mark_prompt_asked
from services.mongo_service import get_tracker
import random

def display_current_time() -> str:
    now = datetime.now()
    return now.strftime("%I:%M:%S %p")


def post_csv_prompt(client, channel: str, team_id: str = "", prefix_text: Optional[str] = None, topic: Optional[str] = None, active_tags: Optional[set] = None) -> None:

    if topic:
        prompt_id, prompt_text, tags = get_random_prompt_by_topic(topic)
    else:
        prompt_id, prompt_text, tags = get_random_prompt_text(active_tags=active_tags)

    mark_prompt_asked(prompt_id)

    tracker = get_tracker()
    if tracker:
        tracker.record_prompt_sent(prompt_id, prompt_text, tags, channel, team_id)

    msg = f">{prompt_text}"
    if prefix_text:
        msg = f"### **{prefix_text.upper()}**\n\n>{prompt_text}"

    msg_block = randomize_message_block(msg)

    client.chat_postMessage(channel=channel, blocks=msg_block,text=msg)

def randomize_message_block(message):
    num = random.randint(1,10)
    headerMSGs = [
        ":bangbang: NEW VIBE CHECK :bangbang:",
        ":bangbang: VIBE CHECK :bangbang:",
        ":bangbang: VIBE CHECK! :bangbang:",
        ":bangbang: VIBE CHECK ALERT :bangbang:",
        ":interrobang: NEW VIBE CHECK :interrobang:",
        ":interrobang: VIBE CHECK :interrobang:",
        ":interrobang: VIBE CHECK! :interrobang:",
        ":interrobang: VIBE CHECK ALERT :interrobang:",
        ":exclamation: NEW VIBE CHECK :exclamation:",
        ":exclamation: VIBE CHECK :exclamation:",
        ":exclamation: VIBE CHECK! :exclamation:",
        ":exclamation: VIBE CHECK ALERT :exclamation:",
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