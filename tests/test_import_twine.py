from unittest.mock import mock_open, patch

import pytest
from flask import Flask, session

from app.navigation.import_twine import ImportTwine


class TestImportTwine:
    @pytest.fixture(autouse=True)
    def setup(self, app: Flask):
        self.app = app
        self.Session = app.extensions["Session"]

    def test_parse_twee_file(self):
        mock_twee_content = """
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

        with patch("builtins.open", mock_open(read_data=mock_twee_content)):
            twine = ImportTwine("mock_file.twee")
            passages = twine.parse_twee_file()

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
