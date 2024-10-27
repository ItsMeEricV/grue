from flask import Blueprint, render_template

from ..users.users import get_current_user

main_bp = Blueprint("main", __name__)


@main_bp.context_processor
def inject_user():
    user = get_current_user()
    return dict(user=user)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/play")
def play():
    return render_template("game.html")
