#!/usr/bin/env python3
"""Simple script to run the FastAPI server locally or on Render.

This script adjusts sys.path so the `app` package inside the agent-service
folder is importable even when starting from the repository root.
It also binds to 0.0.0.0 and reads the PORT from the environment, which
is required by Render and many PaaS platforms.
"""

import os
import sys

# Ensure this directory (agent-service) is on the Python path so `app` resolves
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if THIS_DIR not in sys.path:
    sys.path.insert(0, THIS_DIR)

import uvicorn  # type: ignore
from app.main import app  # noqa: E402


def main() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "false").lower() in {"1", "true", "yes"}
    log_level = os.getenv("LOG_LEVEL", "info")
    uvicorn.run(app, host=host, port=port, reload=reload, log_level=log_level)


if __name__ == "__main__":
    main()