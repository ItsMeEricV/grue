from __future__ import annotations

import uuid
from typing import TypedDict

from flask import current_app
from sqlalchemy import select

from ..db import get_db_session
from ..models import Decision, DecisionDestination, Location, User

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

    # TODO: Once we are ready to persist the user's location, we should make a factory method
    # that takes in a User, fetches its current location, and returns a Nav object. If no
    # current location is found, we should return a Nav object with the genesis location for the default season
    # EXAMPLE
    @classmethod
    def from_user(cls, user: User) -> Nav:
        """
        Create a Nav object from a user

        Args:
            user (User): The user

        Returns:
            Nav: The Nav object
        """
        id = uuid.uuid4()
        id2 = uuid.uuid4()
        return cls(id, id2, user)

    def __init__(
        self, season_id: uuid.UUID, current_location_id: uuid.UUID, user: User
    ):
        self.__season_id = season_id
        self.__location_id = current_location_id
        self.__user = user

    def get_location_id(self) -> uuid.UUID:
        return self.__location_id

    def get_season_id(self) -> uuid.UUID:
        return self.__season_id

    def get_user(self) -> User:
        return self.__user

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

    @staticmethod
    def create_location(description: str) -> uuid.UUID:
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
        location = Location(id=id, description=description)
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
