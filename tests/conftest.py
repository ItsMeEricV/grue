import pytest
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner
from sqlalchemy.engine.base import Engine

from app import create_app
from app.models import Base


@pytest.fixture()
def app():
    app = create_app("config.TestConfig")
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
def runner(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()
