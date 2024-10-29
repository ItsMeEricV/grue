import os
import sys

# Add the parent directory to the sys.path to allow absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import User
from config import MainConfig

engine = create_engine(MainConfig.SQLALCHEMY_DATABASE_URI)

Session = sessionmaker(bind=engine)
session = Session()

admin_users = os.getenv("ADMIN_USERS", "").split(",")
for user in admin_users:
    username, email, phone = user.split(":")
    user = User(username=username, phone=phone, email=email, is_admin=True)
    session.add(user)

# Commit the transaction
try:
    session.commit()
    print(f"{(admin_users.count)} Admin user(s) added successfully!")
except Exception as e:
    session.rollback()
    print(f"Error occurred: {e}")
finally:
    session.close()
