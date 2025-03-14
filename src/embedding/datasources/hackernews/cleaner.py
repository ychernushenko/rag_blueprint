from typing import List

from tqdm import tqdm

from embedding.datasources.core.cleaner import BaseCleaner
from embedding.datasources.hackernews.document import HackernewsDocument


class HackernewsCleaner(BaseCleaner):
    """
    The `HackernewsCleaner` class is a concrete implementation of `BaseCleaner` for cleaning Hacker News documents.
    """

    def clean(
        self, documents: List[HackernewsDocument]
    ) -> List[HackernewsDocument]:
        """
        Clean the list of Hacker News documents. If the title or url is empty, it is not added to the cleaned documents.

        :param documents: List of HackernewsDocument objects
        :return: List of cleaned HackernewsDocument objects
        """
        cleaned_documents = []

        print("NUMBER_OF_DOCUMENTS" + len(documents))
        for document in HackernewsCleaner._get_documents_with_tqdm(documents):
            if not HackernewsCleaner._has_empty_fields(document):
                cleaned_documents.append(document)

        print("NUMBER_OF_CLEANED_DOCUMENTS" + len(cleaned_documents))
        return cleaned_documents

    @staticmethod
    def _get_documents_with_tqdm(documents: List[HackernewsDocument]):
        """
        Return the documents with tqdm progress bar if GlobalSettings.SHOW_PROGRESS is True, else return the documents as is.

        :param documents: List of HackernewsDocument objects
        """
        return tqdm(documents, desc="[Hacker News] Cleaning documents")

    @staticmethod
    def _has_empty_fields(document: HackernewsDocument) -> bool:
        """
        Check if the document has empty title or url fields.

        :param document: A HackernewsDocument object
        :return: True if the title or url is empty, False otherwise
        """
        return not document.title or not document.url
