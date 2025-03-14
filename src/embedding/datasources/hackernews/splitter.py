from typing import List

from llama_index_client import TextNode

from common.bootstrap.configuration.pipeline.embedding.embedding_model.embedding_model_binding_keys import (
    BoundEmbeddingModelMarkdownSplitter,
)
from embedding.datasources.core.splitter import BaseSplitter
from embedding.datasources.hackernews.document import HackernewsDocument


class HackernewsSplitter(BaseSplitter):
    """
    The `HackernewsSplitter` class is a concrete class that defines the interface for splitting Hacker News documents into text nodes.
    """

    def __init__(
        self,
        markdown_splitter: BoundEmbeddingModelMarkdownSplitter,
    ):
        """
        Initialize the HackernewsSplitter with a markdown splitter.

        :param markdown_splitter: MarkdownSplitter object for splitting documents
        """
        self.markdown_splitter = markdown_splitter

    def split(self, documents: List[HackernewsDocument]) -> List[TextNode]:
        """
        Split the given list of Hacker News documents into text nodes using `markdown_splitter`.

        :param documents: List of HackernewsDocument objects
        :return: List of TextNode objects
        """
        text_nodes = []
        for document in documents:
            text_nodes.extend(
                self.markdown_splitter.split([document.title + document.url])
            )
        return text_nodes
