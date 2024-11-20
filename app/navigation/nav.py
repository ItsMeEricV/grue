import uuid
from typing import TypedDict

from flask import current_app
from sqlalchemy import select

from ..db import get_db_session
from ..models import Decision, DecisionDestination, Location

"""
Navigating around in the world
"""


class Nav:

    Destination = TypedDict(
        "Destination",
        {"destination_location_id": uuid.UUID, "description": str, "position": int},
    )

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

    @staticmethod
    def get_decisions_for_location(
        location_id: uuid.UUID,
    ) -> list[tuple[DecisionDestination, str]]:
        """
        Get a location and its decisions

        Args:
            location_id (str): The location id

        Returns:
            Location: The location
        """
        stmt = (
            select(DecisionDestination, Location.description)
            .select_from(DecisionDestination)
            .join(Decision)
            .join(Location)
            .where(Decision.source_location_id == location_id)
            .order_by(DecisionDestination.position)
        )
        results = list(get_db_session().execute(stmt).all())
        return [(row.DecisionDestination, row.description) for row in results]
