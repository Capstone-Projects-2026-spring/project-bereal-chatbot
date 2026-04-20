# src/commands/mentor_mentee_command.py
import logging

from bot.state import get_team_id

logger = logging.getLogger(__name__)

_HELP_TEXT = (
    "*Mentor-Mentee Program* :handshake:\n\n"
    "• `/mentor signup mentor` — join as a mentor (opens a profile form)\n"
    "• `/mentor signup mentee` — join as a mentee (opens a profile form)\n"
    "• `/mentor status` — see your current pairing\n"
    "• `/mentor leave` — leave the program\n"
    "• `/mentor admin` — _(admin)_ view all profiles & manually pair users\n"
    "• `/mentor match` — _(admin)_ auto-match all unmatched users by interests\n"
)


def register_mentor_mentee_command(bolt_app, state_manager):

    # ------------------------------------------------------------------ #
    #  Slash command router                                                #
    # ------------------------------------------------------------------ #
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
            from services.mentor_service import get_registration
            existing = get_registration(team_id, user_id)
            if existing:
                respond(
                    f":x: You're already signed up as a *{existing['role']}*. "
                    f"Use `/mentor leave` first if you'd like to change roles."
                )
                return
            _open_signup_modal(client, body, parts[1], team_id)

        elif text == "status":
            _handle_status(user_id, team_id, respond)

        elif text == "leave":
            _handle_leave(user_id, team_id, respond)

        elif text == "admin":
            _open_admin_modal(client, body, team_id)

        elif text == "match":
            _handle_match(client, team_id, respond)

        else:
            respond(_HELP_TEXT)

    # ------------------------------------------------------------------ #
    #  Signup modal submission                                             #
    # ------------------------------------------------------------------ #
    @bolt_app.view("mentor_signup_modal")
    def handle_signup_modal(ack, body, client):
        ack()
        metadata = body["view"].get("private_metadata", "|")
        team_id, role = (metadata.split("|", 1) + [""])[:2]
        user_id = body["user"]["id"]
        values = body["view"]["state"]["values"]

        job_title = (values.get("job_title_block", {})
                     .get("job_title_input", {}).get("value") or "").strip()
        years_experience = (values.get("experience_block", {})
                            .get("experience_input", {}).get("value") or "").strip()
        bio = (values.get("bio_block", {})
               .get("bio_input", {}).get("value") or "").strip()

        from services.mentor_service import upsert_registration
        from services.mongo_service import get_user_interests
        interests = get_user_interests(team_id, user_id)
        upsert_registration(team_id, user_id, role, interests, job_title, years_experience, bio)

        partner_label = "mentee" if role == "mentor" else "mentor"
        try:
            client.chat_postMessage(
                channel=user_id,
                text=(
                    f":white_check_mark: You're signed up as a *{role}*!\n\n"
                    f"*Your profile:*\n"
                    f"• Role: {job_title}\n"
                    f"• Experience: {years_experience}\n"
                    f"• About you: _{bio}_\n\n"
                    f"An admin will review profiles and connect you with a {partner_label}. "
                    f"Use `/mentor status` to check anytime."
                )
            )
        except Exception as e:
            logger.error("[MENTOR] Failed to DM signup confirmation to %s: %s", user_id, e)

        logger.info("[MENTOR] User %s signed up as %s in team %s", user_id, role, team_id)

    # ------------------------------------------------------------------ #
    #  Admin panel modal submission (manual pair)                          #
    # ------------------------------------------------------------------ #
    @bolt_app.view("mentor_admin_modal")
    def handle_admin_modal(ack, body, client):
        ack()
        team_id = body["view"].get("private_metadata", "")
        values = body["view"]["state"]["values"]

        mentor_id = (values.get("pair_mentor_block", {})
                     .get("pair_mentor_select", {}).get("selected_user"))
        mentee_id = (values.get("pair_mentee_block", {})
                     .get("pair_mentee_select", {}).get("selected_user"))

        admin_id = body["user"]["id"]

        if not mentor_id or not mentee_id:
            # Admin closed without selecting — nothing to do
            return

        from services.mentor_service import get_registration, _get_col, _save_pair
        mentor_reg = get_registration(team_id, mentor_id)
        mentee_reg = get_registration(team_id, mentee_id)

        if not mentor_reg or mentor_reg["role"] != "mentor":
            try:
                client.chat_postMessage(
                    channel=admin_id,
                    text=f":x: <@{mentor_id}> is not registered as a mentor in this program."
                )
            except Exception:
                pass
            return

        if not mentee_reg or mentee_reg["role"] != "mentee":
            try:
                client.chat_postMessage(
                    channel=admin_id,
                    text=f":x: <@{mentee_id}> is not registered as a mentee in this program."
                )
            except Exception:
                pass
            return

        col = _get_col(team_id)
        _save_pair(col, mentor_id, mentee_id)
        shared_tags = list(
            set(mentor_reg.get("interests", [])) & set(mentee_reg.get("interests", []))
        )
        _notify_new_pair(client, mentor_id, mentee_id, shared_tags, team_id)

        try:
            client.chat_postMessage(
                channel=admin_id,
                text=(
                    f":tada: Paired <@{mentor_id}> (mentor) with <@{mentee_id}> (mentee)! "
                    f"Their group chat has been created."
                )
            )
        except Exception as e:
            logger.error("[MENTOR] Failed to confirm pair to admin %s: %s", admin_id, e)

        logger.info("[MENTOR] Admin %s paired %s + %s in team %s", admin_id, mentor_id, mentee_id, team_id)


# ------------------------------------------------------------------ #
#  Helper: open signup modal                                           #
# ------------------------------------------------------------------ #
def _open_signup_modal(client, body: dict, role: str, team_id: str) -> None:
    role_label = "Mentor" if role == "mentor" else "Mentee"
    bio_placeholder = (
        "What experience do you bring? What topics or skills can you help with?"
        if role == "mentor"
        else "What are you hoping to learn? What kind of guidance are you looking for?"
    )

    try:
        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "mentor_signup_modal",
                "private_metadata": f"{team_id}|{role}",
                "title": {"type": "plain_text", "text": f"Sign Up as {role_label}"},
                "submit": {"type": "plain_text", "text": "Sign Up"},
                "close": {"type": "plain_text", "text": "Cancel"},
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": (
                                f"Fill out your profile below. Admins use this to match you with "
                                f"the right {'mentee' if role == 'mentor' else 'mentor'}."
                            ),
                        },
                    },
                    {
                        "type": "input",
                        "block_id": "job_title_block",
                        "label": {"type": "plain_text", "text": "Job Title / Role"},
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "job_title_input",
                            "placeholder": {"type": "plain_text", "text": "e.g. Software Engineer, Product Designer, Data Analyst"},
                        },
                    },
                    {
                        "type": "input",
                        "block_id": "experience_block",
                        "label": {"type": "plain_text", "text": "Time in this role"},
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "experience_input",
                            "placeholder": {"type": "plain_text", "text": "e.g. 5 years, Less than 1 year, 6 months"},
                        },
                    },
                    {
                        "type": "input",
                        "block_id": "bio_block",
                        "label": {"type": "plain_text", "text": "About you"},
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "bio_input",
                            "multiline": True,
                            "placeholder": {"type": "plain_text", "text": bio_placeholder},
                        },
                    },
                ],
            },
        )
    except Exception as e:
        logger.error("[MENTOR] Failed to open signup modal for %s: %s", body.get("user_id"), e)


# ------------------------------------------------------------------ #
#  Helper: open admin panel modal                                      #
# ------------------------------------------------------------------ #
def _open_admin_modal(client, body: dict, team_id: str) -> None:
    from services.mentor_service import get_all_registrations

    all_regs = get_all_registrations(team_id)
    mentors = [r for r in all_regs if r["role"] == "mentor"]
    mentees = [r for r in all_regs if r["role"] == "mentee"]

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "Mentor-Mentee Program — Admin View"},
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*{len(mentors)} mentor(s)* and *{len(mentees)} mentee(s)* registered.\n"
                    f"Select a mentor and mentee below to pair them — this creates a group chat."
                ),
            },
        },
        {"type": "divider"},
    ]

    # --- Mentors ---
    blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": ":bust_in_silhouette: *Mentors*"}})
    if not mentors:
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": "_No mentors signed up yet._"}})
    else:
        for m in mentors:
            status = f":handshake: Paired with <@{m['matched_with']}>" if m.get("matched_with") else ":hourglass_flowing_sand: Unmatched"
            interests = ", ".join(m.get("interests", [])) or "none set"
            bio = (m.get("bio") or "").strip()
            bio_line = f"\n>_{bio}_" if bio else ""
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*<@{m['user_id']}>*  |  {m.get('job_title', 'N/A')}  |  {m.get('years_experience', 'N/A')}{bio_line}\n"
                        f"Interests: {interests}   {status}"
                    ),
                },
            })

    blocks.append({"type": "divider"})

    # --- Mentees ---
    blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": ":bust_in_silhouette: *Mentees*"}})
    if not mentees:
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": "_No mentees signed up yet._"}})
    else:
        for m in mentees:
            status = f":handshake: Paired with <@{m['matched_with']}>" if m.get("matched_with") else ":hourglass_flowing_sand: Unmatched"
            interests = ", ".join(m.get("interests", [])) or "none set"
            bio = (m.get("bio") or "").strip()
            bio_line = f"\n>_{bio}_" if bio else ""
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*<@{m['user_id']}>*  |  {m.get('job_title', 'N/A')}  |  {m.get('years_experience', 'N/A')}{bio_line}\n"
                        f"Interests: {interests}   {status}"
                    ),
                },
            })

    blocks.append({"type": "divider"})

    # --- Pair selector ---
    blocks += [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*Manually Pair Two Users*\nSelect a mentor and a mentee, then click Save."},
        },
        {
            "type": "input",
            "block_id": "pair_mentor_block",
            "optional": True,
            "label": {"type": "plain_text", "text": "Select Mentor"},
            "element": {
                "type": "users_select",
                "action_id": "pair_mentor_select",
                "placeholder": {"type": "plain_text", "text": "Choose a mentor..."},
            },
        },
        {
            "type": "input",
            "block_id": "pair_mentee_block",
            "optional": True,
            "label": {"type": "plain_text", "text": "Select Mentee"},
            "element": {
                "type": "users_select",
                "action_id": "pair_mentee_select",
                "placeholder": {"type": "plain_text", "text": "Choose a mentee..."},
            },
        },
    ]

    try:
        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "mentor_admin_modal",
                "private_metadata": team_id,
                "title": {"type": "plain_text", "text": "Mentor Admin Panel"},
                "submit": {"type": "plain_text", "text": "Pair & Create Chat"},
                "close": {"type": "plain_text", "text": "Close"},
                "blocks": blocks,
            },
        )
    except Exception as e:
        logger.error("[MENTOR] Failed to open admin modal: %s", e)


# ------------------------------------------------------------------ #
#  Helper: status                                                      #
# ------------------------------------------------------------------ #
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
            f"as your {partner_label}{date_note}.\n\n"
            f"*Your profile:* {reg.get('job_title', '')} · {reg.get('years_experience', '')}"
        )
    else:
        respond(
            f":hourglass_flowing_sand: You're signed up as a *{role}* and waiting to be matched.\n\n"
            f"*Your profile:* {reg.get('job_title', '')} · {reg.get('years_experience', '')}\n"
            f"_{reg.get('bio', '')}_"
        )


# ------------------------------------------------------------------ #
#  Helper: leave                                                       #
# ------------------------------------------------------------------ #
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
        "Your pairing has been cleared and your partner returned to the unmatched pool."
    )
    logger.info("[MENTOR] User %s left the program in team %s", user_id, team_id)


# ------------------------------------------------------------------ #
#  Helper: auto-match                                                  #
# ------------------------------------------------------------------ #
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
        _notify_new_pair(client, mentor_id, mentee_id, shared_tags, team_id)

    respond(f":tada: Matched {len(pairs)} pair(s)! Each pair has been given a group chat.")
    logger.info("[MENTOR] Auto-matched %d pairs for team %s", len(pairs), team_id)


# ------------------------------------------------------------------ #
#  Helper: notify pair (group DM)                                      #
# ------------------------------------------------------------------ #
def _notify_new_pair(client, mentor_id: str, mentee_id: str, shared_tags: list, team_id: str) -> None:
    """DM each person their partner's full profile, then try to open a group DM."""
    from services.mentor_service import get_registration, _get_col

    mentor_reg = get_registration(team_id, mentor_id) or {}
    mentee_reg = get_registration(team_id, mentee_id) or {}

    tags_line = f"\n:label: *Shared interests:* {', '.join(shared_tags)}" if shared_tags else ""

    def _profile_block(reg: dict) -> str:
        lines = []
        if reg.get("job_title"):
            lines.append(f"• *Role:* {reg['job_title']}")
        if reg.get("years_experience"):
            lines.append(f"• *Experience:* {reg['years_experience']}")
        if reg.get("bio"):
            lines.append(f"• *About:* _{reg['bio']}_")
        return "\n".join(lines) if lines else "_No profile details provided._"

    mentor_msg = (
        f":handshake: *You've been matched as a mentor!*\n\n"
        f"Your mentee is <@{mentee_id}>.\n\n"
        f"*Their profile:*\n{_profile_block(mentee_reg)}"
        f"{tags_line}\n\n"
        f"Reach out and introduce yourself — a quick message goes a long way!"
    )

    mentee_msg = (
        f":handshake: *You've been matched with a mentor!*\n\n"
        f"Your mentor is <@{mentor_id}>.\n\n"
        f"*Their profile:*\n{_profile_block(mentor_reg)}"
        f"{tags_line}\n\n"
        f"Don't be shy — feel free to reach out and say hello!"
    )

    for uid, msg in [(mentor_id, mentor_msg), (mentee_id, mentee_msg)]:
        try:
            client.chat_postMessage(channel=uid, text=msg)
            logger.info("[MENTOR] Sent pairing DM to %s", uid)
        except Exception as e:
            logger.error("[MENTOR] Failed to DM %s: %s", uid, e)

    # Also try to create a group DM — may not work without mpim:write permission
    channel_id = None
    try:
        result = client.conversations_open(users=f"{mentor_id},{mentee_id}")
        channel_id = result["channel"]["id"]
        col = _get_col(team_id)
        col.update_one({"user_id": mentor_id}, {"$set": {"group_dm_channel": channel_id}})
        col.update_one({"user_id": mentee_id}, {"$set": {"group_dm_channel": channel_id}})
        client.chat_postMessage(
            channel=channel_id,
            text=(
                f":wave: Hey <@{mentor_id}> and <@{mentee_id}>! "
                f"This is your shared space — use it to connect, ask questions, and share advice."
                f"{tags_line}"
            )
        )
        logger.info("[MENTOR] Group DM created: %s", channel_id)
    except Exception as e:
        logger.warning("[MENTOR] Could not create group DM (this is OK — individual DMs were sent): %s", e)


# ------------------------------------------------------------------ #
#  Weekly check-in (called by scheduler)                               #
# ------------------------------------------------------------------ #
def send_weekly_checkin(client, team_id: str) -> None:
    """Send a weekly check-in prompt to each active mentor-mentee pair's group chat."""
    from services.mentor_service import get_all_pairs
    from services.prompt_service import get_random_prompt_text

    pairs = get_all_pairs(team_id)
    if not pairs:
        return

    for mentor_id, mentee_id, group_dm_channel in pairs:
        _, prompt_text, _ = get_random_prompt_text()
        msg = (
            f":wave: *Weekly Mentor-Mentee Check-in!*\n\n"
            f"<@{mentor_id}> and <@{mentee_id}> — here's a conversation starter for this week:\n\n"
            f"_{prompt_text}_"
        )
        target = group_dm_channel or mentor_id
        try:
            client.chat_postMessage(channel=target, text=msg)
            if not group_dm_channel:
                client.chat_postMessage(channel=mentee_id, text=msg)
        except Exception as e:
            logger.error("[MENTOR] Failed to send weekly check-in for pair %s+%s: %s", mentor_id, mentee_id, e)

    logger.info("[MENTOR] Sent weekly check-ins for %d pair(s) in team %s", len(pairs), team_id)
