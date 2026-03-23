# src/bot/main.py
import threading

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
    register_force_prompt_command(bolt_app, client)
    register_time_commands(bolt_app, state)
    register_set_channel_command(bolt_app, client, state)
    register_control_panel(bolt_app, state)

    # Start background scheduler
    threading.Thread(
        target=run_time_checker,
        args=(client, cfg.default_channel, state),
        daemon=True
    ).start()

    print("[BOOT] Bot ready.")
    return bolt_app
