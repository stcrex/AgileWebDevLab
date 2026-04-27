from flask import Flask

from app.config import Config
from app.extensions import csrf, db, login_manager
from app.routes.auth import auth_bp
from app.routes.main import main_bp


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    # Stage 3 simple auth pages are exempted from CSRF so login/register work reliably.
    csrf.exempt(auth_bp)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    @app.cli.command("init-db")
    def init_db_command():
        from app.seed import seed_demo_data

        db.drop_all()
        db.create_all()
        seed_demo_data()

        print("Database initialised successfully.")

    return app
