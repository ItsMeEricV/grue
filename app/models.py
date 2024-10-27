import uuid

from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import BOOLEAN, UUID, VARCHAR
from sqlalchemy.orm import declarative_base, sessionmaker

from config import Config

from . import db

Base = declarative_base()
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = "users"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(VARCHAR(255), unique=True, nullable=False)
    phone = db.Column(db.BigInteger, unique=True, nullable=False)
    db.CheckConstraint("phone > 0", name="phone_positive")
    email = db.Column(VARCHAR(255), unique=True, nullable=True)
    is_admin = db.Column(BOOLEAN, default=False)

    def __repr__(self) -> str:
        return f"<User({self.id}, username={self.username}, phone={self.phone}, email={self.email}, is_admin={self.is_admin}>"
