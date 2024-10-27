from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
migrate = Migrate()

from .auth.oauth import register_oauth
from .blueprints.auth import auth_bp
from .blueprints.main import main_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    register_oauth(app)
    # Register DB models
    register_models()

    # Import and register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    return app


def register_models() -> None:
    from .models import User

    _ = User
