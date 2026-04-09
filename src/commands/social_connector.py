# src/commands/social_connector.py
import logging
import random
from typing import Optional

logger = logging.getLogger(__name__)


def find_matching_pair(team_id: str) -> tuple[Optional[str], Optional[str], list[str]]:
    """
    Find two users from the workspace with at least one shared interest tag.
    Returns (user1_id, user2_id, shared_tags) or (None, None, []) if no pair is found.
    """
    from services.mongo_service import get_all_user_interests

    all_users = get_all_user_interests(team_id)
    users_with_tags = [u for u in all_users if u.get("tags")]

    if len(users_with_tags) < 2:
        return None, None, []

    matching_pairs = []
    for i in range(len(users_with_tags)):
        for j in range(i + 1, len(users_with_tags)):
            u1 = users_with_tags[i]
            u2 = users_with_tags[j]
            shared = list(set(u1["tags"]) & set(u2["tags"]))
            if shared:
                matching_pairs.append((u1["user_id"], u2["user_id"], shared))

    if not matching_pairs:
        return None, None, []

    user1_id, user2_id, shared_tags = random.choice(matching_pairs)
    return user1_id, user2_id, shared_tags


def send_social_connector_message(client, channel: str, team_id: str) -> None:
    """
    Find two users with shared interest tags and post a Groq-generated
    @mention message pairing them in the channel.
    """
    from services.llm_service import get_social_connector_message

    user1_id, user2_id, shared_tags = find_matching_pair(team_id)
    if not user1_id or not user2_id:
        logger.info("[SOCIAL] No matching pair found for team %s", team_id)
        return

    message = get_social_connector_message(user1_id, user2_id, shared_tags)
    try:
        client.chat_postMessage(channel=channel, text=message)
        logger.info("[SOCIAL] Posted connector message for %s and %s", user1_id, user2_id)
    except Exception as e:
        logger.error("[SOCIAL] Failed to post connector message: %s", e)
