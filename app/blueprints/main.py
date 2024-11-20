import uuid

from flask import Blueprint, render_template, request

from ..navigation.nav import Nav
from ..seasons.seasons import SeasonStore
from ..users.users import UserStore
from ..util import uuid_validate

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


@main_bp.route("/play", defaults={"url_season_id": None})
@main_bp.route("/play/<path:url_season_id>")
def play(url_season_id: str | None):
    if url_season_id is not None:
        id = uuid_validate(url_season_id)
        if id is None:
            Season = SeasonStore.get_current_season()
            season_id = Season.id
        else:
            Season = SeasonStore.get_season_by_id(id)
            season_id = Season.id
    else:
        Season = SeasonStore.get_current_season()
        season_id = Season.id

    decisions = Nav.get_decisions_for_location(Season.genesis_location_id)
    location_description = decisions[0][1]
    descisions = [decision[0] for decision in decisions]
    return render_template(
        "game.html",
        location_description=location_description,
        decisions=descisions,
        season_id=season_id,
    )


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
