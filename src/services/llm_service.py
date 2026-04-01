import os
from typing import Optional

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
            "respond with ONLY a single emoji that captures the sentiment or content. "
            "No text, no explanation, just one emoji character."
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
        
        emoji = response.choices[0].message.content.strip()
        
        # Validate it's actually an emoji (rough check)
        if emoji and len(emoji) <= 2:
            return emoji
        
        return None
        
    except Exception as e:
        print(f"[LLM] Error getting emoji reaction: {e}")
        return None
