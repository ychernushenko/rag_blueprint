from embedding.datasources.core.document import BaseDocument


class HackernewsDocument(BaseDocument):
    """
    A document class for Hacker News stories.

    Inherits from BaseDocument and provides a method to create a document
    from a Hacker News story dictionary.

    Attributes:
        text: Markdown-formatted story content
        metadata: Extracted story metadata including dates, IDs, and URLs
        excluded_embed_metadata_keys: Metadata keys to exclude from embeddings
        excluded_llm_metadata_keys: Metadata keys to exclude from LLM context
    """

    @classmethod
    def from_story(cls, story: dict) -> "HackernewsDocument":
        """
        Create a HackernewsDocument from a Hacker News story dictionary.

        Args:
            story (dict): A dictionary containing the Hacker News story data.

        Returns:
            HackernewsDocument: An instance of HackernewsDocument with the title and URL set.
        """
        document = cls(
            text=story.get("title", "") + " " + story.get("url", ""),
            metadata=HackernewsDocument._get_metadata(story),
        )
        return document

    @staticmethod
    def _get_metadata(story: dict) -> dict:
        """Extract and format page metadata.

        Args:
            story: Dictionary containing Hacker news story details

        Returns:
            dict: Structured metadata including type and IDs
        """
        return {
            "type": story["type"],
            "id": story["id"],
            "title": story["title"],
            "url": f"https://news.ycombinator.com/item?id={ story["id"]}",
        }
