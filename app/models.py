import uuid
from typing import Optional

from sqlalchemy import BigInteger, Boolean, CheckConstraint, create_engine
from sqlalchemy.dialects.postgresql import UUID, VARCHAR
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from config import MainConfig

engine: Engine = create_engine(MainConfig.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(VARCHAR(255), unique=True, nullable=False)
    phone: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    CheckConstraint("phone > 0", name="phone_positive")
    email: Mapped[Optional[str]] = mapped_column(
        VARCHAR(255), unique=True, nullable=True
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<User({self.id}, username={self.username}, phone={self.phone}, email={self.email}, is_admin={self.is_admin}>"
