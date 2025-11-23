from pathlib import Path
import json
from logging import getLogger
log = getLogger()

# Explizites Template-Verzeichnis setzen, da die Templates unter app/web/templates liegen
BASE_DIR = Path(__file__).parent.parent

MEDIA_IMAGES = BASE_DIR / "media" / "images"

MEDIA_VIDEOS = BASE_DIR / "media" / "videos"

PLAYLIST_PATH = BASE_DIR / "data" / "playlist.json"

USERS_FILE = BASE_DIR / "data" / "users.json"

TEMPLATES_DIR = BASE_DIR / "app" / "web" / "templates"


def log_config():
    """Loggt die aktuelle Konfiguration."""
    log.info(f"BASE_DIR: {BASE_DIR}")
    log.info(f"MEDIA_IMAGES: {MEDIA_IMAGES}")
    log.info(f"MEDIA_VIDEOS: {MEDIA_VIDEOS}")
    log.info(f"PLAYLIST_PATH: {PLAYLIST_PATH}")
    log.info(f"USERS_FILE: {USERS_FILE}")
    log.info(f"TEMPLATES_DIR: {TEMPLATES_DIR}")


def check_directories():
    """Stellt sicher, dass die benötigten Verzeichnisse existieren."""
    MEDIA_IMAGES.mkdir(parents=True, exist_ok=True)
    MEDIA_VIDEOS.mkdir(parents=True, exist_ok=True)
    PLAYLIST_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not PLAYLIST_PATH.exists():
        json.dump([], PLAYLIST_PATH.open("w", encoding="utf-8"), indent=2)
    log_config()
