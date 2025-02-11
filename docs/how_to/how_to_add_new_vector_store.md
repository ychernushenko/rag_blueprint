# How To Add New Vector Store Implementation

This guide outlines the process of adding support for a new vector store implementation. We use the existing `Chroma` as an example, located in [vector_store_configuration.py](https://github.com/feld-m/rag_blueprint/blob/main/src/common/bootstrap/configuration/pipeline/embedding/vector_store/vector_store_configuration.py) file.

## Update Project Dependencies

Since we will use [Chroma](https://www.trychroma.com/) vector store through [llamaindex](https://docs.llamaindex.ai/en/stable/) implementation add correspodning entries to `pyproject.toml`:

```toml
...
chromadb==0.6.3
llama-index-vector-stores-chroma==0.3.0
...
```

## Docker Configuration

In order to include it in the intialization script chroma has to be added to [docker-compose.yml](https://github.com/feld-m/rag_blueprint/blob/main/build/workstation/docker/docker-compose.yml):

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

## Define Vector Store Enum Name

Vector store name has to be added to `VectorStoreName` enum from `vector_store_configuration.py` as follows:

```py
class VectorStoreName(str, Enum):
    ...
    CHROMA = "chroma"
```

String value has to correspond to the name in docker configuration.

## Configure Vector Store Secrets

Next, define how secrets for the vector store are handled. In our case chroma does not require any secrets therefore we define it as follows:

```py
class ChromaSecrets(BaseSettings):
    pass
```

Otherwise, we would implement secrets as follows:

```py
class ChromaSecrets(BaseSettings):
    model_config = ConfigDict(
        env_file="configuration/secrets.default.env",
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

Secrets would be read from secrets file (`env_vars/.env`) and further used for client initialization.

## Implement the Vector Store Configuration

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

Which already includes the fields from `VectorStoreConfiguration`, plus these defined in the snippet.

`name` Constrained to the Chroma value, ensuring only configurations matching VectorStoreName.Chroma are valid.

`secrets`: Links the configuration to the ChromaSecrets class.

**Example JSON Configuration**

```json
...
    "vector_store": {
        "name": "chroma",
        "collection_name": "new-collection",
        "host": "chroma",                   // replace with valid host e.g. 127.0.0.1
        "protocol": "http",
        "ports": {
            "rest": 6333
        }
    }
...
```

`chroma` Name of the vector store to be used, corresponds to the vector store name from [docker-compose.yml](https://github.com/feld-m/rag_blueprint/blob/main/build/workstation/docker/docker-compose.yml).

`collection_name` Name of the collection to which documents will be embedded.

`host` Vector store host in the form of ip or domain e.g. 127.0.0.1.

`protocol` Used for creating url in combination with `host`.

`ports` Ports on which vector store is available. Used for creating url in combination with `protocol` and `host`.

## Expose LLM Configuration

To make pydantic parse corresponding json object to our `ChromaConfiguration` we need to add it to `AVAILABLE_VECTOR_STORES` variable:

```py
AVAILABLE_VECTOR_STORES = Union[..., ChromaConfiguration]
```


## Create the Vector Store Client Builder

We need to define how Chroma client is build in order to enable pre-run validation. For that we update [client_builders.py](https://github.com/feld-m/rag_blueprint/blob/main/src/common/builders/client_builders.py):

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
            HttpClient: Configured http client instance for Chroma.
        """
        return ChromaHttpClient(
            host=configuration.host,
            port=configuration.ports.rest,
        )
```

**Explanation**:

- **Dependencies**: Use dependency injection (@inject) to ensure proper initialization.

- **Configuration**: Extracts `host`, `port` from the `ChromaConfiguration`.

## Create the Vector Store Builder

The builder is responsible for initializing the vector store. Our implementation leverages [llamaindex](https://docs.llamaindex.ai/en/stable/), to add the builder logic to [vector_store_builders.py](https://github.com/feld-m/rag_blueprint/blob/main/src/common/builders/vector_store_builders.py) we add necessary builder.

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

## Vector Store Validation

Before embedding process it is checked if defined `collection-name` already exists at the vector store. In such case embedding process is skipped. To enable such checks we need to implement vector store validator in [vector_store_validators.py](https://github.com/feld-m/rag_blueprint/blob/main/src/embedding/validators/vector_store_validators.py):

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
        Valiuate the Chroma vector store settings.
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

## Vector Store Validator Builder

For the above vector store validator we add builder to [vector_store_builders.py](https://github.com/feld-m/rag_blueprint/blob/main/src/embedding/validators/builders.py):

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

## Create Vector Store Binder

The last thing to do is add the correspodning binder that is responsible for initializing the vector store. For that we update [vector_store_binders.py](https://github.com/feld-m/rag_blueprint/blob/main/src/common/bootstrap/configuration/pipeline/embedding/vector_store/vector_store_binder.py):

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

It ensures us that all instances that we defined through this guide are successfully initialized during the bootstrap and ready to use. From this point Chroma database is available for use through [`configuration.json](https://github.com/feld-m/rag_blueprint/blob/main/src/common/bootstrap/configuration/configuration.json )
