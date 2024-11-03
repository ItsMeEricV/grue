import os
import sys

# Add the parent directory to the sys.path to allow absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.models import User
from config import MainConfig

engine = create_engine(MainConfig.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)

admin_users = os.getenv("ADMIN_USERS", "").split(",")
with Session.begin() as session:
    for user in admin_users:
        username, email, phone = user.split(":")
        user = User(username=username, phone=phone, email=email, is_admin=True)
        session.add(user)

result = session.execute(select(User).order_by(User.id))
print(result.all())
