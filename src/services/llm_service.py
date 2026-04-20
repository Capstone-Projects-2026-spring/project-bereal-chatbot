import base64
import os
import re
from typing import Any, List, Optional

import requests

try:
    from groq import Groq
except ImportError:
    Groq = None


# Common Slack emoji names that work reliably
VALID_SLACK_EMOJI_NAMES = {
    "smiley" , "laughing", "sweat_smile",
    "rolling_on_the_floor_laughing", "joy", "slightly_smiling_face",
    "upside_down_face", "melting_face", "wink", "heart_eyes",
    "star-struck", "relaxed", "yum", "zany_face", "money_mouth_face",
    "hugging_face", "thinking_face", "saluting_face","grimacing",
    "face_exhaling", "shaking_face", "relieved", "pensive", "sleepy",
    "face_with_thermometer", "face_with_head_bandage", "nauseated_face",
    "cold_face", "woozy_face", "dizzy_face", "exploding_head", "face_with_cowboy_hat",
    "partying_face", "smiling_face_with_3_hearts", "sunglasses", "nerd_face",
    "confused", "worried", "slightly_frowning_face", "open_mouth",
    "hushed", "astonished", "flushed", "pleading_face", "face_holding_back_tears",
    "frowning", "fearful", "sob", "scream", "confounded", "disappointed",
    "triumph", "angry", "rage", "face_with_symbols_on_mouth", "smiling_imp",
    "skull", "ghost", "alien", "space_invader", "robot_face", "smiley_cat",
    "see_no_evil", "hear_no_evil", "speak_no_evil", "thumbsup", "thumbsdown",
    "gift_heart", "two_hearts", "heart", "100", "eyes", "clap", "wave",
    "heart_hands"
}


def get_reaction_emoji(
    message_text: str,
    prompt_text: Optional[str] = None,
    image_urls: Optional[List[str]] = None,
    slack_token: Optional[str] = None,
) -> Optional[str]:
    """
    Uses Groq's free LLM API to pick a relevant Slack emoji reaction.

    Args:
        message_text: The user's response message
        prompt_text: Optional original prompt they were responding to
        image_urls: Optional list of Slack private image URLs attached to the message
        slack_token: Bot token used to download private Slack images

    Returns:
        A valid Slack emoji name (like "thumbsup"), or None if the API call fails or is disabled
    """
    # Check if LLM reactions are enabled
    if os.getenv("LLM_REACTIONS_ENABLED", "true").lower() != "true":
        return None
    
    # Skip empty messages (unless images are provided)
    if (not message_text or not message_text.strip()) and not image_urls:
        return None
    
    # Check if Groq is installed
    if Groq is None:
        print("[LLM] Groq not installed. Install with: pip install groq")
        return None
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("[LLM] GROQ_API_KEY not set in .env file")
        return None
    
    try:
        client = Groq(api_key=api_key)
        
        emoji_names_str = ", ".join(sorted(list(VALID_SLACK_EMOJI_NAMES)[:50]))  # Show sample
        system_prompt = (
            "You are an emoji expert. Given a user's response to a prompt, "
            "respond with ONLY a single Slack emoji name that captures the sentiment or content. "
            f"The name must be a valid Slack emoji name from the following list: {emoji_names_str}. "
            "No colons, no Unicode characters, no explanation. "
            "Examples of valid responses: heart, tada, fire, slightly_smiling_face, origami"
        )
        
        text_parts: List[str] = []
        if message_text and message_text.strip():
            text_parts.append(f"User response: {message_text}")
        if prompt_text:
            text_parts.append(f"Original prompt: {prompt_text}")
        if image_urls and not text_parts:
            text_parts.append("User posted an image. React with an appropriate emoji.")

        # Build message content — use vision format when images are present
        user_content: Any
        encoded_images = []
        if image_urls:
            for url in image_urls:
                try:
                    headers = {"Authorization": f"Bearer {slack_token}"} if slack_token else {}
                    resp = requests.get(url, headers=headers, timeout=10)
                    resp.raise_for_status()
                    mime = resp.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
                    b64 = base64.b64encode(resp.content).decode()
                    encoded_images.append(f"data:{mime};base64,{b64}")
                except Exception as img_err:
                    print(f"[LLM] Could not download image for vision: {img_err}")

        if encoded_images:
            user_content = [{"type": "text", "text": " ".join(text_parts)}]
            for data_url in encoded_images:
                user_content.append({"type": "image_url", "image_url": {"url": data_url}})
        else:
            user_content = " ".join(text_parts)

        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",  # Free model, very fast
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.7,
            max_tokens=20
        )
        
        emoji = response.choices[0].message.content.strip().strip(":")
        print(f"[LLM] Got emoji reaction: {emoji}")
        
        # Validate the Slack emoji name (letters, numbers, underscores, hyphens)
        if emoji and re.match(r'^[a-z0-9_\-]+$', emoji):
            return emoji
        
        return None
        
    except Exception as e:
        print(f"[LLM] Error getting emoji reaction: {e}")
        return None


def get_reply_message(
    message_text: str,
    image_urls: Optional[List[str]] = None,
    slack_token: Optional[str] = None,
) -> Optional[str]:
    """
    Uses Groq's LLM API to generate a short, casual reply to a user's message.

    Args:
        message_text: The user's message text
        image_urls: Optional list of Slack private image URLs attached to the message
        slack_token: Bot token used to download private Slack images

    Returns:
        A short reply string, or None if the API call fails or is disabled
    """
    if (not message_text or not message_text.strip()) and not image_urls:
        return None

    if Groq is None:
        print("[LLM] Groq not installed. Install with: pip install groq")
        return None

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("[LLM] GROQ_API_KEY not set in .env file")
        return None

    try:
        client = Groq(api_key=api_key)

        system_prompt = (
            "You are a friendly Slack bot that occasionally chimes in on conversations. "
            "Generate a very short, casual reply (1-2 sentences max) to the user's message. "
            "Be warm, witty, and conversational. Use a Slack emoji at the end if it fits naturally. "
            "Do NOT be overly enthusiastic or robotic. Match the energy of the message."
        )

        text_parts: List[str] = []
        if message_text and message_text.strip():
            text_parts.append(message_text)
        if image_urls and not text_parts:
            text_parts.append("The user posted an image. Write a short, casual comment about it.")

        # Build message content — use vision format when images are present
        user_content: Any
        encoded_images = []
        if image_urls:
            for url in image_urls:
                try:
                    headers = {"Authorization": f"Bearer {slack_token}"} if slack_token else {}
                    resp = requests.get(url, headers=headers, timeout=10)
                    resp.raise_for_status()
                    mime = resp.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
                    b64 = base64.b64encode(resp.content).decode()
                    encoded_images.append(f"data:{mime};base64,{b64}")
                except Exception as img_err:
                    print(f"[LLM] Could not download image for reply: {img_err}")

        if encoded_images:
            user_content = [{"type": "text", "text": " ".join(text_parts)}]
            for data_url in encoded_images:
                user_content.append({"type": "image_url", "image_url": {"url": data_url}})
        else:
            user_content = " ".join(text_parts)

        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.8,
            max_tokens=100
        )

        reply = response.choices[0].message.content.strip()
        print(f"[LLM] Got reply message: {reply}")
        return reply if reply else None

    except Exception as e:
        print(f"[LLM] Error getting reply message: {e}")
        return None


def get_social_connector_message(user1_id: str, user2_id: str, shared_tags: List[str]) -> str:
    """
    Uses Groq to generate a friendly channel message pairing two users with shared interests.
    Falls back to a default message if the API call fails or is disabled.
    """
    fallback = (
        f"Hey <@{user1_id}> and <@{user2_id}>, you two might have a lot in common — "
        f"try getting to know each other more! :wave:"
    )

    if Groq is None:
        return fallback

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return fallback

    tags_str = ", ".join(shared_tags)

    try:
        client = Groq(api_key=api_key)

        system_prompt = (
            "You are a friendly Slack bot that helps teammates connect. "
            "Generate a single short, warm message pairing two Slack users based on shared interests. "
            "Use Slack user mention format exactly as provided: <@USER_ID>. "
            "Keep it to 1-2 sentences. Be casual and encouraging. End with a relevant Slack emoji."
        )

        user_msg = (
            f"Generate a connection message for <@{user1_id}> and <@{user2_id}> "
            f"who both like: {tags_str}."
        )

        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.8,
            max_tokens=100,
        )

        msg = response.choices[0].message.content.strip()
        return msg if msg else fallback

    except Exception as e:
        print(f"[LLM] Error getting social connector message: {e}")
        return fallback
