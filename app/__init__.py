# app/__init__.py
from flask import Flask
import os
import secrets
from .config import TEMPLATES_DIR
from .web.signage_server import BP as main_bp
from .web.routes import admin_bp
from .web.auth import BP as auth_bp


# from .extensions import db, login_manager, ...  # falls du sowas nutzt


def create_app() -> Flask:

    app = Flask(__name__, template_folder=str(TEMPLATES_DIR))

    # Secret key for session signing. Prefer an environment variable in production.
    app.secret_key = os.environ.get('SIGNAGE_SECRET') or secrets.token_hex(32)
    if not os.environ.get('SIGNAGE_SECRET'):
        app.logger.warning(
            'SIGNAGE_SECRET not set; using generated secret (not for production)')

    # Config laden
    app.config.from_mapping(
        MAX_CONTENT_LENGTH=1024 * 1024 * 1024,  # z.B. 1 GB
        # weitere Config …
    )

    # Extensions initialisieren
    # db.init_app(app)
    # login_manager.init_app(app)
    # etc.

    # Blueprints registrieren
    app.register_blueprint(main_bp)
    # register admin routes (they declare their own '/admin' path)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app
