import datetime
import uuid

from flask import current_app
from sqlalchemy import func, select
from sqlalchemy.exc import NoResultFound

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
        Session = current_app.extensions["Session"]
        with Session() as db_session:
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
                    db_session.execute(
                        select(Season).order_by(Season.date_created.desc())
                    )
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
        Session = current_app.extensions["Session"]
        with Session() as db_session:
            season = (
                db_session.execute(select(Season).filter(Season.id == id))
                .scalars()
                .first()
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
        Session = current_app.extensions["Session"]
        with Session() as db_session:
            stmt = select(Season).order_by(Season.date_created.asc())
            seasons = db_session.execute(stmt).scalars().all()
            stmt = select(func.count(Location.id), Location.season_id).group_by(
                Location.season_id
            )
            results = db_session.execute(stmt).all()

        location_counts: dict[uuid.UUID, int] = {
            row.season_id: int(row[0]) for row in results
        }

        return [(season, location_counts.get(season.id, 0)) for season in seasons]

    @staticmethod
    def create_season(name: str, origin_file: str) -> uuid.UUID:
        """
        Create a season

        Args:
            name (str): The name of the season

        Returns:
            Season ID
        """
        Session = current_app.extensions["Session"]
        id = uuid.uuid4()
        season = Season(
            id=id,
            name=name,
            date_created=datetime.datetime.now(datetime.timezone.utc),
            origin_file=origin_file,
        )
        with Session.begin() as db_session:
            db_session.add(season)

        return id
