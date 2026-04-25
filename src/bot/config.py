# src/bot/config.py
import os
from dataclasses import dataclass
from dotenv import load_dotenv

from bot.paths import REPO_ROOT


@dataclass(frozen=True)
class BotConfig:
    """Immutable configuration loaded from environment variables at startup."""

    token: str
    signing_secret: str
    default_channel: str
    mongo_uri: str
    llm_reactions_enabled: bool
    llm_reactions_probability: float
    llm_replies_enabled: bool
    llm_replies_probability: float


def load_config() -> BotConfig:
    """Load and validate bot configuration from the .env file at repo root."""
    env_path = REPO_ROOT / ".env"
    load_dotenv(dotenv_path=env_path)
    print("Loaded .env from:", env_path)

    token = os.getenv("SLACK_BOT_TOKEN")
    signing_secret = os.getenv("SLACK_SIGNING_SECRET")
    default_channel = os.getenv("DEFAULT_CHANNEL", "#bot-test")
    mongo_uri = os.getenv("MONGO_URI")
    llm_reactions_enabled = os.getenv("LLM_REACTIONS_ENABLED", "true").lower() == "true"
    llm_reactions_probability = float(os.getenv("LLM_REACTIONS_PROBABILITY", "0.5"))
    llm_replies_enabled = os.getenv("LLM_REPLIES_ENABLED", "true").lower() == "true"
    llm_replies_probability = float(os.getenv("LLM_REPLIES_PROBABILITY", "0.5"))

    if not token:
        raise RuntimeError("Missing SLACK_BOT_TOKEN in .env")
    if not signing_secret:
        raise RuntimeError("Missing SLACK_SIGNING_SECRET in .env")
    if not mongo_uri:
        raise RuntimeError("Missing MONGO_URI in .env")

    return BotConfig(
        token=token,
        signing_secret=signing_secret,
        default_channel=default_channel,
        mongo_uri=mongo_uri,
        llm_reactions_enabled=llm_reactions_enabled,
        llm_reactions_probability=llm_reactions_probability,
        llm_replies_enabled=llm_replies_enabled,
        llm_replies_probability=llm_replies_probability
    )
