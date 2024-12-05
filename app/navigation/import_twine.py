import json
import re
from dataclasses import dataclass
from typing import List, TypedDict


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
    filename: str

    def __init__(self, filename: str):
        self.filename = filename


class ImportTwine(Import):
    story_title: str
    metadata: HarloweMetadata
    passages: list[TwinePassage] = []

    def parse_twee_file(self) -> list[TwinePassage]:
        """
        Parses a Twee file and extracts passage content and connections.

        Args:
            file_path: Path to the Twee file.

        Returns:
            A dictionary where keys are passage names and values are tuples containing
            the passage content and a list of links to other passages.
        """

        with open(self.filename, "r", encoding="utf-8") as file:
            twee_content = file.read()

        # Regular expression to match a passage
        passage_pattern = r"\s*(.+?)\s*(?:\{\s*.*?\s*\})?\n(.*?)(?=\n::|$)"
        matches = twee_content.split("\n::")

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
                m = "".join(lines[1:])
                try:
                    self.metadata: HarloweMetadata = json.loads(
                        m, object_hook=lambda d: HarloweMetadata(**d)
                    )
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON for StoryData: {e}")

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
