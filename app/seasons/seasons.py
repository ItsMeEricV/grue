import uuid

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from ..db import get_db_session
from ..models import Season

"""
Basic season getter functions until we have more need for season CRUD
"""


class SeasonStore:
    @staticmethod
    def get_current_season() -> Season:
        """
        Get the current season based on the default flag
        If no default season is set, get the latest season based on the version flag

        Returns:
            Season
        """
        db_session = get_db_session()
        try:
            season = (
                db_session.execute(select(Season).filter(Season.default == True))
                .scalars()
                .one()
            )
        except NoResultFound:
            # If no default season is set, get the latest season
            # This shouldn't happen but just in case we have a race condition
            season = (
                db_session.execute(select(Season).order_by(Season.version.desc()))
                .scalars()
                .first()
            )
            if season is None:
                raise ValueError("No seasons found")
        return season

    @staticmethod
    def get_season_by_id(id: uuid.UUID) -> Season:
        """
        Get a season by id

        Returns:
            Season
        """
        season = (
            get_db_session()
            .execute(select(Season).filter(Season.id == id))
            .scalars()
            .first()
        )
        if season is None:
            raise ValueError("No season found")
        return season
