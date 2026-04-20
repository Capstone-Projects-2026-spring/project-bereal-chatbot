# src/commands/mentor_mentee_command.py
import logging

from bot.state import get_team_id

logger = logging.getLogger(__name__)

_HELP_TEXT = (
    "*Mentor-Mentee Program* :handshake:\n\n"
    "• `/mentor signup mentor` — join as a mentor\n"
    "• `/mentor signup mentee` — join as a mentee\n"
    "• `/mentor status` — see your current pairing\n"
    "• `/mentor leave` — leave the program\n"
    "• `/mentor match` — _(admin)_ run matching now\n"
)


def register_mentor_mentee_command(bolt_app, state_manager):

    @bolt_app.command("/mentor")
    def handle_mentor_command(ack, body, respond, client):
        ack()
        team_id = get_team_id(body)
        user_id = body["user_id"]
        text = (body.get("text") or "").strip().lower()

        if text.startswith("signup"):
            parts = text.split()
            if len(parts) < 2 or parts[1] not in ("mentor", "mentee"):
                respond("Usage: `/mentor signup mentor` or `/mentor signup mentee`")
                return
            _handle_signup(user_id, team_id, parts[1], respond)

        elif text == "status":
            _handle_status(user_id, team_id, respond)

        elif text == "leave":
            _handle_leave(user_id, team_id, respond)

        elif text == "match":
            _handle_match(client, team_id, respond)

        else:
            respond(_HELP_TEXT)


def _handle_signup(user_id: str, team_id: str, role: str, respond) -> None:
    from services.mentor_service import get_registration, upsert_registration
    from services.mongo_service import get_user_interests

    existing = get_registration(team_id, user_id)
    if existing:
        respond(
            f":x: You're already signed up as a *{existing['role']}*. "
            f"Use `/mentor leave` first if you'd like to change roles."
        )
        return

    interests = get_user_interests(team_id, user_id)
    upsert_registration(team_id, user_id, role, interests)

    partner_label = "mentee" if role == "mentor" else "mentor"
    respond(
        f":white_check_mark: You've signed up as a *{role}*!\n\n"
        f"You'll be paired with a {partner_label} at the next matching round (every Monday). "
        f"Use `/mentor status` to check your pairing anytime."
    )
    logger.info("[MENTOR] User %s signed up as %s in team %s", user_id, role, team_id)


def _handle_status(user_id: str, team_id: str, respond) -> None:
    from services.mentor_service import get_registration

    reg = get_registration(team_id, user_id)
    if not reg:
        respond(
            ":information_source: You're not signed up yet. "
            "Use `/mentor signup mentor` or `/mentor signup mentee` to join."
        )
        return

    role = reg["role"]
    matched_with = reg.get("matched_with")
    if matched_with:
        partner_label = "mentee" if role == "mentor" else "mentor"
        date_str = (reg.get("matched_at") or "")[:10]
        date_note = f" (since {date_str})" if date_str else ""
        respond(
            f":handshake: You are a *{role}*, paired with <@{matched_with}> "
            f"as your {partner_label}{date_note}."
        )
    else:
        respond(
            f":hourglass_flowing_sand: You're signed up as a *{role}* and waiting to be matched. "
            f"Matching runs every Monday morning."
        )


def _handle_leave(user_id: str, team_id: str, respond) -> None:
    from services.mentor_service import get_registration, remove_registration, clear_pair

    reg = get_registration(team_id, user_id)
    if not reg:
        respond(":information_source: You're not currently signed up for the mentor-mentee program.")
        return

    partner_id = reg.get("matched_with")
    if partner_id:
        clear_pair(team_id, user_id, partner_id)

    remove_registration(team_id, user_id)
    respond(
        ":wave: You've been removed from the mentor-mentee program. "
        "Your pairing has been cleared and your partner has been returned to the unmatched pool."
    )
    logger.info("[MENTOR] User %s left the program in team %s", user_id, team_id)


def _handle_match(client, team_id: str, respond) -> None:
    from services.mentor_service import get_all_unmatched, run_matching

    mentors, mentees = get_all_unmatched(team_id)
    if not mentors or not mentees:
        respond(":x: Not enough unmatched mentors or mentees to form pairs right now.")
        return

    pairs = run_matching(team_id, mentors, mentees)
    if not pairs:
        respond(":x: Could not find any compatible pairs.")
        return

    for mentor_id, mentee_id, shared_tags in pairs:
        _notify_new_pair(client, mentor_id, mentee_id, shared_tags)

    respond(f":tada: Matched {len(pairs)} pair(s)! Both users in each pair have been DM'd.")
    logger.info("[MENTOR] Matched %d pairs for team %s", len(pairs), team_id)


def _notify_new_pair(client, mentor_id: str, mentee_id: str, shared_tags: list) -> None:
    """DM both users to introduce them to each other."""
    from services.llm_service import get_mentor_intro_message

    mentor_msg, mentee_msg = get_mentor_intro_message(mentor_id, mentee_id, shared_tags)
    for user_id, msg in [(mentor_id, mentor_msg), (mentee_id, mentee_msg)]:
        try:
            client.chat_postMessage(channel=user_id, text=msg)
        except Exception as e:
            logger.error("[MENTOR] Failed to DM %s: %s", user_id, e)


def send_weekly_checkin(client, team_id: str) -> None:
    """DM each mentor-mentee pair a weekly conversation starter."""
    from services.mentor_service import get_all_pairs
    from services.prompt_service import get_random_prompt_text

    pairs = get_all_pairs(team_id)
    if not pairs:
        return

    for mentor_id, mentee_id in pairs:
        _, prompt_text, _ = get_random_prompt_text()
        msg = (
            f":wave: *Weekly Mentor-Mentee Check-in!*\n\n"
            f"Here's a conversation starter for you and your partner this week:\n\n"
            f"_{prompt_text}_"
        )
        for user_id in (mentor_id, mentee_id):
            try:
                client.chat_postMessage(channel=user_id, text=msg)
            except Exception as e:
                logger.error("[MENTOR] Failed to send weekly check-in to %s: %s", user_id, e)

    logger.info("[MENTOR] Sent weekly check-ins for %d pair(s) in team %s", len(pairs), team_id)
