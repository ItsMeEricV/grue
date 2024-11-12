import uuid
from typing import List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import TEXT, UUID, VARCHAR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(
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


class Season(Base):
    __tablename__ = "seasons"
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(VARCHAR(2048), nullable=False)
    genesis_location_id: Mapped[str] = mapped_column(ForeignKey("locations.id"))
    parent: Mapped["Location"] = relationship(
        back_populates="child", single_parent=True
    )


class Location(Base):
    __tablename__ = "locations"
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    description: Mapped[str] = mapped_column(TEXT, nullable=False)
    child: Mapped["Season"] = relationship(back_populates="parent")
    # many-to-many relationship to Child, bypassing the `Association` class
    children: Mapped[List["Decision"]] = relationship(
        secondary="locations_decisions",
        back_populates="parents",
        foreign_keys="[LocationDecision.destination_location_id, LocationDecision.source_location_id]",
    )

    # association between Parent -> Association -> Child
    child_associations: Mapped[List["LocationDecision"]] = relationship(
        back_populates="parent", foreign_keys="[LocationDecision.source_location_id]"
    )


class Decision(Base):
    __tablename__ = "decisions"
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    description: Mapped[str] = mapped_column(TEXT, nullable=False)
    # many-to-many relationship to Parent, bypassing the `Association` class
    parents: Mapped[List["Location"]] = relationship(
        secondary="locations_decisions", back_populates="children"
    )
    # association between Child -> Association -> Parent
    parent_associations: Mapped[List["LocationDecision"]] = relationship(
        back_populates="child", foreign_keys="[LocationDecision.decision_id]"
    )


class LocationDecision(Base):
    __tablename__ = "locations_decisions"
    source_location_id: Mapped[str] = mapped_column(
        ForeignKey(
            "locations.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    destination_location_id: Mapped[str] = mapped_column(
        ForeignKey(
            "locations.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    decision_id: Mapped[str] = mapped_column(
        ForeignKey(
            "decisions.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # association between Assocation -> Child
    child: Mapped["Decision"] = relationship(
        back_populates="parent_associations",
        foreign_keys="[LocationDecision.decision_id]",
    )

    # association between Assocation -> Parent
    parent: Mapped["Location"] = relationship(
        back_populates="child_associations",
        foreign_keys="[LocationDecision.source_location_id]",
    )

    __table_args__ = (
        Index("locations_decisions_position_idx", "source_location_id", "position"),
        UniqueConstraint(
            "source_location_id", "position", name="source_position_unique"
        ),
    )
