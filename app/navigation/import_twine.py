import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, TypedDict
from uuid import UUID, uuid4

from flask import current_app
from sqlalchemy import insert, update

from ..models import Decision, DecisionDestination, Location, Season


# Metadata structure for Harlowe format
class HarloweMetadata(TypedDict):
    ifid: str
    format: str
    format_version: str
    start: str
    zoom: int


# The link from one passage to another
# Label is the text displayed to the user. It can be the same as the target passage name.
@dataclass
class TwineLink:
    label: str
    target: str


# A passage in the Twine story, containing one or more links to other passages
@dataclass
class TwinePassage:
    name: str
    content: str
    links: List[TwineLink]


class Import:
    filepath: str
    filename: str

    def __init__(self, filepath: str, filename: str):
        self.filepath = filepath
        self.filename = filename


class ImportTwine(Import):
    """
    Handles importing and parsing of Twine story files in Twee format.

    This class reads a Twee file, extracts the story title, metadata, and passages,
    and creates the necessary database records to represent the story structure.

    Attributes:
        story_title (str): The title of the Twine story
        metadata (HarloweMetadata | None): Story metadata in Harlowe format
        passages (list[TwinePassage]): List of passages making up the story
        season_id (UUID): Unique identifier for this imported story/season
    """

    story_title: str
    metadata: HarloweMetadata | None
    passages: list[TwinePassage] = []
    season_id: UUID

    def __init__(self, filepath: str, filename: str):
        """
        Initialize a new Twine story import.

        Args:
            filepath (str): Path to the Twee file to import
            filename (str): Original filename of the Twee file
        """
        super().__init__(filepath, filename)
        self.story_title: str = ""
        self.metadata = None
        self.passages: List[TwinePassage] = []
        self.season_id: UUID = uuid4()

    def parse_twee_file(self) -> list[TwinePassage]:
        """
        Parses a Twee file and extracts passage content and connections.

        This method reads the Twee file and parses out:
        - Story title
        - Story metadata (must be Harlowe format)
        - Individual passages and their links to other passages

        Args:
            file_path: Path to the Twee file.

        Returns:
            A dictionary where keys are passage names and values are tuples containing
            the passage content and a list of links to other passages.

        Raises:
            json.JSONDecodeError: If story metadata is invalid JSON
            TypeError: If story metadata doesn't match expected format
            ValueError: If story format is not Harlowe
        """

        with open(self.filepath, "r", encoding="utf-8") as file:
            twee_content = file.read()

        # Regular expression to match a passage
        passage_pattern = r"\s*(.+?)\s*(?:\{\s*.*?\s*\})?\n(.*?)(?=\n::|$)"
        matches = twee_content.split("::")

        for match in matches:
            match = match.strip()
            lines = match.split("\n")
            first = lines[0]

            # first line might be empty
            if len(first) == 0:
                continue
            # store the story title
            elif first == "StoryTitle":
                self.story_title = lines[1]
                continue
            # store the story metadata
            elif first == "StoryData":
                try:
                    self.metadata = json.loads(
                        "".join(lines[1:]), object_hook=lambda d: HarloweMetadata(**d)
                    )
                except json.JSONDecodeError as e:
                    # TODO: log this error
                    print(f"Error decoding JSON for StoryData: {e}")
                    raise json.JSONDecodeError(
                        "Error decoding JSON for StoryData", e.doc, e.pos
                    )
                except TypeError as e:
                    # TODO: log this error
                    print(f"Error decoding JSON for StoryData: {e}")
                    raise TypeError("Error decoding JSON for StoryData") from e
                assert self.metadata is not None

                if self.metadata["format"] != "Harlowe":
                    raise ValueError("Only Harlowe format is supported")

                continue
            else:
                # now let's parse the passages
                inner_matches = re.findall(passage_pattern, match, re.DOTALL)

                for match in inner_matches:
                    passage_name = match[0].strip()
                    passage_content = match[1].split("\n")[0].strip()
                    passage = TwinePassage(
                        name=passage_name, content=passage_content, links=[]
                    )

                    # Regular expression to match links within a passage
                    link_pattern = r"\[\[(.*?)(?:->(.*?))?\]\]"
                    links = re.findall(link_pattern, match[1].strip())

                    for link in links:
                        label = link[0]
                        destination = link[1] if link[1] else link[0]
                        passage.links.append(TwineLink(label, destination))

                    self.passages.append(passage)

        return self.passages

    def insert_story(self) -> None:
        """
        Inserts the story into the database.
        Creates a season, locations, decisions, and decision destinations.
        """
        if self.metadata is None:
            raise ValueError("Must call parse_twee_file before insert_story")

        # First create a dict of passage name to uuid
        passage_uuids: dict[str, UUID] = {}

        # we know the content start location will be the genesis_location_id
        genesis_location_id: UUID = uuid4()
        passage_uuids[self.metadata["start"]] = genesis_location_id

        locations: list[Location] = []
        decisions: list[Decision] = []
        decision_destinations: list[DecisionDestination] = []
        self.season_id = uuid4()

        season = Season(
            id=self.season_id,
            name=self.story_title,
            # don't set genesis_location_id here, due to the fk constraint we need to set it after the locations are inserted
            default=False,
            date_created=datetime.now(timezone.utc),
            origin_file=self.filename,
        )

        for passage in self.passages:
            if passage.name not in passage_uuids:
                passage_uuids[passage.name] = uuid4()

        for passage in self.passages:
            locations.append(
                Location(
                    id=passage_uuids[passage.name],
                    description=passage.content,
                    season_id=self.season_id,
                )
            )
            decision = Decision(
                id=uuid4(), source_location_id=passage_uuids[passage.name]
            )
            decisions.append(decision)
            for index, link in enumerate(passage.links):
                decision_destinations.append(
                    DecisionDestination(
                        decision_id=decision.id,
                        destination_location_id=passage_uuids[link.target],
                        description=link.label,
                        position=index,
                    )
                )

        # now insert the data into the database
        # we need to insert the locations first, then the decisions, then the decision destinations
        Session = current_app.extensions["Session"]
        with Session.begin() as db_session:
            db_session.execute(insert(Season), [season.__dict__])
            db_session.execute(
                insert(Location), [location.__dict__ for location in locations]
            )
            db_session.execute(
                insert(Decision), [decision.__dict__ for decision in decisions]
            )
            db_session.execute(
                insert(DecisionDestination),
                [dest.__dict__ for dest in decision_destinations],
            )
            db_session.execute(
                update(Season)
                .where(Season.id == self.season_id)
                .values(genesis_location_id=genesis_location_id)
            )

    def __str__(self):
        return f"ImportTwine({self.filename})"
