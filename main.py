"""Start the Recruitment Assistant API for local use."""

from pathlib import Path
import sys

import uvicorn

SOURCE_DIR = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(SOURCE_DIR))

from recruitment_assistant.api import app


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, workers=1)