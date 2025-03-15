from injector import inject

from common.bootstrap.configuration.pipeline.embedding.datasources.datasources_configuration import (
    HackernewsDatasourceConfiguration,
)
from common.bootstrap.configuration.pipeline.embedding.embedding_model.embedding_model_binding_keys import (
    BoundEmbeddingModelMarkdownSplitter,
)
from embedding.datasources.core.cleaner import Cleaner
from embedding.datasources.hackernews.cleaner import HackernewsCleaner
from embedding.datasources.hackernews.manager import HackernewsDatasourceManager
from embedding.datasources.hackernews.reader import HackernewsReader


class HackernewsDatasourceManagerBuilder:
    """Builder for creating Hacker News datasource manager instances.

    Provides factory method to create configured HackernewsDatasourceManager
    with required components for content processing.
    """

    @staticmethod
    @inject
    def build(
        configuration: HackernewsDatasourceConfiguration,
        reader: HackernewsReader,
        cleaner: Cleaner,
        splitter: BoundEmbeddingModelMarkdownSplitter,
    ) -> HackernewsDatasourceManager:
        """Creates a configured Hacker News datasource manager.

        Args:
            configuration: Hacker News access and processing settings
            reader: Component for reading Hacker News content
            cleaner: Component for cleaning raw content
            splitter: Component for splitting content into chunks

        Returns:
            HackernewsDatasourceManager: Configured manager instance
        """
        return HackernewsDatasourceManager(
            configuration=configuration,
            reader=reader,
            cleaner=cleaner,
            splitter=splitter,
        )


class HackernewsReaderBuilder:
    """Builder for creating Hacker News reader instances.

    Provides factory method to create configured HackernewsReader objects.
    """

    @staticmethod
    @inject
    def build(
        configuration: HackernewsDatasourceConfiguration,
    ) -> HackernewsReader:
        """Creates a configured Hacker News reader.

        Args:
            configuration: Hacker News access settings

        Returns:
            HackernewsReader: Configured reader instance
        """
        return HackernewsReader(
            configuration=configuration,
        )


class HackernewsCleanerBuilder:
    """Builder for creating Hacker News content cleaner instances.

    Provides factory method to create Cleaner objects for Hacker News content.
    """

    @staticmethod
    @inject
    def build() -> HackernewsCleaner:
        """Creates a content cleaner for Hacker News.

        Returns:
            Cleaner: Configured cleaner instance
        """
        return HackernewsCleaner()
