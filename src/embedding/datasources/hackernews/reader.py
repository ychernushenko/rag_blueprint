import logging
from typing import List

import requests
from tqdm import tqdm

from common.bootstrap.configuration.pipeline.embedding.datasources.datasources_configuration import (
    HackernewsDatasourceConfiguration,
)
from embedding.datasources.core.reader import BaseReader
from embedding.datasources.hackernews.document import HackernewsDocument


class HackernewsReader(BaseReader):
    """Reader for extracting top stories from Hacker News.

    Implements document extraction from Hacker News, handling pagination
    and export limits. Supports both synchronous and asynchronous retrieval.

    Attributes:
        export_limit: Maximum number of documents to extract
        base_url: Base URL for Hacker News API
    """

    def __init__(
        self,
        configuration: HackernewsDatasourceConfiguration,
    ):
        """Initialize the Hacker News reader.

        Args:
            configuration: Settings for Hacker News access and limits
        """
        super().__init__()
        self.export_limit = configuration.export_limit
        self.base_url = configuration.base_url

    def get_all_documents(self) -> List[HackernewsDocument]:
        """Synchronously fetch all top stories from Hacker News.

        Returns:
            List[HackernewsDocument]: List of extracted documents

        Note:
            Not implemented - use get_all_documents_async instead.
        """
        pass

    async def get_all_documents_async(self) -> List[HackernewsDocument]:
        """Asynchronously fetch all top stories from Hacker News.

        Retrieves top stories from Hacker News, respecting export limit.

        Returns:
            List[HackernewsDocument]: List of extracted and processed documents
        """
        logging.info(
            f"Fetching top stories from Hacker News with limit {self.export_limit}"
        )
        top_stories_url = f"{self.base_url}/v0/topstories.json"
        response = requests.get(top_stories_url)
        response.raise_for_status()
        story_ids = response.json()

        if self.export_limit is not None:
            story_ids = story_ids[: self.export_limit]

        documents = []
        for story_id in tqdm(story_ids, desc="Fetching Hacker News stories"):
            story_url = f"{self.base_url}/v0/item/{story_id}.json"
            story_response = requests.get(story_url)
            story_response.raise_for_status()
            story = story_response.json()
            documents.append(HackernewsDocument.from_story(story))

        return documents
