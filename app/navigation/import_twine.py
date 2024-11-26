import json
import re
from typing import Dict, List, Optional, Tuple


class Import:
    filename: str

    def __init__(self, filename: str):
        self.filename = filename


class ImportTwine(Import):

    def parse_twee_filev1(self) -> Dict[str, Tuple[str, List[str]]]:
        """
        Parses a Twee file and extracts passage content and connections.

        Args:
            file_path: Path to the Twee file.

        Returns:
            A dictionary where keys are passage names and values are tuples containing
            the passage content and a list of links to other passages.
        """

        passages: Dict[str, Tuple[str, List[str]]] = {}
        with open(self.filename, "r", encoding="utf-8") as file:
            twee_content = file.read()

        # Regular expression to match a passage
        passage_pattern = r"::\s*(.+?)\s*(?:\{\s*.*?\s*\})?\n(.*?)(?=\n::|$)"
        matches = re.findall(passage_pattern, twee_content, re.DOTALL)

        for match in matches:
            passage_name = match[0]
            passage_content = match[1].strip()

            # Regular expression to match links within a passage
            link_pattern = r"\[\[(.*?)(?:->(.*?))?\]\]"
            links = re.findall(link_pattern, passage_content)

            # Extract only the destination passage names from the links
            passage_links = [link[1] if link[1] else link[0] for link in links]

            passages[passage_name] = (passage_content, passage_links)

        return passages

    def parse_twee_file(self) -> List[Tuple[str, str, List[str]]]:
        """
        Parses a Twee file, extracts passage content and connections, and orders them.

        Args:
            file_path: Path to the Twee file.

        Returns:
            A list of tuples, where each tuple contains the passage name,
            the first line of the passage content, and a list of links
            to other passages. The list is ordered according to the story flow.
        """

        with open(self.filename, "r", encoding="utf-8") as file:
            twee_content = file.read()

        # Extract StoryData JSON
        story_data_match = re.search(
            r"::\s*StoryData\n(.*?)(?=\n::|$)", twee_content, re.DOTALL
        )
        if not story_data_match:
            raise ValueError("StoryData not found in the Twee file.")
        story_data = json.loads(story_data_match.group(1).strip())
        start_passage = story_data.get("start")
        if not start_passage:
            raise ValueError("Start passage not found in StoryData.")
        # Extract passages
        passage_pattern = r"::\s*(.+?)\s*(?:\{\s*.*?\s*\})?\n(.*?)(?=\n::|$)"
        matches = re.findall(passage_pattern, twee_content, re.DOTALL)
        passages: Dict[str, Tuple[str, List[str]]] = {}
        for match in matches:
            passage_name = match[0]
            passage_lines = match[1].strip().splitlines()
            passage_content = passage_lines[0] if passage_lines else ""

            # Extract links
            link_pattern = r"\[\[(.*?)(?:->(.*?))?\]\]"
            links = re.findall(link_pattern, match[1])
            passage_links = [link[1] if link[1] else link[0] for link in links]

            passages[passage_name] = (passage_content, passage_links)

        # Order passages based on story flow
        ordered_passages = []
        current_passage = start_passage
        while current_passage:
            content, links = passages.get(current_passage, ("", []))
            ordered_passages.append((current_passage, content, links))
            if links:
                current_passage = links[0]  # Follow the first link
            else:
                current_passage = None

        return ordered_passages
