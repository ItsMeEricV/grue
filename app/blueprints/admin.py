import os
import time

from flask import Blueprint, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

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
    season_name: str = request.form["season_name"]
    if file.filename == "":
        print("No selected file")
        return redirect(request.url)
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filename = f"{int(time.time())}_{filename}"
        filename = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filename)
        id = SeasonStore.create_season(season_name, file.filename)
        twine_data = ImportTwine(filename).parse_twee_file()
        print(twine_data)
        # print(f"Metadata: {twine_data[1]}")
        # print(f"Start Passage: {twine_data[1].get('start')}")
        # print("Passages:")
        # for passage in twine_data[0]:
        #     print(f"Title: {passage['title']}")
        #     print(f"Metadata: {passage['metadata']}")
        #     print(f"Content: {passage['content']}")
        #     print("-----")

        print("File successfully uploaded")
        return redirect(url_for("admin.seasons"))
    else:
        print("Allowed file types are .twee (Twine story files)")
        return redirect(request.url)
