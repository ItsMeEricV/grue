from __future__ import annotations

import uuid
from typing import TypedDict

from flask import current_app
from sqlalchemy import select

from ..db import get_db_session
from ..models import Decision, DecisionDestination, Location, Season, User, UserLocation
from ..seasons.seasons import SeasonStore
from ..users.user_locations import UserLocationStore

"""
Navigating around in the world

Instantiate a Nav object given a User object. The Nav object will have a current location
and a season. The Nav object can fetch decisions for the current location.
"""


class Nav:

    Destination = TypedDict(
        "Destination",
        {"destination_location_id": uuid.UUID, "description": str, "position": int},
    )

    __season_id: uuid.UUID
    __location_id: uuid.UUID
    __user: User

    @classmethod
    def from_user(cls, user: User) -> Nav:
        """
        Create a Nav object from a user

        Args:
            user (User): The user

        Returns:
            Nav: The Nav object
        """
        season = SeasonStore.get_current_season()
        if season.genesis_location_id is None:
            raise ValueError("No genesis location set for season")

        user_location = UserLocationStore.fetch(
            season.id,
            user.id,
        )
        if user_location is None:
            return cls(season.id, season.genesis_location_id, user)

        return cls(season.id, user_location.location_id, user)

    def __init__(
        self, season_id: uuid.UUID, current_location_id: uuid.UUID, user: User
    ):
        self.__season_id = season_id
        self.__location_id = current_location_id
        self.__user = user

    """
    Getters
    """

    def get_location_id(self) -> uuid.UUID:
        return self.__location_id

    def get_season_id(self) -> uuid.UUID:
        return self.__season_id

    def get_user(self) -> User:
        return self.__user

    """
    Navigation core methods
    """

    def fetch_decisions(self) -> tuple[str, list[DecisionDestination]]:
        """
        Get a location and its decisions

        Args:
            location_id (str): The location id

        Returns:
            tuple[str, list[DecisionDestination]]: The location description and a list of decisions
        """
        stmt = (
            select(DecisionDestination, Location.description)
            .select_from(DecisionDestination)
            .join(Decision)
            .join(Location)
            .where(Decision.source_location_id == self.__location_id)
            .order_by(DecisionDestination.position)
        )
        results = list(get_db_session().execute(stmt).all())
        description = None
        destinations: list[DecisionDestination] = []
        for row in results:
            description = row.description
            destinations.append(row.DecisionDestination)

        # We should always have one or more decisions for a location, but if have no
        # decisions, we should still return the location description
        if description is None:
            stmt = select(Location.description).where(Location.id == self.__location_id)
            description = get_db_session().execute(stmt).scalar_one()

        return (description, destinations)

    def set_location(self, location_id: uuid.UUID) -> UserLocation:
        """
        Set the current location

        Args:
            location_id (str): The location id
        """
        self.__location_id = location_id

        return UserLocationStore.set(
            self.__season_id, self.__user.id, self.__location_id
        )

    @staticmethod
    def create_location(season: Season, description: str) -> uuid.UUID:
        """
                Create a new location

                Args:
                    description (str): The description of the location
        .UUID
                Returns:
                    id (str): id of the newly created location
        """
        db_session = get_db_session()
        id: uuid.UUID = uuid.uuid4()
        location = Location(id=id, description=description, season_id=season.id)
        db_session.add(location)
        db_session.commit()
        return id

    @staticmethod
    def creation_decisions(
        source_location_id: uuid.UUID, destinations: list[Destination]
    ) -> Decision:
        """
        Create a new decision
        Args:
            source_location_id (str): The source location id
            destinations (list[Destination]): A list of destinations

        Returns:
            Decision: The newly created decision
        """
        decision_id = uuid.uuid4()
        decision = Decision(id=decision_id, source_location_id=source_location_id)

        Session = current_app.extensions["Session"]
        with Session.begin() as db_session:
            db_session.add(decision)
            for destination in destinations:
                decision_destination = DecisionDestination(
                    decision_id=decision_id,
                    destination_location_id=destination["destination_location_id"],
                    description=destination["description"],
                    position=destination["position"],
                )
                db_session.add(decision_destination)
        return decision
