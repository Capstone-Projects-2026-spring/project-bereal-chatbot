# src/commands/prompt_stats_command.py
from services.mongo_service import get_tracker


def register_prompt_stats_command(bolt_app):
    @bolt_app.command("/promptstats")
    def handle_prompt_stats(ack, respond, body):
        ack()

        tracker = get_tracker()
        if not tracker:
            respond("Prompt tracker is not initialized.")
            return

        team_id = body.get("team_id") or (body.get("authorizations") or [{}])[0].get("team_id") or ""
        stats = tracker.get_all_stats(team_id)
        if not stats:
            respond("No prompt stats recorded yet.")
            return

        lines = ["*Prompt Stats (most asked first)*"]
        for doc in stats[:20]:
            tags = ", ".join(doc.get("tags", [])) or "—"
            asked = doc.get("times_asked", 0)
            responded = doc.get("times_responded", 0)
            prompt = doc.get("prompt", "")[:60]
            lines.append(f"• [asked {asked}x | responses {responded}] _{tags}_ — {prompt}…")

        respond("\n".join(lines))
