# How to Add a New Vector Store Implementation

This guide demonstrates how to add support for a new vector store implementation, using `Chroma` as an example. The implementation is defined in [vector_store_configuration.py](https://github.com/feld-m/rag_blueprint/blob/main/src/common/bootstrap/configuration/pipeline/embedding/vector_store/vector_store_configuration.py).

## Step 1: Add Dependencies

Add the required packages to `pyproject.toml`:

```toml
...
chromadb==0.6.3
llama-index-vector-stores-chroma==0.3.0
...
```

## Step 2: Configure Docker Service

Add the vector store service to [docker-compose.yml](https://github.com/feld-m/rag_blueprint/blob/main/build/workstation/docker/docker-compose.yml):

```yml
name: rag
services:
...
  chroma:
    image: chromadb/chroma:0.6.4.dev19
    environment:
      CHROMA_HOST_PORT: ${RAG__VECTOR_STORE__PORT_REST}
    ports:
      - "${RAG__VECTOR_STORE__PORT_REST}:${RAG__VECTOR_STORE__PORT_REST}"
    restart: unless-stopped
    volumes:
      - ./.docker-data/chroma:/chroma/chroma/
...
```

## Step 3: Define Vector Store Type

Add the vector store to the `VectorStoreName` enum in `vector_store_configuration.py`:

```py
class VectorStoreName(str, Enum):
    ...
    CHROMA = "chroma"
```

The enum value must match the service name in the Docker configuration.

## Step 4: Configure Secrets Management

Define a secrets configuration class. For services without secrets:

```py
class ChromaSecrets(BaseSettings):
    model_config = ConfigDict(
        extra="ignore",
    )
```

For services requiring secrets:

```py
class ChromaSecrets(BaseSettings):
    model_config = ConfigDict(
        env_file_encoding="utf-8",
        env_prefix="RAG__VECTOR_STORE__",
        env_nested_delimiter="__",
        extra="ignore",
    )

    some_secret_1: Optional[SecretStr] = Field(
        None, description="First secret."
    )
    some_secret_2: Optional[SecretStr] = Field(
        None, description="Second secret."
    )
```

Secrets are read from `configurations/secrets.{environment}.env` during client initialization.

## Step 5: Implement the Vector Store Configuration

Define the Chroma configuration class for the LLM, extending the base `ChromaConfiguration`:

```py
class ChromaConfiguration(VectorStoreConfiguration):
    name: Literal[VectorStoreName.CHROMA] = Field(
        ..., description="The name of the vector store."
    )
    secrets: ChromaSecrets = Field(
        None, description="The secrets for the Qdrant vector store."
    )
```

This class includes fields from `VectorStoreConfiguration`, plus the ones defined in the snippet.

- `name`: Constrained to the Chroma value, ensuring only configurations matching `VectorStoreName.CHROMA` are valid.
- `secrets`: Links the configuration to the `ChromaSecrets` class.

**Example JSON Configuration**

```json
...
    "vector_store": {
        "name": "chroma",
        "collection_name": "new-collection",
        "host": "chroma",
        "protocol": "http",
        "ports": {
            "rest": 6333
        }
    }
...
```

- `name`: Name of the vector store to be used, corresponds to the vector store name from [docker-compose.yml](https://github.com/feld-m/rag_blueprint/blob/main/build/workstation/docker/docker-compose.yml).
- `collection_name`: Name of the collection to which documents will be embedded.
- `host`: Vector store host in the form of IP or domain e.g. 127.0.0.1.
- `protocol`: Used for creating URL in combination with `host`.
- `ports`: Ports on which the vector store is available. Used for creating URL in combination with `protocol` and `host`.

## Step 6: Expose LLM Configuration

To make Pydantic parse the corresponding JSON object to our `ChromaConfiguration`, add it to the `AVAILABLE_VECTOR_STORES` variable:

```py
AVAILABLE_VECTOR_STORES = Union[..., ChromaConfiguration]
```

## Step 7: Create the Vector Store Client Builder

Define how the Chroma client is built to enable pre-run validation. Update [client_builders.py](https://github.com/feld-m/rag_blueprint/blob/main/src/common/builders/client_builders.py):

```py
from chromadb import HttpClient as ChromaHttpClient
from chromadb.api import ClientAPI as ChromaClient
from injector import inject

from common.bootstrap.configuration.pipeline.embedding.vector_store.vector_store_configuration import (
    ChromaConfiguration,
    ...
)

class ChromaClientBuilder:
    """Builder for creating configured Chroma client instances.

    Provides factory method to create ChromaClient with vector store settings.
    """

    @staticmethod
    @inject
    def build(configuration: ChromaConfiguration) -> ChromaClient:
        """Creates a configured Chroma client instance.

        Args:
            configuration: Chroma connection settings.

        Returns:
            HttpClient: Configured HTTP client instance for Chroma.
        """
        return ChromaHttpClient(
            host=configuration.host,
            port=configuration.ports.rest,
        )
```

**Explanation**:

- **Dependencies**: Use dependency injection (@inject) to ensure proper initialization.
- **Configuration**: Extracts `host`, `port` from the `ChromaConfiguration`.

## Step 8: Create the Vector Store Builder

The builder is responsible for initializing the vector store. Our implementation leverages [llamaindex](https://docs.llamaindex.ai/en/stable/). Add the builder logic to [vector_store_builders.py](https://github.com/feld-m/rag_blueprint/blob/main/src/common/builders/vector_store_builders.py):

```py
from injector import inject
from llama_index.vector_stores.chroma import ChromaVectorStore
...
import (
    ChromaConfiguration,
    ...
)

...

class ChromaStoreBuilder:
    """Builder for creating configured Chroma vector store instances.

    Provides factory method to create ChromaVectorStore with client and collection settings.
    """

    @staticmethod
    @inject
    def build(
        configuration: ChromaConfiguration,
    ) -> ChromaVectorStore:
        """Creates a configured Chroma vector store instance.

        Args:
            chroma_client: Client for Chroma vector database interaction.
            configuration: Chroma settings including collection name.

        Returns:
            ChromaVectorStore: Configured Chroma instance.
        """
        return ChromaVectorStore(
            host=configuration.host,
            port=str(configuration.ports.rest),
            collection_name=configuration.collection_name,
        )
```

**Explanation**:

- **Dependencies**: Use dependency injection (@inject) to ensure proper initialization.
- **Configuration**: Extracts `host`, `port`, and `collection_name` from the `ChromaConfiguration`.
- **Library Integration**: Uses `llama_index.vector_stores.chroma` to create the vector store instance.

## Step 9: Vector Store Validation

Before the embedding process, it is checked if the defined `collection-name` already exists at the vector store. In such a case, the embedding process is skipped. Implement the vector store validator in [vector_store_validators.py](https://github.com/feld-m/rag_blueprint/blob/main/src/embedding/validators/vector_store_validators.py):

```py
from chromadb.api import ClientAPI as ChromaClient
from common.bootstrap.configuration.pipeline.embedding.vector_store.vector_store_configuration import (
    ChromaConfiguration,
    ...
)

class ChromaVectorStoreValidator(VectorStoreValidator):
    """Validator for Chroma vector store configuration.

    Validates collection settings and existence for Chroma
    vector store backend.

    Attributes:
        configuration: Settings for vector store
        chroma_client: Client for Chroma interactions
    """

    def __init__(
        self,
        configuration: ChromaConfiguration,
        chroma_client: ChromaClient,
    ):
        """Initialize validator with configuration and client.

        Args:
            configuration: Chroma vector store settings
            chroma_client: Client for Chroma operations
        """
        self.configuration = configuration
        self.chroma_client = chroma_client

    def validate(self) -> None:
        """
        Validate the Chroma vector store settings.
        """
        self.validate_collection()

    def validate_collection(self) -> None:
        """Validate Chroma collection existence.

        Raises:
            CollectionExistsException: If collection already exists
        """
        collection_name = self.configuration.collection_name
        if collection_name in self.chroma_client.list_collections():
            raise CollectionExistsException(collection_name)
```

## Step 10: Vector Store Validator Builder

For the above vector store validator, add a builder to [vector_store_builders.py](https://github.com/feld-m/rag_blueprint/blob/main/src/embedding/validators/builders.py):

```py
from common.bootstrap.configuration.pipeline.embedding.vector_store.vector_store_configuration import (
    ChromaConfiguration,
    ...
)

...

class ChromaVectorStoreValidatorBuilder:
    """Builder for creating Chroma vector store validator instances.

    Provides factory method to create configured ChromaVectorStoreValidator
    objects with required components.
    """

    @staticmethod
    @inject
    def build(
        configuration: ChromaConfiguration, chroma_client: ChromaClient
    ) -> ChromaVectorStoreValidator:
        """Create configured Chroma validator instance.

        Args:
            configuration: Settings for vector store
            chroma_client: Client for Chroma interactions

        Returns:
            ChromaVectorStoreValidator: Configured validator instance
        """
        return ChromaVectorStoreValidator(
            configuration=configuration, chroma_client=chroma_client
        )

```

## Step 11: Create Vector Store Binder

The last step is to add the corresponding binder responsible for initializing the vector store. Update [vector_store_binders.py](https://github.com/feld-m/rag_blueprint/blob/main/src/common/bootstrap/configuration/pipeline/embedding/vector_store/vector_store_binder.py):

```py
from chromadb.api import ClientAPI as ChromaClient

from common.bootstrap.configuration.pipeline.embedding.vector_store.vector_store_configuration import (
    ChromaConfiguration,
    ...
)

from common.builders.client_builders import (
    ChromaClientBuilder,
    ...
)
from common.builders.vector_store_builders import (
    ChromaStoreBuilder,
    ...
)
from embedding.validators.builders import (
    ChromaVectorStoreValidatorBuilder,
    ...
)

...

class ChromaBinder(BaseBinder):
    """Binder for the Chroma components."""

    def bind(self) -> None:
        """Bind the Chroma components."""
        self._bind_configuration()
        self._bind_client()
        self._bind_vector_store()
        self._bind_validator()

    def _bind_configuration(self) -> None:
        """Bind the Chroma configuration."""
        self.binder.bind(
            ChromaConfiguration,
            to=self.configuration.pipeline.embedding.vector_store,
            scope=singleton,
        )

    def _bind_client(self) -> None:
        """Bind the Chroma client."""
        self.binder.bind(
            ChromaClient,
            to=ChromaClientBuilder.build,
            scope=singleton,
        )

    def _bind_vector_store(self) -> None:
        """Bind the Qdrant store."""
        self.binder.bind(
            VectorStore,
            to=ChromaStoreBuilder.build,
            scope=singleton,
        )

    def _bind_validator(self) -> None:
        """Bind the Chroma vector store validator."""
        self.binder.bind(
            VectorStoreValidator,
            to=ChromaVectorStoreValidatorBuilder.build,
        )

...

class VectorStoreBinder(BaseBinder):
    """Binder for the vector store component."""

    mapping = {
        ...
        VectorStoreName.CHROMA: ChromaBinder,
    }

    ...
```

This ensures that all instances defined in this guide are successfully initialized during the bootstrap and ready to use. From this point, the Chroma database is available for use in the pipeline.
