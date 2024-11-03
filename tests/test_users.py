import pytest
from flask import Flask, session

from app.models import User
from app.users.users import UserStore


class TestAppContext:
    def test_app_context(self, app: Flask):
        with app.app_context():
            assert app.config["TESTING"] is True


class TestUserStore:
    @pytest.fixture(autouse=True)
    def setup(self, app: Flask):
        self.app = app
        self.Session = app.extensions["Session"]

    def test_get_all_users(self):
        with self.app.app_context():
            # Add test users
            user1 = User(username="user1", email="user1@example.com", phone=1111111111)
            user2 = User(username="user2", email="user2@example.com", phone=2222222222)

            with self.Session.begin() as db_session:
                db_session.add(user1)
                db_session.add(user2)

            users: list[User] = UserStore.get_all_users()
            assert len(users) == 2
            assert users[0].username == "user1"
            assert users[1].username == "user2"

    def test_get_current_user(self):
        with self.app.app_context():
            # Add test user
            user = User(username="user1", email="user1@example.com", phone=1111111111)
            with self.Session.begin() as db_session:
                db_session.add(user)

            # Set the user in the session
            with self.app.test_request_context():
                session["user"] = {"email": "user1@example.com"}

                # Call get_current_user
                current_user = UserStore.get_current_user()
                assert current_user is not None
                assert current_user.username == "user1"
                assert current_user.email == "user1@example.com"
                assert current_user.phone == 1111111111

    def test_get_current_user_no_user(self):
        with self.app.app_context():
            # Set the session to be empty
            with self.app.test_request_context():
                session.pop("user", None)

                # Call get_current_user
                current_user = UserStore.get_current_user()
                assert current_user is None
