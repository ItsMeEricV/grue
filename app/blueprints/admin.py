import os
import time
from uuid import UUID

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import delete
from werkzeug.utils import secure_filename

from ..models import Season
from ..navigation.import_twine import ImportTwine
from ..seasons.seasons import SeasonStore
from ..users.users import UserStore

admin_bp = Blueprint("admin", __name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"twee"}


# Only .twee files supported
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@admin_bp.context_processor
def inject_user():
    user = UserStore.get_current_user()
    return dict(user=user, current_user_is_admin=UserStore.current_user_is_admin)


@admin_bp.route("/admin/users")
def users():
    users = UserStore.get_all_users()
    return render_template(
        "admin/admin_users.html", endpoint="admin.users", users=users
    )


@admin_bp.route("/admin/seasons")
def seasons():
    seasons = SeasonStore.fetch_seasons_with_counts()
    return render_template(
        "admin/admin_seasons.html", endpoint="admin.seasons", seasons=seasons
    )


@admin_bp.route("/admin/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        print("No file part")
        return redirect(request.url)

    file = request.files["file"]
    if file.filename == "":
        print("No selected file")
        return redirect(request.url)
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filename_with_ts = f"{int(time.time())}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename_with_ts)
        file.save(filepath)
        twine = ImportTwine(filepath, file.filename)
        twine.parse_twee_file()
        twine.insert_story()

        print("File successfully uploaded")
        return redirect(url_for("admin.seasons"))
    else:
        print("Allowed file types are .twee (Twine story files)")
        return redirect(request.url)


@admin_bp.route("/admin/delete_season/<uuid:season_id>", methods=["POST"])
def delete_season(season_id: UUID):
    Session = current_app.extensions["Session"]
    with Session.begin() as db_session:
        stmt = delete(Season).where(Season.id == season_id)
        result = db_session.execute(stmt)
        if result.rowcount > 0:
            flash("Season successfully deleted")
        else:
            flash("Season not found")
    return redirect(url_for("admin.seasons"))


@admin_bp.route("/admin/make_default/<uuid:season_id>", methods=["POST"])
def make_default(season_id: UUID):
    Session = current_app.extensions["Session"]
    with Session.begin() as db_session:
        # First need to mark the current default season as not default
        current_default_season = (
            db_session.query(Season).filter(Season.default).one_or_none()
        )
        if current_default_season:
            current_default_season.default = False
            db_session.query(Season).update({Season.default: False})
        season = db_session.query(Season).filter(Season.id == season_id).one_or_none()
        if season:
            # Reset the default flag for all seasons
            db_session.query(Season).update({Season.default: False})
            # Set the selected season as default
            season.default = True
            flash("Season successfully set as default")
        else:
            flash("Season not found")
        return redirect(url_for("admin.seasons"))
