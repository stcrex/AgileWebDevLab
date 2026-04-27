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
        from app.models import User
        return User.query.get(int(user_id))

    app.register_blueprint(main_bp)

    @app.cli.command("init-db")
    def init_db_command():
        from app.seed import seed_demo_data

        db.drop_all()
        db.create_all()
        seed_demo_data()

        print("Database initialised successfully.")

    return app
