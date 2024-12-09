import datetime
import uuid

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
    and_,
)
from sqlalchemy.dialects.postgresql import TEXT, TIMESTAMP, UUID, VARCHAR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(VARCHAR(255), unique=True, nullable=False)
    phone: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    CheckConstraint("phone > 0", name="phone_positive")
    email: Mapped[str | None] = mapped_column(VARCHAR(255), unique=True, nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    # One-to-many relationship: one user can have many user_locations
    user_locations: Mapped[list["UserLocation"]] = relationship(
        "UserLocation", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User({self.id}, username={self.username}, phone={self.phone}, email={self.email}, is_admin={self.is_admin}>"


class Season(Base):
    __tablename__ = "seasons"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(VARCHAR(2048), nullable=False)
    genesis_location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "locations.id", use_alter=True, name="fk_seasons_genesis_location_id"
        ),
        nullable=True,
    )
    default: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    date_created: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default="now()"
    )
    origin_file: Mapped[str] = mapped_column(VARCHAR(2048), nullable=True)

    # relationships
    genesis_location: Mapped["Location"] = relationship(
        back_populates="season",
        single_parent=True,
        foreign_keys="[Location.id]",
        primaryjoin="Location.id == Season.genesis_location_id",
    )
    locations: Mapped[list["Location"]] = relationship(
        "Location",
        back_populates="season",
        foreign_keys="[Location.season_id]",
        primaryjoin="Location.season_id == Season.id",
        cascade="all, delete-orphan",
    )

    # One-to-many relationship: one season can have many user_locations
    user_seasons: Mapped[list["UserLocation"]] = relationship(
        "UserLocation", back_populates="season", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index(
            "ix_season_default_unique",
            "default",
            unique=True,
            postgresql_where=and_(default == True, genesis_location_id != None),
        ),
    )

    def __repr__(self) -> str:
        return f"<Season(id={self.id}, name={self.name}, genesis_location_id={self.genesis_location_id}, default={self.default}, date_created={self.date_created})>"


class UserLocation(Base):
    __tablename__ = "user_locations"
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    season_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("seasons.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("locations.id", onupdate="CASCADE", ondelete="CASCADE"),
    )

    # Many-to-one relationship: a user_location has one user
    user: Mapped["User"] = relationship("User", back_populates="user_locations")
    # Many-to-one relationship: a user_location has one location
    location: Mapped["Location"] = relationship(
        "Location", back_populates="user_locations"
    )
    # Many-to-one relationship: a user_location has one season
    season: Mapped["Season"] = relationship("Season", back_populates="user_seasons")


class Location(Base):
    __tablename__ = "locations"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    description: Mapped[str] = mapped_column(TEXT, nullable=False)
    season_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "seasons.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="fk_locations_season_id",
        ),
        nullable=False,
    )

    season: Mapped["Season"] = relationship(
        back_populates="locations", foreign_keys=[season_id]
    )

    # One-to-many relationship: one location can have many source decisions
    source_decisions: Mapped[list["Decision"]] = relationship(
        "Decision",
        back_populates="source_location",
        foreign_keys="[Decision.source_location_id]",
        cascade="all, delete-orphan",
    )

    # Many-to-many relationship: one location can be the destination for many decisions
    destination_decisions: Mapped[list["Decision"]] = relationship(
        "Decision",
        secondary="decision_destinations",
        back_populates="destination_locations",
        primaryjoin="Location.id == DecisionDestination.destination_location_id",
        secondaryjoin="Decision.id == DecisionDestination.decision_id",
    )

    # One-to-many relationship: one location can have many user_locations
    user_locations: Mapped[list["UserLocation"]] = relationship(
        "UserLocation", back_populates="location", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_locations_season_id", "season_id"),)

    def __repr__(self) -> str:
        return f"<Location(id={self.id}, description={self.description})>"


class Decision(Base):
    __tablename__ = "decisions"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "locations.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
    )

    # One-to-many relationship: a decision has one source location
    source_location: Mapped["Location"] = relationship(
        "Location",
        back_populates="source_decisions",
        foreign_keys=[source_location_id],
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
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    decision_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "decisions.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    destination_location_id: Mapped[uuid.UUID] = mapped_column(
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
            "decision_id",
            "destination_location_id",
            "position",
            name="destination_location_position_unique",
        ),
    )

    def __repr__(self) -> str:
        return f"<DecisionDestination(id={self.id}, decision_id={self.decision_id}, destination_location_id={self.destination_location_id}, description={self.description}, position={self.position})>"
