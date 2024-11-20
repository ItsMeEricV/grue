import uuid

from sqlalchemy import select

from ..db import get_db_session
from ..models import Season

"""
Basic season getter functions until we have more need for season CRUD
"""


class SeasonStore:
    @staticmethod
    def get_current_season() -> Season:
        """
        Get the current season

        Returns:
            Season
        """
        season = get_db_session().execute(select(Season)).scalars().first()
        if season is None:
            raise ValueError("No season found")
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
