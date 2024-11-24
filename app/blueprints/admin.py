from flask import Blueprint, render_template

from ..users.users import UserStore

admin_bp = Blueprint("admin", __name__)


@admin_bp.context_processor
def inject_user():
    user = UserStore.get_current_user()
    return dict(user=user, current_user_is_admin=UserStore.current_user_is_admin)


@admin_bp.route("/admin/users")
def users():
    return render_template("admin_users.html")


@admin_bp.route("/admin/seasons")
def seasons():
    return render_template("admin_seasons.html")
