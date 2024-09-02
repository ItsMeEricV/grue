from flask import Flask

# App initialization

def create_app():
    app = Flask(__name__)

    # Import and register blueprints
    from .blueprints import auth_bp, main_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)

    return app