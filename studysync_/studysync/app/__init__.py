from __future__ import annotations

from flask import Flask, redirect, url_for

from .config import Config
from .extensions import csrf, db, login_manager, migrate


def create_app(config_object: type[Config] = Config) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)

    app.instance_path and __import__("os").makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    from .routes.auth import auth_bp
    from .routes.main import main_bp
    from .routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.route("/")
    def index():
        return redirect(url_for("main.timetable"))

    @app.context_processor
    def inject_now():
        from datetime import datetime

        return {"now": datetime.utcnow}

    return app
