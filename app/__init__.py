from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from .blueprints.main import main_bp
from .blueprints.auth import auth_bp

# TEMP
#import sys

db = SQLAlchemy()
migrate = Migrate()

# App initialization
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Register DB models
    register_models()

    # Import and register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    # TEMP
    # Debug route to print all routes
    # @app.route('/debug')
    # def debug_routes():
    #     print(app.url_map, file=sys.stderr)
    #     return 'hi121212'

    return app

# Import models to register them with SQLAlchemy
def register_models() -> None:
    from .models import User
    _ = User