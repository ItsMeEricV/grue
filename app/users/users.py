from typing import List, Optional

from flask import session
from sqlalchemy import or_

from ..models import Session, User

"""
Basic user getter functions until we have more need for user CRUD
"""

# Create a session
db_session = Session()


def get_user_by_email_or_phone(
    email: Optional[str], phone: Optional[int]
) -> Optional[User]:
    """
    Get a user by email or phone

    Returns:
        Optional[User]: The user, or None if no user was found
    """
    if not email and not phone:
        raise ValueError("Either email or phone must be provided")
    return User.query.filter(or_(User.email == email, User.phone == phone)).first()


def get_all_users() -> List[User]:
    """
    Get all users

    Returns:
        List[User]: A list of all users
    """
    users = db_session.query(User).all()
    return users


def get_current_user() -> Optional[User]:
    """
    Get the current user from the session

    Returns:
        Optional[User]: The current user, or None if there is no user in the session
    """
    if not session.get("user"):
        return None
    user = session.get("user")
    return db_session.query(User).filter_by(email=user.get("email")).first()


def current_user_is_admin() -> bool:
    """
    Is the current user an admin?

    Returns:
        bool: True if the current user is an admin, False otherwise
    """
    user = get_current_user()
    return user and user.is_admin
