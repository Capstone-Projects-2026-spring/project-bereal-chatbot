# run.py (repo root)
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent
SRC_DIR = REPO_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))

# Entry point is oauth_app.py via gunicorn — this file is no longer the main entry point.
# Kept for local development only.
from oauth_app import app

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
