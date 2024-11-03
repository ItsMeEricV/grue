# utils.py or db.py
from flask import current_app
from sqlalchemy.orm import Session

"""
Utility functions for the database
"""


def get_db_session() -> Session:
    return current_app.extensions["Session"]()
