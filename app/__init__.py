from flask import Flask

from app.config import Config
from app.extensions import db, login_manager, csrf
from app.routes.main import main_bp


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "main.index"

    @login_manager.user_loader
    def load_user(user_id):
        # Temporary loader for Stage 1.
        # We do not have real users yet, so return None.
        return None

    app.register_blueprint(main_bp)

    return app
