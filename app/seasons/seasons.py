import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import NoResultFound

from ..db import get_db_session
from ..models import Location, Season

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
        db_session.close()
        return season

    @staticmethod
    def get_season_by_id(id: uuid.UUID) -> Season:
        """
        Get a season by id

        Returns:
            Season
        """
        db_session = get_db_session()
        season = (
            db_session.execute(select(Season).filter(Season.id == id)).scalars().first()
        )
        if season is None:
            raise ValueError("No season found")
        db_session.close()
        return season

    @staticmethod
    def fetch_seasons_with_counts() -> list[tuple[Season, int]]:
        """
        Fetch all seasons with location count
        For admin pages only! Location counting will get expensive over time

        Returns:
            list[Season]
        """
        db_session = get_db_session()
        stmt = select(Season).order_by(Season.version.asc())
        seasons = db_session.execute(stmt).scalars().all()
        # fetch all locations for each season, grouped by season
        stmt = select(func.count(Location.id), Location.season_id).group_by(
            Location.season_id
        )
        results = db_session.execute(stmt).all()
        db_session.close()

        location_counts: dict[uuid.UUID, int] = {}
        for row in results:
            location_counts[row.season_id] = int(row[0])

        return [(season, location_counts.get(season.id, 0)) for season in seasons]
