from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .auth.oauth import register_oauth
from .blueprints.auth import auth_bp
from .blueprints.main import main_bp
from .models import Base


def create_app(config: str) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)

    db = SQLAlchemy(model_class=Base)
    migrate = Migrate(app, db)
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
