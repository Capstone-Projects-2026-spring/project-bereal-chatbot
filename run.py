# run.py (repo root)
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent
SRC_DIR = REPO_ROOT / "src"

# Put src/ on the import path so "bot", "services", "commands", etc. work.
sys.path.insert(0, str(SRC_DIR))

from bot.main import main  # now this works because src/ is on sys.path

if __name__ == "__main__":
    main()