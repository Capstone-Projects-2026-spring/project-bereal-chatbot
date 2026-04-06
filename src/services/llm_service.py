import os
from typing import Optional

try:
    from groq import Groq
except ImportError:
    Groq = None


# Common Slack emoji names that work reliably
VALID_SLACK_EMOJI_NAMES = {
    "thumbsup", "heart", "laughing", "thinking_face", "sunglasses",
    "fire", "sparkles", "tada", "clap", "wave", "pray", "+1",
    "smile", "smiley", "grinning", "joy", "sweat_smile",
    "relaxed", "unamused", "face_with_rolling_eyes", "thinking_face", "angry",
    "disappointed", "worried", "cry", "cool", "rocket", "star",
    "boom", "bulb", "books", "brain", "computer", "keyboard",
    "love_letter", "mailbox", "memo", "clipboard", "chart_with_upwards_trend",
    "coffee", "pizza", "apple", "banana", "tropical_drink", "beers",
    "beer", "wine_glass", "cocktail", "camera", "video_camera", 
    "musical_note", "speaker", "bell", "loudspeaker", "game_die", "dart",
    "basketball", "soccer", "football", "baseball", "tennis",
    "golfer", "surfer", "skateboard", "swimmer", "person_climbing",
    "person_with_ball", "person_in_lotus_position",
    "raised_hands", "handshake", "airplane", "car", "train", "ship",
    "mouse", "keyboard", "printer", "phone", "iphone", "telephone",
    "alarm_clock", "hourglass", "calendar", "sunrise", "city_sunset", "rainbow",
    "snow_cloud", "cloud", "sun_behind_cloud", "umbrella", "umbrella_on_ground",
    "zap", "droplet", "ocean", "earth_americas",
    "mountain", "volcano", "evergreen_tree",
    "palm_tree", "cactus", "tulip", "rose", "sunflower", "hibiscus",
    "cherry_blossom", "bouquet", "corn", "hot_pepper", "watermelon",
    "strawberry", "birthday", "cake", "lollipop", "doughnut",
    "candy", "cookie", "checkered_flag", "crown", "trophy", "purse", "gift",
    "gem", "gear", "wrench", "crossed_swords", "shield",
    "boxing_glove"
}


def get_reaction_emoji(message_text: str, prompt_text: Optional[str] = None) -> Optional[str]:
    """
    Uses Groq's free LLM API to pick a relevant Slack emoji reaction.
    
    Args:
        message_text: The user's response message
        prompt_text: Optional original prompt they were responding to
        
    Returns:
        A valid Slack emoji name (like "thumbsup"), or None if the API call fails or is disabled
    """
    # Check if LLM reactions are enabled
    if os.getenv("LLM_REACTIONS_ENABLED", "true").lower() != "true":
        return None
    
    # Skip empty messages
    if not message_text or not message_text.strip():
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
            f"You are an emoji expert. Given a user's response to a prompt, "
            f"respond with ONLY a single Slack emoji name (without colons) that captures the sentiment or content. "
            f"Pick one from valid Slack emoji names list: {emoji_names_str}. "
            f"No text, no explanation, just the emoji name. Example response: 'thumbsup' or 'heart' or 'laughing'"
        )
        
        user_msg = f"User response: {message_text}"
        if prompt_text:
            user_msg += f"\n\nOriginal prompt: {prompt_text}"
        
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",  # Free model, very fast
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.7,
            max_tokens=20
        )
        
        emoji_name = response.choices[0].message.content.strip().lower()
        
        # Clean up the response (remove colons if they tried to use :emoji: format)
        emoji_name = emoji_name.strip(":")
        
        # Validate it's a recognized Slack emoji name
        if emoji_name in VALID_SLACK_EMOJI_NAMES:
            return emoji_name
        
        # If LLM returned something unrecognized, return None instead of risking an error
        if emoji_name and not emoji_name.isalnum() and emoji_name != "-1" and emoji_name != "+1":
            print(f"[LLM] Unrecognized emoji name returned: {emoji_name}")
        
        return None
        
    except Exception as e:
        print(f"[LLM] Error getting emoji reaction: {e}")
        return None
