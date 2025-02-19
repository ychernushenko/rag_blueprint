from injector import inject
from llama_index.core import get_response_synthesizer
from llama_index.core.prompts.base import PromptTemplate
from llama_index.core.prompts.prompt_type import PromptType
from llama_index.core.response_synthesizers import BaseSynthesizer

from common.bootstrap.configuration.pipeline.augmentation.query_engine.synthesizer.synthesizer_binding_keys import (
    BoundLLM,
)
from common.bootstrap.configuration.pipeline.augmentation.query_engine.synthesizer.synthesizer_configuration import (
    TreeSynthesizerConfiguration,
)

CUSTOM_PROMPT_TEMPLATE = PromptTemplate(
    (
        "Context information from multiple sources is below.\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "Based on the above context answer to the below query with a lot of enthusiasim and humoristic sense\n"
        "Query: {query_str}\n"
        "Answer: "
    ),
    prompt_type=PromptType.SUMMARY,
)


class TreeSynthesizerBuilder:
    """Builder for creating tree-based response synthesizer instances.

    Provides factory method to create configured synthesizers that use
    hierarchical summarization for response generation.
    """

    @staticmethod
    @inject
    def build(
        llm: BoundLLM,
        configuration: TreeSynthesizerConfiguration,
    ) -> BaseSynthesizer:
        """Creates a configured tree-based response synthesizer.

        Args:
            llm: Language model for response generation.
            configuration: Synthesizer settings including response mode
                and streaming options.

        Returns:
            BaseSynthesizer: Configured synthesizer instance using tree
                summarization strategy.
        """

        return get_response_synthesizer(
            llm=llm,
            response_mode=configuration.response_mode,
            streaming=configuration.streaming,
            summary_template=CUSTOM_PROMPT_TEMPLATE,
        )
