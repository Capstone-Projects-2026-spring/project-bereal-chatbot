# src/bot/paths.py
from pathlib import Path

# repo root: .../project-bereal-chatbot/
# This file is at: repo/src/bot/paths.py
# parents[0] = bot, parents[1] = src, parents[2] = repo root
REPO_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = REPO_ROOT / "data"
PROMPTS_DIR = DATA_DIR / "prompts"
LOGS_DIR = DATA_DIR / "logs"

PROMPTS_CSV = PROMPTS_DIR / "vibecheck_prompts.csv"
STRUCTURED_JSONL = LOGS_DIR / "slack_messages.jsonl"

# Ensure folders exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)