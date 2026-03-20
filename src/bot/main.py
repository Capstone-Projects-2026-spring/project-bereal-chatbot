# src/bot/main.py
import threading

from slack_sdk import WebClient
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from bot.config import load_config
from bot.paths import STRUCTURED_JSONL
from bot.state import create_state
from bot.scheduler import run_time_checker

from commands.force_prompt_command import register_force_prompt_command
from commands.time_commands import register_time_commands
from commands.control_panel_commands import register_control_panel
from app_logging.structured_logger import install_structured_message_logging


def main():
    print("\n[BOOT] Starting bot...")

    cfg = load_config()
    state = create_state()

    client = WebClient(token=cfg.token)
    bolt_app = App(token=cfg.token, ignoring_self_events_enabled=False)

    # Logging + commands
    install_structured_message_logging(bolt_app, client, log_file=str(STRUCTURED_JSONL))
    register_force_prompt_command(bolt_app, client)
    register_time_commands(bolt_app, state)
    register_control_panel(bolt_app, state)

    # Online message
    try:
        client.chat_postMessage(channel=cfg.default_channel, text="bot online")
    except Exception as e:
        print(f"Error posting 'bot online' message: {e}")

    # Background time checker
    print("[BOOT] Starting background time checker...")
    time_thread = threading.Thread(
        target=run_time_checker,
        args=(client, cfg.default_channel, state),
        daemon=True
    )
    time_thread.start()

    # Socket Mode
    print("[BOOT] Starting Socket Mode handler...")
    handler = SocketModeHandler(bolt_app, cfg.app_token)
    handler.start()


if __name__ == "__main__":
    main()