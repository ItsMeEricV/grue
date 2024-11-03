from flask import Blueprint, render_template

from ..users.users import current_user_is_admin, get_all_users, get_current_user

main_bp = Blueprint("main", __name__)


# TODO: Refactor so we don't have to copy pasta this inject_user across all blueprints
@main_bp.context_processor
def inject_user():
    user = get_current_user()
    print(get_all_users())
    return dict(user=user, current_user_is_admin=current_user_is_admin)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/play")
def play():
    return render_template("game.html")
