from pathlib import Path
import json
from logging import getLogger
from .add_user import add_user

log = getLogger()

# Explizites Template-Verzeichnis setzen, da die Templates unter app/web/templates liegen
BASE_DIR = Path(__file__).parent.parent

MEDIA_IMAGES = BASE_DIR / "media" / "images"

MEDIA_VIDEOS = BASE_DIR / "media" / "videos"

PLAYLIST_PATH = BASE_DIR / "data" / "playlist.json"

USERS_FILE = BASE_DIR / "data" / "users.json"

TEMPLATES_DIR = BASE_DIR / "app" / "web" / "templates"


def get_users() -> list[dict]:
    try:
        return json.loads(USERS_FILE.read_text(encoding='utf-8'))
    except Exception as e:
        log.error("Error loading users: %s", e)
        return []


def init_signage() -> None:
    log.info("Initializing signage application...")
    # Weitere Initialisierungen können hier hinzugefügt werden
    MEDIA_IMAGES.mkdir(parents=True, exist_ok=True)
    MEDIA_VIDEOS.mkdir(parents=True, exist_ok=True)
    PLAYLIST_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not PLAYLIST_PATH.exists():
        PLAYLIST_PATH.write_text(json.dumps([], indent=2), encoding="utf-8")
    if not USERS_FILE.exists():
        USERS_FILE.write_text(json.dumps([], indent=2), encoding="utf-8")

    if get_users():
        log.info("Users already exist. Skipping admin user creation.")
        return

    if not add_user():
        log.error("Failed to add admin user. Exiting.")
        raise RuntimeError("Failed to add admin user.")


init_signage()
