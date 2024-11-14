import uuid

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
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
    email: Mapped[str | None] = mapped_column(VARCHAR(255), unique=True, nullable=True)
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
    location: Mapped["Location"] = relationship(
        back_populates="season", single_parent=True
    )


class Location(Base):
    __tablename__ = "locations"
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    description: Mapped[str] = mapped_column(TEXT, nullable=False)
    season: Mapped["Season"] = relationship(back_populates="location")

    # One-to-many relationship: one location can have many source decisions
    source_decisions: Mapped[list["Decision"]] = relationship(
        "Decision",
        back_populates="source_location",
        foreign_keys="[Decision.source_location_id]",
    )

    # Many-to-many relationship: one location can be the destination for many decisions
    destination_decisions: Mapped[list["Decision"]] = relationship(
        "Decision",
        secondary="decision_destinations",
        back_populates="destination_locations",
        primaryjoin="Location.id == DecisionDestination.destination_location_id",
        secondaryjoin="Decision.id == DecisionDestination.decision_id",
    )

    def __repr__(self) -> str:
        return f"<Location(id={self.id}, description={self.description})>"


class Decision(Base):
    __tablename__ = "decisions"
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_location_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "locations.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
    )

    # One-to-many relationship: a decision has one source location
    source_location: Mapped["Location"] = relationship(
        "Location", back_populates="source_decisions", foreign_keys=[source_location_id]
    )

    # Many-to-many relationship to Location via decision_destinations association table
    destination_locations: Mapped[list["Location"]] = relationship(
        "Location",
        secondary="decision_destinations",
        back_populates="destination_decisions",
        primaryjoin="Decision.id == DecisionDestination.decision_id",
        secondaryjoin="Location.id == DecisionDestination.destination_location_id",
    )

    def __repr__(self) -> str:
        return f"<Decision(id={self.id}, source_location_id={self.source_location_id})>"


# Association table for the many-to-many relationship
class DecisionDestination(Base):
    __tablename__ = "decision_destinations"
    decision_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "decisions.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    destination_location_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "locations.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    description: Mapped[str] = mapped_column(TEXT, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        # Ensure there is only ever a single position for a location
        # For example, if a location has two decisions, the positions should be 0 and 1
        UniqueConstraint(
            "destination_location_id",
            "position",
            name="destionation_location_position_unique",
        ),
    )

    def __repr__(self) -> str:
        return f"<DecisionDestination(decision_id={self.decision_id}, destination_location_id={self.destination_location_id}, description={self.description}, position={self.position})>"
