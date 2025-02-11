from abc import ABC
from enum import Enum
from typing import Any, Callable, Literal, Optional, Union

import tiktoken
from pydantic import ConfigDict, Field, SecretStr
from pydantic_settings import BaseSettings
from transformers import AutoTokenizer

from common.bootstrap.configuration.pipeline.embedding.embedding_model.splitting_configuration import (
    SplittingConfiguration,
)
from common.bootstrap.secrets_configuration import ConfigurationWithSecrets
from common.builders.embedding_builders import (
    HuggingFaceEmbeddingModelBuilder,
    OpenAIEmbeddingModelBuilder,
    VoyageEmbeddingModelBuilder,
)


# Enums
class EmbeddingModelProviderNames(str, Enum):
    HUGGING_FACE = "hugging_face"
    OPENAI = "openai"
    VOYAGE = "voyage"


# Secrets
class HuggingFaceSecrets(BaseSettings):
    # Placeholder to succeed secrets intialization
    model_config = ConfigDict(
        extra="ignore",
    )


class OpenAIEmbeddingModelSecrets(BaseSettings):
    model_config = ConfigDict(
        env_file_encoding="utf-8",
        env_prefix="RAGKB__EMBEDDING_MODELS__OPEN_AI__",
        env_nested_delimiter="__",
        extra="ignore",
    )

    api_key: Optional[SecretStr] = Field(
        None, description="API key for the model"
    )


class VoyageSecrets(BaseSettings):
    model_config = ConfigDict(
        env_file_encoding="utf-8",
        env_prefix="RAGKB__EMBEDDING_MODELS__VOYAGE__",
        env_nested_delimiter="__",
        extra="ignore",
    )

    api_key: Optional[SecretStr] = Field(
        None, description="API key for the model"
    )


# Configuration


class EmbeddingModelConfiguration(ConfigurationWithSecrets, ABC):
    provider: EmbeddingModelProviderNames = Field(
        ..., description="The provider of the embedding model."
    )
    name: str = Field(..., description="The name of the embedding model.")
    tokenizer_name: str = Field(
        ...,
        description="The name of the tokenizer used by the embedding model.",
    )
    batch_size: int = Field(64, description="The batch size for embedding.")

    splitting: Optional[SplittingConfiguration] = Field(
        None, description="The splitting configuration for the embedding model."
    )
    tokenizer_func: Optional[Callable] = Field(
        None,
        description="The tokenizer function used by the embedding model.",
        exclude=True,
    )

    def model_post_init(self, context: Any) -> None:
        super().model_post_init(context)
        self.tokenizer_func = self.get_tokenizer()

    def get_tokenizer(self) -> Callable:
        match self.provider:
            case (
                EmbeddingModelProviderNames.HUGGING_FACE
                | EmbeddingModelProviderNames.VOYAGE
            ):
                return AutoTokenizer.from_pretrained(
                    self.tokenizer_name
                ).tokenize
            case EmbeddingModelProviderNames.OPENAI:
                return tiktoken.encoding_for_model(self.tokenizer_name).encode
            case _:
                raise ValueError(
                    f"Tokenizer for `{self.provider}` provider not found."
                )


class HuggingFaceConfiguration(EmbeddingModelConfiguration):
    provider: Literal[EmbeddingModelProviderNames.HUGGING_FACE] = Field(
        ..., description="The provider of the embedding model."
    )
    secrets: HuggingFaceSecrets = Field(
        None, description="The secrets for the language model."
    )

    builder: Callable = Field(
        HuggingFaceEmbeddingModelBuilder.build,
        description="The builder for the embedding model.",
        exclude=True,
    )


class OpenAIEmbeddingModelConfiguration(EmbeddingModelConfiguration):

    provider: Literal[EmbeddingModelProviderNames.OPENAI] = Field(
        ..., description="The provider of the embedding model."
    )
    max_request_size_in_tokens: int = Field(
        8191,
        description="Maximum size of the request in tokens.",
    )
    secrets: OpenAIEmbeddingModelSecrets = Field(
        None, description="The secrets for the language model."
    )

    builder: Callable = Field(
        OpenAIEmbeddingModelBuilder.build,
        description="The builder for the embedding model.",
        exclude=True,
    )

    def model_post_init(self, __context):
        super().model_post_init(__context)
        if self.splitting:
            self.batch_size = (
                self.max_request_size_in_tokens
                // self.splitting.chunk_size_in_tokens
            )


class VoyageConfiguration(EmbeddingModelConfiguration):

    provider: Literal[EmbeddingModelProviderNames.VOYAGE] = Field(
        ..., description="The provider of the embedding model."
    )
    secrets: VoyageSecrets = Field(
        None, description="The secrets for the language model."
    )

    builder: Callable = Field(
        VoyageEmbeddingModelBuilder.build,
        description="The builder for the embedding model.",
        exclude=True,
    )


AVAILABLE_EMBEDDING_MODELS = Union[
    OpenAIEmbeddingModelConfiguration,
    HuggingFaceConfiguration,
    VoyageConfiguration,
]
