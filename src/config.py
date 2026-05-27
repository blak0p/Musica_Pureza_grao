"""Centralized path configuration for school bell system.

All hardcoded paths in the project are consolidated here.
Paths are resolved once at import time via environment variables
with computed defaults relative to PROJECT_DIR.
"""

import os
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    """Load .env file into os.environ (setdefault semantics).

    Reads key=value pairs from the given path and calls
    os.environ.setdefault for each — existing env vars take precedence.

    Silently returns if the file doesn't exist.
    """
    if not path.exists():
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())


# ── Project root (autodetected from file location) ──
# src/config.py -> PROJECT_DIR is the parent of src/
PROJECT_DIR: Path = Path(__file__).resolve().parent.parent

# ── Auto-load .env from project root ──
_load_dotenv(PROJECT_DIR / ".env")

# ── Configurable paths (env var override, fallback computed) ──
MUSIC_DIR: Path = Path(os.environ.get("MUSIC_DIR", str(Path.home() / "musica")))
STATIC_DIR: Path = Path(os.environ.get("STATIC_DIR", str(PROJECT_DIR / "static")))

# ── Derived paths (always relative to PROJECT_DIR) ──
STATE_DIR: Path = PROJECT_DIR / "state"
STATE_FILE: Path = STATE_DIR / "carousel.json"
LOG_FILE_SERVER: Path = STATE_DIR / "server.log"
LOG_FILE_BELL: Path = STATE_DIR / "colegio-bell.log"

# ── System paths ──
PYTHON_PATH: str = "/usr/bin/python3"
MPV_PATH: str = "/usr/bin/mpv"

# ── Authentication (from .env with fallback) ──
WEB_USER: str = os.environ.get("WEB_USER", "admin")
WEB_PASSWORD: str = os.environ.get("WEB_PASSWORD", "admin123")
