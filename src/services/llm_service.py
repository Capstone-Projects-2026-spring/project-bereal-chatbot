import os
import re
from typing import Optional, List

try:
    from groq import Groq
except ImportError:
    Groq = None


def get_reaction_emoji(message_text: str, prompt_text: Optional[str] = None) -> Optional[str]:
    """
    Uses Groq's free LLM API to pick a relevant emoji reaction.
    
    Args:
        message_text: The user's response message
        prompt_text: Optional original prompt they were responding to
        
    Returns:
        A single emoji string, or None if the API call fails or is disabled
    """
    # Check if LLM reactions are enabled
    if os.getenv("LLM_REACTIONS_ENABLED", "true").lower() != "true":
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
        
        system_prompt = (
            "You are an emoji expert. Given a user's response to a prompt, "
            "respond with ONLY a single Slack emoji name that captures the sentiment or content. "
            "The name must be a valid Slack emoji name: lowercase letters, numbers, underscores, and hyphens only. "
            "No colons, no Unicode characters, no text, no explanation. "
            "Examples of valid responses: heart, tada, fire, slightly_smiling_face, origami"
        )
        
        user_msg = f"User response: {message_text}"
        if prompt_text:
            user_msg += f"\n\nOriginal prompt: {prompt_text}"
        
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",  # Free model, very fast
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.7,
            max_tokens=10
        )
        
        emoji = response.choices[0].message.content.strip().strip(":")
        
        # Validate it looks like a Slack emoji name (letters, numbers, underscores, hyphens)
        if emoji and re.match(r'^[a-z0-9_\-]+$', emoji):
            return emoji
        
        return None
        
    except Exception as e:
        print(f"[LLM] Error getting emoji reaction: {e}")
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
