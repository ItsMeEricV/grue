from flask import Blueprint


# Initialize blueprints
auth_bp = Blueprint('auth', __name__)
main_bp = Blueprint('main', __name__)

# print(app.url_map, file=sys.stderr)
# print(app.url_map, file=sys.stderr)

# Import routes to register them with the blueprints
#from . import auth, main_bp