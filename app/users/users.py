from typing import List, Optional

from flask import session
from sqlalchemy import or_

from ..models import Session, User

# Create a session
db_session = Session()


def get_user_by_email_or_phone(
    email: Optional[str], phone: Optional[int]
) -> Optional[User]:
    if not email and not phone:
        raise ValueError("Either email or phone must be provided")
    return User.query.filter(or_(User.email == email, User.phone == phone)).first()


def get_all_users() -> List[User]:
    users = User.query.all()
    return users


# Based on the current session, return the user that matches the email in the session
def get_current_user() -> Optional[User]:
    if not session.get("user"):
        return None
    user = session.get("user")
    return db_session.query(User).filter_by(email=user.get("email")).first()
