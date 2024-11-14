import uuid

from flask import Blueprint, render_template

from ..navigation.nav import Nav
from ..users.users import UserStore

main_bp = Blueprint("main", __name__)


# TODO: Refactor so we don't have to copy pasta this inject_user across all blueprints
@main_bp.context_processor
def inject_user():
    user = UserStore.get_current_user()
    return dict(user=user, current_user_is_admin=UserStore.current_user_is_admin)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/play")
def play():
    # TODO: remove debug
    location_id = uuid.UUID("3d6d5051-0f49-47de-a2e2-d87a186c403e")
    Nav.get_decisions_for_location(location_id)
    return render_template("game.html")


@main_bp.route("/design")
def design():
    # TODO: remove debug
    location_id = uuid.UUID("3d6d5051-0f49-47de-a2e2-d87a186c403e")
    # These are hardcoded for now, but would be passed in from the client in a real game
    id1 = uuid.UUID("6571f563-7438-47d7-804c-d0d57f4a6f2e")
    id2 = uuid.UUID("c6ddfc25-bf8e-4978-88e6-c01aee1e7aac")
    decision_destination1: Nav.Destination = {
        "destination_location_id": id1,
        "description": "Go north",
        "position": 0,
    }
    decision_destination2: Nav.Destination = {
        "destination_location_id": id2,
        "description": "Go south",
        "position": 1,
    }
    Nav.creation_decisions(location_id, [decision_destination1, decision_destination2])
    return render_template("game.html")
