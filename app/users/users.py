from typing import Sequence

from flask import session
from sqlalchemy import or_, select

from ..db import get_db_session
from ..models import User

"""
Basic user getter functions until we have more need for user CRUD
"""


class UserStore:
    @staticmethod
    def get_user_by_email_or_phone(email: str | None, phone: int | None) -> User | None:
        """
        Get a user by email or phone

        Returns:
            User | None: The user, or None if no user was found
        """
        db_session = get_db_session()
        if not email and not phone:
            raise ValueError("Either email or phone must be provided")
        return (
            db_session.execute(
                select(User).filter(or_(User.email == email, User.phone == phone))
            )
            .scalars()
            .one_or_none()
        )

    @staticmethod
    def get_all_users() -> list[User]:
        """
        Get all users

        Returns:
            list[User]: A list of all users
        """
        db_session = get_db_session()
        users: Sequence[User] = (
            db_session.execute(select(User).order_by(User.username)).scalars().all()
        )
        return list(users)

    @staticmethod
    def get_current_user() -> User | None:
        """
        Get the current user from the session

        Returns:
            User | None: The current user, or None if there is no user in the session
        """
        db_session = get_db_session()
        if not session.get("user"):
            return None
        email: str = str(session.get("user").get("email"))
        return (
            db_session.execute(select(User).filter(User.email == email))
            .scalars()
            .one_or_none()
        )

    @staticmethod
    def current_user_is_admin() -> bool:
        """
        Is the current user an admin?

        Returns:
            bool: True if the current user is an admin, False otherwise
        """
        user: User | None = UserStore.get_current_user()
        if not user:
            return False
        return user.is_admin
