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
    users_with_tags = [user for user in all_users if user.get("tags")]

    if len(users_with_tags) < 2:
        return None, None, []

    matching_pairs = []
    for first_index in range(len(users_with_tags)):
        for second_index in range(first_index + 1, len(users_with_tags)):
            first_user = users_with_tags[first_index]
            second_user = users_with_tags[second_index]
            shared_tags = sorted(set(first_user["tags"]) & set(second_user["tags"]))
            if shared_tags:
                matching_pairs.append((first_user["user_id"], second_user["user_id"], shared_tags))

    if not matching_pairs:
        return None, None, []

    return random.choice(matching_pairs)


def send_social_connector_message(client, channel: str, team_id: str) -> None:
    """
    Find two users with shared interest tags and post a soft introduction in the channel.
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
    except Exception as error:
        logger.error("[SOCIAL] Failed to post connector message: %s", error)
