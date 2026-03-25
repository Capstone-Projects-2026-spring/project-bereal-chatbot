# src/commands/status_command.py
from bot.state import get_team_id


def register_status_command(bolt_app, state_manager):
    @bolt_app.command("/vibestatus")
    def handle_status(ack, respond, body):
        ack()

        team_id = get_team_id(body)
        state = state_manager.get_state(team_id)

        mode = state.get_selected_mode() or "not set"
        channel = state.get_active_channel() or "not set"
        active_days = state.get_active_days()
        days_str = ", ".join(sorted(active_days)) if active_days else "none"

        if mode == "mode_static":
            scheduled = state.get_static_time() or "not set"
            mode_label = "Static"
        elif mode == "mode_preset":
            scheduled = state.get_daily_target_time() or "not set"
            mode_label = "Preset"
        elif mode == "mode_random":
            scheduled = state.get_daily_target_time() or "not set"
            start = state.get_random_start_time() or "?"
            end = state.get_random_end_time() or "?"
            mode_label = f"Random ({start} – {end})"
        else:
            scheduled = state.get_daily_target_time() or "not set"
            mode_label = mode

        today_active = state.is_today_active()

        respond(
            f"*Vibe Check Bot Status*\n"
            f"• *Mode:* {mode_label}\n"
            f"• *Channel:* {channel}\n"
            f"• *Today's prompt time:* {scheduled}\n"
            f"• *Active days:* {days_str}\n"
            f"• *Posting today:* {'yes' if today_active else 'no'}"
        )
