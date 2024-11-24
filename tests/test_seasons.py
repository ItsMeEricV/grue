import uuid

import pytest
from flask import Flask

from app.models import Season
from app.seasons.seasons import SeasonStore


class TestSeasonStore:
    @pytest.fixture(autouse=True)
    def setup(self, app: Flask):
        self.app = app
        self.Session = app.extensions["Session"]

    def test_get_current_season_default_set(self):
        with self.app.app_context():
            # Create a mock season
            id = uuid.uuid4()
            mock_season = Season(
                id=id,
                name="Season 1",
                genesis_location_id=uuid.uuid4(),
                default=True,
                version=1,
            )

            with self.Session.begin() as db_session:
                db_session.add(mock_season)

            # Call the method
            season = SeasonStore.get_current_season()

            # Assert the result
            assert season.id == id

    def test_get_current_season_no_default_set(self):
        with self.app.app_context():
            # Create a mock season
            id = uuid.uuid4()
            mock_season = Season(
                id=id,
                name="Season 2",
                genesis_location_id=uuid.uuid4(),
                default=False,
                version=2,
            )

            with self.Session.begin() as db_session:
                db_session.add(mock_season)

            # Call the method
            season = SeasonStore.get_current_season()

            # Assert the result
            assert season.id == id
            assert season.default == False

    def test_get_current_season_no_seasons_found(self):
        with self.app.app_context():
            # Call the method and assert it raises ValueError
            with pytest.raises(ValueError, match="No seasons found"):
                SeasonStore.get_current_season()
