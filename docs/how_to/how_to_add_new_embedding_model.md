# How to Add a New Embedding Model Implementation

This guide demonstrates how to add support for a new embedding model implementation, using OpenAI as an example. The implementation is defined in [embedding_model_configuration.py](https://github.com/feld-m/rag_blueprint/blob/main/src/common/bootstrap/configuration/pipeline/embedding/embedding_model/embedding_model_configuration.py).

## Step 1: Add Dependencies

Add the required packages to `pyproject.toml`:

```toml
...
llama-index-embeddings-openai=0.2.4
...
```

## Step 2: Define the Embedding Model Provider

In *embedding_model_configuration.py*, add the new provider to the `EmbeddingModelProviderNames` enumeration:

```py
class EmbeddingModelProviderNames(str, Enum):
    ...
    OPENAI = "openai"
```

## Step 3: Configure Embedding Model Secrets

Create a secrets class for the new provider:

```py
class OpenAIEmbeddingModelSecrets(BaseSettings):
    model_config = ConfigDict(
        env_file_encoding="utf-8",
        env_prefix="RAG__EMBEDDING_MODELS__OPEN_AI__",
        env_nested_delimiter="__",
        extra="ignore",
    )

    api_key: Optional[SecretStr] = Field(
        None, description="API key for the embedding model"
    )
```

Add the corresponding environment variable to `configurations/secrets.{environment}.env`:

```sh
...
RAG__EMBEDDING_MODELS__OPEN_AI__API_KEY=<openai_api_key>
...
```

## Step 4: Implement the Embedding Model Configuration

Define the configuration class for the new provider:

```py
class OpenAIEmbeddingModelConfiguration(EmbeddingModelConfiguration):

    provider: Literal[EmbeddingModelProviderNames.OPENAI] = Field(
        ..., description="The provider of the embedding model."
    )
    max_request_size_in_tokens: int = Field(
        8191,
        description="Maximum size of the request in tokens.",
    )
    secrets: OpenAIEmbeddingModelSecrets = Field(
        None, description="The secrets for the language embedding model."
    )

    builder: Callable = Field(
        OpenAIEmbeddingModelBuilder.build,
        description="The builder for the embedding model.",
        exclude=True,
    )

    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.batch_size = (
            self.max_request_size_in_tokens
            // self.splitting.chunk_size_in_tokens
        )
```

## Step 5: Setup Tokenizer Initialization

Customize the `get_tokenizer` method in `EmbeddingModelConfiguration`:

```py
import tiktoken
...
class EmbeddingModelConfiguration(BaseModel):
    ...
    def get_tokenizer(self) -> Callable:
        match self.provider:
            ...
            case EmbeddingModelProviderNames.OPENAI:
                return tiktoken.encoding_for_model(self.tokenizer_name).encode
            ...
```

## Step 6: Example JSON Configuration

```json
...
    "embedding_model": {
        "provider": "openai",
        "name": "text-embedding-3-small",
        "tokenizer_name": "text-embedding-3-small",
        "splitting": {
            "name": "basic",
            "chunk_overlap_in_tokens": 50,
            "chunk_size_in_tokens": 384
        }
    }
...
```

## Step 7: Expose Embedding Model Configuration

Add the new configuration to `AVAILABLE_EMBEDDING_MODELS`:

```py
AVAILABLE_EMBEDDING_MODELS = Union[..., OpenAIEmbeddingModelConfiguration]
```

## Step 8: Create the Embedding Model Builder

Add the builder logic to [embedding_builders.py](https://github.com/feld-m/rag_blueprint/blob/main/src/common/builders/embedding_builders.py):

```py
from typing import TYPE_CHECKING

from injector import inject
from llama_index.embeddings.openai import OpenAIEmbedding

if TYPE_CHECKING:
    from common.bootstrap.configuration.pipeline.embedding.embedding_model.embedding_model_configuration import (
        OpenAIEmbeddingModelConfiguration,
    )


class OpenAIEmbeddingModelBuilder:
    """Builder for creating OpenAI embedding model instances.

    Provides factory method to create configured OpenAIEmbedding objects.
    """

    @staticmethod
    @inject
    def build(
        configuration: "OpenAIEmbeddingModelConfiguration",
    ) -> OpenAIEmbedding:
        """Creates a configured OpenAI embedding model.

        Args:
            configuration: Embedding model settings including API key, name and batch size.

        Returns:
            OpenAIEmbedding: Configured embedding model instance.
        """
        return OpenAIEmbedding(
            api_key=configuration.secrets.api_key.get_secret_value(),
            model_name=configuration.name,
            embed_batch_size=configuration.batch_size,
        )
```

After completing these steps, the OpenAI embedding models are ready to be configured and used in the RAG System.
