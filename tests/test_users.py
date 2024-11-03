import pytest
from flask import Flask
from sqlalchemy import create_engine, select
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, User
from app.users.users import get_all_users

# from .conftest import Session


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

        with Session.begin() as session:
            session.add(user1)
            session.add(user2)

        # DEBUG to fetch the users directly after insert
        # results = Session().execute(select(User).order_by(User.id)).scalars().all()
        # print(results)

        users: list[User] = get_all_users()
        assert len(users) == 2
        assert users[0].username == "user1"
