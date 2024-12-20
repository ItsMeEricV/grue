import secrets

from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from ..users.users import UserStore

auth_bp = Blueprint("auth", __name__)


# TODO: Refactor so we don't have to copy pasta this inject_user across all blueprints
@auth_bp.context_processor
def inject_user():
    user = UserStore.get_current_user()
    return dict(user=user, current_user_is_admin=UserStore.current_user_is_admin)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # Add your authentication logic here
        if username == "admin" and password == "password":  # Example check
            return redirect(url_for("main.index"))
        else:
            return "Invalid credentials", 401
    google_client_id = current_app.config["GOOGLE_CLIENT_ID"]  # type: ignore
    return render_template("login.html", google_client_id=google_client_id)


@auth_bp.route("/login/google")
def login_google():
    nonce: str = secrets.token_urlsafe(32)  # Generate a nonce
    session["nonce"] = nonce  # Store it in the session
    redirect_uri = url_for("auth.callback", _external=True)
    oauth = current_app.extensions["oauth"]
    return oauth.google.authorize_redirect(redirect_uri, nonce=nonce)


@auth_bp.route("/callback")
def callback():
    oauth = current_app.extensions["oauth"]
    token = oauth.google.authorize_access_token()
    nonce: str | None = session.pop("nonce", None)  # type: ignore
    if nonce is not None:
        nonce = str(nonce)  # type: ignore
    user_info = oauth.google.parse_id_token(token, nonce=nonce)
    session["user"] = user_info
    return redirect(url_for("main.index"))


@auth_bp.route("/logout")
def logout():
    session.pop("user", None)  # type: ignore
    return "You have been logged out"
