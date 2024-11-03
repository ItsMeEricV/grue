from flask import Flask, session

from app.models import User
from app.users.users import UserStore


def test_app_context(app: Flask):
    with app.app_context():
        # Your test code here
        assert app.config["TESTING"] is True


# def test_client_request(client: FlaskClient):
#     response = client.get("/login")
#     assert response.status_code == 200
#     assert response.json == {"key": "value"}


def test_get_all_users(app: Flask):
    with app.app_context():
        Session = app.extensions["Session"]

        # Add test users
        user1 = User(username="user1", email="user1@example.com", phone=1111111111)
        user2 = User(username="user2", email="user2@example.com", phone=2222222222)

        with Session.begin() as db_session:
            db_session.add(user1)
            db_session.add(user2)

        # DEBUG to fetch the users directly after insert
        # results = Session().execute(select(User).order_by(User.id)).scalars().all()
        # print(results)

        users: list[User] = UserStore.get_all_users()
        assert len(users) == 2
        assert users[0].username == "user1"


def test_get_current_user(app: Flask):
    with app.app_context():
        Session = app.extensions["Session"]

        # Add test user
        user = User(username="user1", email="user1@example.com", phone=1111111111)
        with Session.begin() as db_session:
            db_session.add(user)

        # Set the user in the session
        with app.test_request_context():
            session["user"] = {"email": "user1@example.com"}

            # Call get_current_user
            current_user = UserStore.get_current_user()
            assert current_user is not None
            assert current_user.username == "user1"
            assert current_user.email == "user1@example.com"
            assert current_user.phone == 1111111111
