from typing import List, Optional, Sequence

from flask import session
from sqlalchemy import or_, select

from ..models import Session, User

"""
Basic user getter functions until we have more need for user CRUD
"""

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
    return (
        db_session.execute(
            select(User).filter(or_(User.email == email, User.phone == phone))
        )
        .scalars()
        .one_or_none()
    )


def get_all_users() -> List[User]:
    """
    Get all users

    Returns:
        List[User]: A list of all users
    """
    users: Sequence[User] = (
        db_session.execute(select(User).order_by(User.id)).scalars().all()
    )
    return list(users)


def get_current_user() -> Optional[User]:
    """
    Get the current user from the session

    Returns:
        Optional[User]: The current user, or None if there is no user in the session
    """
    if not session.get("user"):
        return None
    email: str = str(session.get("user").get("email"))
    return (
        db_session.execute(select(User).filter(User.email == email))
        .scalars()
        .one_or_none()
    )


def current_user_is_admin() -> bool:
    """
    Is the current user an admin?

    Returns:
        bool: True if the current user is an admin, False otherwise
    """
    user: Optional[User] = get_current_user()
    if not user:
        return False
    return user.is_admin
