# src/bot/main.py
import threading
import json
import os
from pathlib import Path

from slack_sdk import WebClient

from bot.config import load_config
from bot.paths import STRUCTURED_JSONL
from bot.state import create_state
from bot.scheduler import run_time_checker

from commands.force_prompt_command import register_force_prompt_command
from commands.time_commands import register_time_commands
from commands.set_channel_command import register_set_channel_command
from commands.control_panel_commands import register_control_panel
from app_logging.structured_logger import install_structured_message_logging


def _build_scheduler_client_provider(fallback_token: str):
    preferred_team_id = os.getenv("SLACK_SCHEDULER_TEAM_ID", "").strip()
    installations_dir = Path("data/installations")

    def _load_installation_token() -> str | None:
        if not installations_dir.exists():
            return None

        # Optional: pin scheduler posts to a single installed workspace.
        if preferred_team_id:
            preferred_file = installations_dir / f"{preferred_team_id}.json"
            if preferred_file.exists():
                try:
                    data = json.loads(preferred_file.read_text(encoding="utf-8"))
                    return data.get("access_token")
                except Exception:
                    return None

        # Otherwise use the most recently written installation.
        candidates = [p for p in installations_dir.glob("*.json") if p.is_file()]
        if not candidates:
            return None
        latest = max(candidates, key=lambda p: p.stat().st_mtime)
        try:
            data = json.loads(latest.read_text(encoding="utf-8"))
            return data.get("access_token")
        except Exception:
            return None

    def _provider() -> WebClient:
        token = _load_installation_token() or fallback_token
        return WebClient(token=token)

    return _provider


def create_bolt_app():
    """Create and return the configured Bolt app. Called by oauth_app.py."""
    from slack_bolt import App
    from slack_bolt.oauth.oauth_settings import OAuthSettings
    from slack_sdk.oauth.installation_store import FileInstallationStore
    from slack_sdk.oauth.state_store import FileOAuthStateStore
    from bot.paths import INSTALLATIONS_DIR, STATES_DIR

    cfg = load_config()
    state = create_state(default_channel=cfg.default_channel)

    oauth_settings = OAuthSettings(
        client_id=cfg.client_id,
        client_secret=cfg.client_secret,
        scopes=["chat:write", "channels:history", "channels:read", "commands"],
        installation_store=FileInstallationStore(base_dir=str(INSTALLATIONS_DIR)),
        state_store=FileOAuthStateStore(
            expiration_seconds=600,
            base_dir=str(STATES_DIR)
        ),
    )

    bolt_app = App(
        signing_secret=cfg.signing_secret,
        oauth_settings=oauth_settings,
    )

    client = WebClient(token=cfg.token)

    install_structured_message_logging(bolt_app, client, log_file=str(STRUCTURED_JSONL))
    register_force_prompt_command(bolt_app)
    register_time_commands(bolt_app, state)
    register_set_channel_command(bolt_app, state)
    register_control_panel(bolt_app, state)

    scheduler_client_provider = _build_scheduler_client_provider(cfg.token)

    # Start background scheduler
    threading.Thread(
        target=run_time_checker,
        args=(scheduler_client_provider, cfg.default_channel, state),
        daemon=True
    ).start()

    print("[BOOT] Bot ready.")
    return bolt_app
