import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from ..db import get_db_session
from ..models import UserLocation

"""
User location store
"""


class UserLocationStore:
    @staticmethod
    def fetch(
        season_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> UserLocation | None:
        """
        Get a user location by user id

        Returns:
            UserLocations
        """
        user_location = (
            get_db_session()
            .execute(
                select(UserLocation).filter(
                    UserLocation.user_id == user_id, UserLocation.season_id == season_id
                )
            )
            .scalars()
            .one_or_none()
        )
        return user_location

    @staticmethod
    def set(
        season_id: uuid.UUID, user_id: uuid.UUID, location_id: uuid.UUID
    ) -> UserLocation:
        """
        Set a user location

        Args:
            season_id (uuid.UUID): The season id
            user_id (uuid.UUID): The user id
            location_id (uuid.UUID): The location id
        """
        stmt = (
            insert(UserLocation)
            .values(season_id=season_id, user_id=user_id, location_id=location_id)
            .on_conflict_do_update(
                index_elements=["season_id", "user_id"],
                set_={"location_id": location_id},
            )
        )
        # TODO: Verify that the user is allowed to set this location based on the season and user's current location
        # For now we just blindly trust we can set this new location
        db_session = get_db_session()
        db_session.execute(stmt)
        db_session.commit()

        return UserLocation(
            season_id=season_id, user_id=user_id, location_id=location_id
        )
