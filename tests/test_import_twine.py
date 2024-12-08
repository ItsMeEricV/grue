from unittest.mock import mock_open, patch

import pytest
from flask import Flask

from app.models import Decision, DecisionDestination, Location, Season
from app.navigation.import_twine import ImportTwine


class TestImportTwine:
    mock_twee_content: str = """
:: StoryTitle
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

    # def test_parse_twee_file(self):

    #     with patch("builtins.open", mock_open(read_data=self.mock_twee_content)):
    #         twine = ImportTwine("mock_file.twee")
    #         passages = twine.parse_twee_file()

    #         assert twine.metadata["ifid"] == "43048DD4-5A6B-4D29-BCC6-F418D5460FED"
    #         assert twine.metadata["start"] == "Introduction"
    #         assert twine.metadata["zoom"] == 1
    #         assert twine.metadata["format"] == "Harlowe"
    #         assert twine.story_title == "Test Story"
    #         assert len(passages) == 5
    #         assert passages[0].name == "Begin Getting Excited"
    #         assert (
    #             passages[0].content
    #             == "You look around and begin to laugh. You see many trees and clouds."
    #         )
    #         assert passages[0].links[0].label == "I am happy"
    #         assert passages[0].links[0].target == "I am happy"
    #         assert passages[0].links[1].label == "I fail to be happy and pass out"
    #         assert passages[0].links[1].target == "You Awake"

    def test_insert_story(self):
        with patch("builtins.open", mock_open(read_data=self.mock_twee_content)):
            twine = ImportTwine("mock_file.twee")
            twine.parse_twee_file()
            with self.app.app_context():
                twine.insert_story()
                with self.Session.begin() as db_session:
                    season = db_session.query(Season).first()
                    assert db_session.query(Season).count() == 1
                    assert db_session.query(Location).count() == 5
                    assert db_session.query(Decision).count() == 3
                    assert db_session.query(DecisionDestination).count() == 5
                    season = db_session.query(Season).first()
                    assert season.name == "Test Story"
                    assert season.origin_file == "mock_file.twee"
                    assert db_session.query(Decision).first().location_id == 1
                    assert db_session.query(Decision).first().destination_id == 2
                    assert db_session.query(Decision).first().label == "I am happy"
                    assert (
                        db_session.query(Decision).first().destination.label
                        == "I am happy"
                    )
                    assert (
                        db_session.query(Decision).first().destination.location_id == 2
                    )
                    assert (
                        db_session.query(Location).first().name
                        == "Begin Getting Excited"
                    )
                    assert db_session.query(Location).first().content == (
                        "You look around and begin to laugh. You see many trees and clouds."
                    )
                    assert db_session.query(Location).first().season_id == season.id
