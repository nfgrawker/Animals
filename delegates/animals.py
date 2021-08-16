from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import desert
import requests

from utils.config import Config
from utils.decorators import bad_server, singleton
from utils.log import Logger


@dataclass
class AnimalStub:
    """DTO for Animal Stubs."""

    id: int
    name: str
    born_at: Optional[int] = None


@dataclass
class PageOfAnimals:
    """DTO for a Page of Animals."""

    page: int
    total_pages: int
    items: List[AnimalStub]


@dataclass
class AnimalComplete:
    """DTO for Complete Animal Information."""

    id: int
    name: str
    friends: List[str]
    born_at: Optional[str] = None


@singleton
class AnimalsDelegate:
    """Class for communicating with Animals Server."""

    def __init__(self):
        self.log = Logger()
        self.config = Config()
        self.pages = self.get_pages()
        self.all_animal_stubs: List[AnimalStub] = []
        self.all_animal_complete: List[AnimalComplete] = []

    @bad_server
    def get_pages(self) -> int:
        """Get total page numbers as they can be different every time."""
        response = requests.get(
            f"{self.config.data.base_url}/animals/v1/animals?page=0"
        )
        response.raise_for_status()
        _schema = desert.schema(PageOfAnimals)
        _schema_response: PageOfAnimals = _schema.load(response.json())
        self.log.info(f"{_schema_response.total_pages} pages found.")

        return _schema_response.total_pages

    @bad_server
    def get_current_page(self, current_page: int) -> List[AnimalStub]:
        """Query current page and return list of Animal Stubs."""
        response = requests.get(
            f"{self.config.data.base_url}/animals/v1/animals?page={current_page}"
        )
        response.raise_for_status()
        _schema = desert.schema(PageOfAnimals)
        _schema_response: PageOfAnimals = _schema.load(response.json())

        return _schema_response.items

    def get_all_animals(self) -> None:
        """Append the current page into the stub list."""
        current_page = 1
        self.log.info("Getting all animal stubs.")
        while current_page < self.pages:
            animals = self.get_current_page(current_page)
            current_page += 1
            for animal in animals:
                self.all_animal_stubs.append(animal)
        self.log.info(f"{len(self.all_animal_stubs)} animals found.")

    @bad_server
    def get_animal_by_id(self, id: int) -> AnimalComplete:
        """Query one animal by Id and change to our format."""
        response = requests.get(f"{self.config.data.base_url}/animals/v1/animals/{id}")
        response.raise_for_status()
        _schema = desert.schema(AnimalComplete)
        raw_animal = response.json()
        if raw_animal["born_at"] is not None:
            raw_animal["born_at"] = str(
                datetime.fromtimestamp(raw_animal["born_at"] / 100).isoformat()
            )
        raw_animal["friends"] = raw_animal["friends"].split(",")
        _schema_response: AnimalComplete = _schema.load(raw_animal)

        return _schema_response

    def expand_animal_stubs(self) -> None:
        """Get Animal info and pass to list."""
        self.log.info("Expanding stubs.")
        self.all_animal_complete = [
            self.get_animal_by_id(animal.id) for animal in self.all_animal_stubs
        ]
        self.log.info("All stubs have been expanded.")

    @bad_server
    def post_list_of_complete_animals(
        self, list_of_animals: List[AnimalComplete]
    ) -> None:
        """Post, max 100 at a time."""
        response = requests.post(
            f"{self.config.data.base_url}/animals/v1/home", json=list_of_animals
        )
        response.raise_for_status()
        self.log.info(response.content)

    def parse_and_send_lists_of_animals(self):
        """Parse the schemas back and send to post."""
        _schema_to_post = desert.schema(AnimalComplete)
        list_to_send = []
        for idx, animal in enumerate(self.all_animal_complete, start=1):
            list_to_send.append(_schema_to_post.dump(animal))
            if idx % 100 == 0:
                self.log.info(f"sending {idx} of {len(self.all_animal_complete)}")
                self.post_list_of_complete_animals(list_to_send)
                list_to_send = []

        self.log.info(f"sending {len(self.all_animal_complete)} of {len(self.all_animal_complete)}")
        self.post_list_of_complete_animals(list_to_send)
