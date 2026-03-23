# src/bot/config.py
import os
from dataclasses import dataclass
from dotenv import load_dotenv

from bot.paths import REPO_ROOT


@dataclass(frozen=True)
class BotConfig:
    token: str
    default_channel: str
    client_id: str
    client_secret: str
    signing_secret: str


def load_config() -> BotConfig:
    env_path = REPO_ROOT / ".env"
    load_dotenv(dotenv_path=env_path)
    print("Loaded .env from:", env_path)

    token = os.getenv("SLACK_BOT_TOKEN")
    default_channel = os.getenv("DEFAULT_CHANNEL", "")
    client_id = os.getenv("SLACK_CLIENT_ID")
    client_secret = os.getenv("SLACK_CLIENT_SECRET")
    signing_secret = os.getenv("SLACK_SIGNING_SECRET")

    if not token:
        raise RuntimeError("Missing SLACK_BOT_TOKEN in .env")
    if not client_id:
        raise RuntimeError("Missing SLACK_CLIENT_ID in .env")
    if not client_secret:
        raise RuntimeError("Missing SLACK_CLIENT_SECRET in .env")
    if not signing_secret:
        raise RuntimeError("Missing SLACK_SIGNING_SECRET in .env")

    return BotConfig(
        token=token,
        default_channel=default_channel,
        client_id=client_id,
        client_secret=client_secret,
        signing_secret=signing_secret,
    )