from embedding.datasources.core.document import BaseDocument


class HackernewsDocument(BaseDocument):
    """
    A document class for Hacker News stories.

    Inherits from BaseDocument and provides a method to create a document
    from a Hacker News story dictionary.

    Attributes:
        title (str): The title of the Hacker News story.
        url (str): The URL of the Hacker News story.
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
            title=story.get("title", ""),
            url=story.get("url", ""),
        )
        return document
