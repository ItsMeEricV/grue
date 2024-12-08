from unittest.mock import mock_open, patch

import pytest
from flask import Flask, session

from app.models import Decision, DecisionDestination, Location, Season, User
from app.navigation.import_twine import ImportTwine
from app.navigation.nav import Nav
from app.users.user_locations import UserLocationStore
from app.users.users import UserStore


class TestImportTwine:
    mock_twee_content: str = """:: StoryTitle
Test Story

:: StoryData
{
  "ifid": "43048DD4-5A6B-4D29-BCC6-F418D5460FED",
  "format": "Harlowe",
  "format-version": "3.3.9",
  "start": "Introduction",
  "zoom": 1
}

:: Begin Getting Excited {"position":"1075,750","size":"100,100"}
You look around and begin to laugh. You see many trees and clouds.
[[I am happy]]
[[I fail to be happy and pass out->You Awake]]

:: I am happy {"position":"1075,875","size":"100,100"}
Satisfied with your happiness, and having no concern over how you came to be here in the first place, you shuffle off to find home.
YOU'VE WON

:: Introduction {"position":"900,400","size":"100,100"}
Welcome to Text Game!
[[Begin Your Adventure->You Awake]]

:: Go Back To Sleep {"position":"725,725","size":"100,100"}
Unconcerned with your stickiness, you allow the warmth from the sun and the soft breeze to coax you back to sleep.
[[You Awake]]

:: You Awake {"position":"900,600","size":"100,100"}
You awake to find yourself in a field. You are covered in honey.
[[Go Back To Sleep]]
[[Begin Getting Excited]]
"""

    @pytest.fixture(autouse=True)
    def setup(self, app: Flask):
        self.app = app
        self.Session = app.extensions["Session"]

    def test_parse_twee_file(self):

        with patch("builtins.open", mock_open(read_data=self.mock_twee_content)):
            twine = ImportTwine("mock_file.twee", "mock_file.twee")
            passages = twine.parse_twee_file()

            assert twine.metadata is not None
            assert twine.metadata["ifid"] == "43048DD4-5A6B-4D29-BCC6-F418D5460FED"
            assert twine.metadata["start"] == "Introduction"
            assert twine.metadata["zoom"] == 1
            assert twine.metadata["format"] == "Harlowe"
            assert twine.story_title == "Test Story"
            assert len(passages) == 5
            assert passages[0].name == "Begin Getting Excited"
            assert (
                passages[0].content
                == "You look around and begin to laugh. You see many trees and clouds."
            )
            assert passages[0].links[0].label == "I am happy"
            assert passages[0].links[0].target == "I am happy"
            assert passages[0].links[1].label == "I fail to be happy and pass out"
            assert passages[0].links[1].target == "You Awake"

    def test_insert_story(self):
        with patch("builtins.open", mock_open(read_data=self.mock_twee_content)):
            twine = ImportTwine("mock_file.twee", "mock_file.twee")
            twine.parse_twee_file()

            with self.app.app_context():
                # Add test user
                user = User(
                    username="user1", email="user1@example.com", phone=1111111111
                )
                with self.Session.begin() as db_session:
                    db_session.add(user)

                twine.insert_story()
                with self.Session.begin() as db_session:
                    season = db_session.query(Season).first()
                    assert db_session.query(Season).count() == 1
                    assert db_session.query(Location).count() == 5
                    assert db_session.query(Decision).count() == 5
                    assert db_session.query(DecisionDestination).count() == 6
                    assert season.name == "Test Story"
                    assert season.origin_file == "mock_file.twee"
                    assert season.genesis_location_id is not None

                    # Set the user in the session
                    with self.app.test_request_context():
                        session["user"] = {"email": "user1@example.com"}
                        user = UserStore.get_current_user()
                        assert user is not None
                        nav = Nav.from_user(user)
                        assert nav.get_location_id() == season.genesis_location_id
                        assert nav.get_season_id() == season.id
                        location_description, decisions = nav.fetch_decisions()
                        assert location_description == "Welcome to Text Game!"
                        assert len(decisions) == 1
                        assert decisions[0].description == "Begin Your Adventure"
                        assert decisions[0].position == 0

                        # move to the next location
                        second_location_id = decisions[0].destination_location_id
                        nav.set_location(second_location_id)
                        location_description, decisions = nav.fetch_decisions()
                        assert (
                            location_description
                            == "You awake to find yourself in a field. You are covered in honey."
                        )
                        assert len(decisions) == 2
                        assert decisions[0].description == "Go Back To Sleep"
                        assert decisions[0].position == 0
                        assert decisions[1].description == "Begin Getting Excited"
                        assert decisions[1].position == 1
                        user_location = UserLocationStore.fetch(
                            season.id,
                            user.id,
                        )
                        assert user_location is not None
                        assert user_location.location_id == second_location_id
