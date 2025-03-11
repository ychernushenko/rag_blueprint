from abc import ABC
from enum import Enum
from typing import Literal, Union

from pydantic import BaseModel, Field

from common.bootstrap.secrets_configuration import ConfigurationWithSecrets


# Enums
class VectorStoreName(str, Enum):
    QDRANT = "qdrant"
    CHROMA = "chroma"


# Secrets


# Configuration
class VectorStorePortsConfiguration(BaseModel):
    rest: int = Field(
        ..., description="The port for the HTTP server of the vector store."
    )


class VectorStoreConfiguration(ConfigurationWithSecrets, ABC):
    name: VectorStoreName = Field(
        ..., description="The name of the vector store."
    )
    ports: VectorStorePortsConfiguration = Field(
        ..., description="The ports for the vector store."
    )
    collection_name: str = Field(
        ..., description="The collection name in the vector store."
    )
    host: str = Field(
        "127.0.0.1", description="Host of the vector store server"
    )
    protocol: Union[Literal["http"], Literal["https"]] = Field(
        "http", description="The protocol for the vector store."
    )


class QDrantConfiguration(VectorStoreConfiguration):
    name: Literal[VectorStoreName.QDRANT] = Field(
        ..., description="The name of the vector store."
    )

    @property
    def url(self) -> str:
        return f"{self.protocol}://{self.host}:{self.ports.rest}"


class ChromaConfiguration(VectorStoreConfiguration):
    name: Literal[VectorStoreName.CHROMA] = Field(
        ..., description="The name of the vector store."
    )


AVAILABLE_VECTOR_STORES = Union[QDrantConfiguration, ChromaConfiguration]
