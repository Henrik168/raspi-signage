from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from functools import wraps
from werkzeug.security import check_password_hash
from typing import Any
from pathlib import Path
import json
from ..config import USERS_FILE

# Use the player templates directory (app/player/templates)
TEMPLATES_DIR = Path(__file__).parent / 'templates'


BP = Blueprint('auth', __name__, template_folder=str(TEMPLATES_DIR))


def load_users() -> list[dict[str, Any]]:
    if not USERS_FILE.exists():
        return []
    try:
        return json.loads(USERS_FILE.read_text(encoding='utf-8'))
    except Exception:
        return []


def get_user(username: str) -> dict[str, Any] | None:
    for u in load_users():
        if u.get('username') == username:
            return u
    return None


def login_user(username: str):
    session['user'] = username


def logout_user():
    session.pop('user', None)


def current_user():
    username = session.get('user')
    if not username:
        return None
    return get_user(username)


def login_required(role: str | None = None):
    def deco(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # If no users are configured at all, allow access (convenience for initial setup)
            if len(load_users()) == 0:
                return f(*args, **kwargs)

            u = current_user()
            if not u:
                return redirect(url_for('auth.login', next=request.path))
            if role and u.get('role') != role:
                return ('Forbidden', 403)
            return f(*args, **kwargs)
        return wrapped
    return deco


@BP.route('/login', methods=['GET', 'POST'])
def login():
    # default redirect after login: main.index (admin endpoint may not exist in this app)
    next_url = request.args.get('next') or url_for('main.index')
    if request.method != 'POST':
        return render_template('login.html', next=next_url)

    username = (request.form.get('username') or '').strip()
    password = request.form.get('password') or ''

    user = get_user(username)
    if not user:
        flash('Ungültiger Benutzername oder Passwort', 'error')
        return redirect(url_for('auth.login', next=next_url))

    stored_hash = user.get('password_hash')
    if not stored_hash or not check_password_hash(stored_hash, password):
        # failed authentication: flash and redirect to GET login to show message
        flash('Ungültiger Benutzername oder Passwort', 'error')
        return redirect(url_for('auth.login', next=next_url))

    login_user(username)
    return redirect(request.form.get('next') or next_url)


@BP.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
