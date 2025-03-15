import sys
from typing import List
from unittest.mock import Mock, patch

import pytest

sys.path.append("./src")

from common.bootstrap.configuration.pipeline.embedding.datasources.datasources_configuration import (
    HackernewsDatasourceConfiguration,
)
from embedding.datasources.hackernews.document import HackernewsDocument
from embedding.datasources.hackernews.reader import HackernewsReader


class Fixtures:
    def __init__(self):
        self.export_limit: int = None
        self.base_url: str = None
        self.story_ids: List[int] = []
        self.stories: dict = {}

    def with_export_limit(self, export_limit: int) -> "Fixtures":
        self.export_limit = export_limit
        return self

    def with_base_url(self) -> "Fixtures":
        self.base_url = "https://hacker-news.firebaseio.com"
        return self

    def with_stories(self, number_of_stories: int) -> "Fixtures":
        for i in range(number_of_stories):
            story_id = i
            self.story_ids.append(story_id)
            self.stories[story_id] = {
                "title": f"Title {i}",
                "url": f"https://news.ycombinator.com/item?id={i}",
                "type": "story",  # Add this line
                "id": story_id,  # Add this line
            }
        return self


class Arrangements:
    def __init__(self, fixtures: Fixtures):
        self.fixtures = fixtures
        self.configuration = Mock(spec=HackernewsDatasourceConfiguration)
        self.configuration.export_limit = self.fixtures.export_limit
        self.configuration.base_url = self.fixtures.base_url
        self.service = HackernewsReader(configuration=self.configuration)

    def on_requests_get(self) -> "Arrangements":
        def requests_get_side_effect(url, *args, **kwargs):
            if url.endswith("topstories.json"):
                return Mock(
                    status_code=200, json=lambda: self.fixtures.story_ids
                )
            else:
                story_id = int(url.split("/")[-1].split(".")[0])
                return Mock(
                    status_code=200,
                    json=lambda: self.fixtures.stories[story_id],
                )

        self.requests_get_patcher = patch(
            "requests.get", side_effect=requests_get_side_effect
        )
        self.mock_requests_get = self.requests_get_patcher.start()
        return self

    def stop_patches(self):
        self.requests_get_patcher.stop()


class Assertions:
    def __init__(self, arrangements: Arrangements):
        self.fixtures = arrangements.fixtures
        self.service = arrangements.service

    def assert_documents(self, documents: List[HackernewsDocument]):
        expected_story_ids = self.fixtures.story_ids
        if self.fixtures.export_limit is not None:
            expected_num_documents = min(
                self.fixtures.export_limit, len(expected_story_ids)
            )
        else:
            expected_num_documents = len(expected_story_ids)
        assert len(documents) == expected_num_documents
        for i, actual_document in enumerate(documents):
            expected_story_id = expected_story_ids[i]
            expected_story = self.fixtures.stories[expected_story_id]
            assert (
                actual_document.text
                == expected_story["title"] + " " + expected_story["url"]
            )


class Manager:
    def __init__(self, arrangements: Arrangements):
        self.fixtures = arrangements.fixtures
        self.arrangements = arrangements
        self.assertions = Assertions(arrangements=arrangements)

    def get_service(self) -> HackernewsReader:
        return self.arrangements.service


@pytest.mark.asyncio
class TestHackernewsReader:
    @pytest.mark.parametrize(
        "export_limit,number_of_stories",
        [
            (5, 10),
            (10, 15),
            (None, 8),
            (3, 5),
            (20, 25),
            (None, 0),
            (5, 0),
        ],
    )
    async def test(self, export_limit: int, number_of_stories: int) -> None:
        # Arrange
        manager = Manager(
            Arrangements(
                Fixtures()
                .with_export_limit(export_limit)
                .with_base_url()
                .with_stories(number_of_stories)
            ).on_requests_get()
        )
        service = manager.get_service()

        # Act
        documents = await service.get_all_documents_async()

        # Assert
        manager.assertions.assert_documents(documents)
