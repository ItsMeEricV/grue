import uuid
from sqlalchemy.dialects.postgresql import UUID
#from flask_sqlalchemy import SQLAlchemy
from . import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.BigInteger, unique=True, nullable=False)
    db.CheckConstraint('phone > 0', name='phone_positive')

    def __repr__(self) -> str:
        return f'<User({self.id}, username={self.username}, phone={self.phone}>'