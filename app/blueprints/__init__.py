from flask import Blueprint

# Initialize blueprints
auth_bp = Blueprint('auth', __name__)
main_bp = Blueprint('main', __name__)

# Import routes to register them with the blueprints
from . import auth, main