from flask import Flask
import sys
from .blueprints.main import main_bp
from .blueprints.auth import auth_bp

# App initialization
def create_app():
    app = Flask(__name__)

    # Import and register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    # Debug route to print all routes
    @app.route('/debug')
    def debug_routes():
        print(app.url_map, file=sys.stderr)
        return 'hi121212'

    return app