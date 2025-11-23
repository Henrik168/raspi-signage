# app/routes.py

from ..config import MEDIA_IMAGES, MEDIA_VIDEOS, BASE_DIR
from ..playlist import playlist
from .poster import create_thumbnail_ffmpeg
from .auth import login_required
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, send_from_directory
from pathlib import Path
import uuid
import os
from logging import getLogger
log = getLogger(__name__)


# Use the player templates directory (app/player/templates)
TEMPLATES_DIR = Path(__file__).parent / 'templates'


admin_bp = Blueprint("admin", __name__, template_folder=str(TEMPLATES_DIR))


@admin_bp.route("/admin")
@login_required(role='admin')
def index():
    items = playlist.all()

    return render_template("admin.html", items=items)


# media files are served by the main signage server blueprint to avoid duplicate routes


@admin_bp.route("/upload", methods=["POST"])
@login_required(role='admin')
def upload():
    file = request.files["file"]
    if not file:
        log.warning("No file part in the request")
        return redirect(url_for("admin.index"))

    filename = file.filename
    if not filename:
        log.warning("No selected file")
        return redirect(url_for("admin.index"))

    ext = filename.lower().split(".")[-1]
    id_ = str(uuid.uuid4())

    if ext in ["jpg", "jpeg", "png", "gif"]:
        target = MEDIA_IMAGES / f"{id_}.{ext}"
        file_type = "image"
    elif ext in ["mp4", "mov", "mkv"]:
        target = MEDIA_VIDEOS / f"{id_}.{ext}"
        file_type = "video"
    else:
        # dateityp ignorieren oder Fehlermeldung
        log.warning("Unsupported file type: %s", ext)
        return redirect(url_for("admin.index"))
    file.save(str(target))

    # store path relative to media/ directory
    rel = target.relative_to(MEDIA_IMAGES.parent)

    poster_rel = None
    if file_type == "video":
        # create thumbnail
        thumb_path = MEDIA_IMAGES / f"{id_}_thumb.jpg"
        log.debug("Creating thumbnail for %s at %s", target, thumb_path)
        try:
            create_thumbnail_ffmpeg(
                video_path=target,
                output_path=thumb_path,
                t=1.0,
                width=320
            )
            poster_rel = thumb_path.relative_to(MEDIA_IMAGES.parent)
        except Exception as e:
            log.error("Error creating thumbnail for %s: %s", target, e)

    playlist.add(
        uuid=id_,
        media_type=file_type,
        file_name=str(rel),
        enabled=True,
        duration=8 if file_type == "image" else None,
        poster=str(poster_rel)
    )

    return redirect(url_for("admin.index"))


@admin_bp.route("/toggle/<item_id>", methods=["POST"])
@login_required(role='admin')
def toggle(item_id):
    playlist.toggle(item_id)
    return redirect(url_for("admin.index"))


@admin_bp.route("/reorder", methods=["POST"])
@login_required(role='admin')
def reorder():
    """Reorder playlist. Expects JSON: {"order": [id1, id2, ...]}"""
    data = request.get_json(silent=True)
    if not data or "order" not in data:
        return jsonify({"ok": False, "error": "missing order"}), 400

    order = data["order"]
    playlist.order(order)

    return jsonify({"ok": True})


@admin_bp.route("/move/<item_id>/<direction>", methods=["POST"])
@login_required(role='admin')
def move(item_id, direction):

    idx = playlist.get_position(item_id)
    if idx is None:
        return jsonify({"ok": False, "error": "not found"}), 404

    if direction == "up":
        playlist.move_by_idx(idx, -1)
    elif direction == "down":
        playlist.move_by_idx(idx, 1)
    else:
        return jsonify({"ok": False, "error": "invalid direction"}), 400

    return redirect(url_for("admin.index"))


@admin_bp.route("/set_duration/<item_id>", methods=["POST"])
@login_required(role='admin')
def set_duration(item_id):
    val = request.form.get("duration") or (
        request.get_json(silent=True) or {}).get("duration")
    try:
        duration = int(val) if val not in (None, "", "null") else None
    except Exception:
        return jsonify({"ok": False, "error": "invalid duration"}), 400

    item = playlist.update_by_uuid(item_id, duration=duration)

    if not item:
        return jsonify({"ok": False, "error": "not found"}), 404

    return jsonify({"ok": True, "redirect": url_for("admin.index")})


@admin_bp.route("/delete/<item_id>", methods=["POST"])
@login_required(role='admin')
def delete(item_id):
    item = playlist.get(item_id)

    if not item:
        return jsonify({"ok": False, "error": "not found"}), 404

    # delete file on disk if exists and inside media/ directory
    targets: list[Path] = []
    targets.append(BASE_DIR / 'media' / Path(item.file_name))
    if item.poster:
        targets.append(BASE_DIR / 'media' / Path(item.poster))

    for target in targets:
        try:
            os.remove(str(target))
        except Exception as e:
            log.error("Error deleting file %s: %s", target, e)

    removed = playlist.remove(item_id)

    if not removed:
        return jsonify({"ok": False, "error": "not found"}), 404

    return jsonify({"ok": True, "redirect": url_for("admin.index")})
