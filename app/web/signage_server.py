# signage_server.py
from flask import Blueprint, render_template, jsonify, send_from_directory
import json
from pathlib import Path
from ..config import PLAYLIST_PATH, BASE_DIR

# Use the player templates directory (app/player/templates)
TEMPLATES_DIR = Path(__file__).parent / 'templates'


BP = Blueprint('main', __name__, template_folder=str(TEMPLATES_DIR))


@BP.route("/")
def index():
    return render_template("index.html")


@BP.route("/playlist.json")
def playlist():
    with open(PLAYLIST_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Optional: nur enabled Items schicken
    data = [item for item in data if item.get("enabled", True)]
    return jsonify(data)


@BP.route('/media/<path:filename>')
def media(filename):
    """Serve media files from the repository 'media' folder to match the main app.

    Example: /media/images/abc.jpg
    """
    media_root = BASE_DIR / 'media'
    return send_from_directory(str(media_root), filename)
