import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import mapped_column, scoped_session, sessionmaker

from app import create_app
from app.models import Base

# Session = sessionmaker(bind=engine)


@pytest.fixture()
def app():
    app = create_app("config.TestConfig")
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # Override the database URI
        }
    )
    engine: Engine = app.extensions["engine"]

    # other setup can go here
    Base.metadata.create_all(engine)

    yield app

    # clean up / reset resources here
    Base.metadata.drop_all(engine)


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture()
def runner(app: Flask) -> FlaskClient:
    return app.test_cli_runner()
