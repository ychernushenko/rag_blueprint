# How to Configure the RAG System

This guide explains how to customize the RAG system pipeline through configuration files.

## Environments

### Definition

The following environments are supported:

```py
class EnvironmentName(str, Enum):
    DEFAULT = "default"
    LOCAL = "local"
    DEV = "dev"
    TEST = "test"
    PROD = "prod"
```

Each environment requires corresponding configuration and secrets files in the [configurations](https://github.com/feld-m/rag_blueprint/tree/main/configurations) directory:

- Configuration files: `configuration.{environment}.json`
- Secrets files: `secrets.{environment}.env`

The configuration files define the pipeline setup, while secrets files store credentials and tokens. For security, all files in the configurations directory are git-ignored except for `configuration.default.json` and `configuration.local.json`.

### Usage

Run the pipeline with a specific configuration using the `--env` flag:

```sh
build/workstation/init.sh --env default
python src/embed.py --env default
```

## Datasource Configuration

Currently, the following datasources are available:

```py
class DatasourceName(str, Enum):
    NOTION = "notion"
    CONFLUENCE = "confluence"
    PDF = "pdf"
```

Blueprint allows the usage of single or multiple datasources. Adjust the corresponding configuration accordingly:

```json
{
    "pipeline": {
        "embedding": {
            "datasources": [
                {
                    "name": "notion",
                    "export_limit": 100
                },
                {
                    "name": "pdf",
                    "export_limit": 100,
                    "base_path": "data/"
                }
            ]
        }
    }
}
```

Each entry in `datasources` corresponds to a single source that will be sequentially used for the extraction of documents to be further processed. The `name` of each entry must correspond to one of the implemented enums. Datasources' secrets must be added to the environment's secret file. To check configurable options for specific datasources, visit [datasources_configuration.json](https://github.com/feld-m/rag_blueprint/blob/main/src/common/bootstrap/configuration/pipeline/embedding/datasources/datasources_configuration.py).

## LLM Configuration

Currently, LLMs from these providers are supported:

```py
class LLMProviderNames(str, Enum):
    OPENAI = "openai"
    OPENAI_LIKE = "openai-like"
```

`OpenAI` indicates the [OpenAI](https://openai.com/) provider, whereas `OPENAI_LIKE` indicates any LLM exposed through an API compatible with OpenAI's API, e.g., a self-hosted LLM exposed via [TabbyAPI](https://theroyallab.github.io/tabbyAPI/).

Minimal setup requires the use of LLMs in augmentation and evaluation processes. To configure this, adjust the following JSON entries:

```json
{
    "pipeline": {
        "augmentation": {
            "query_engine": {
                "synthesizer": {
                    "name": "tree",
                    "llm": {
                        "provider": "openai",
                        "name": "gpt-4o-mini",
                        "max_tokens": 1024,
                        "max_retries": 3,
                        "context_window": 16384
                    }
                }
            }
        },
        "evaluation": {
            "judge_llm": {
                "provider": "openai",
                "name": "gpt-4o-mini",
                "max_tokens": 1024,
                "max_retries": 3,
                "context_window": 16384
            }
        }
    }
}
```

Providers' secrets must be added to the environment's secret file. The `provider` field must be one of the values from `LLMProviderNames`, and the `name` field indicates the specific model exposed by the provider. To check configurable options for specific providers, visit [llm_configuration.json](https://github.com/feld-m/rag_blueprint/blob/main/src/common/bootstrap/configuration/pipeline/augmentation/query_engine/llm_configuration.py).

In the above case, augmentation and evaluation processes use the same LLM, which might be suboptimal. To change it, simply adjust the entry of one of these:

```json
{
    "pipeline": {
        "augmentation": {
            "query_engine": {
                "synthesizer": {
                    "name": "tree",
                    "llm": {
                        "provider": "openai",
                        "name": "gpt-4o-mini",
                        "max_tokens": 1024,
                        "max_retries": 3,
                        "context_window": 16384
                    }
                }
            }
        },
        "evaluation": {
            "judge_llm": {
                "provider": "openai-like",  // another provider
                "name": "my-llm",           // another llm
                "max_tokens": 512           // different parameters
            }
        }
    }
}
```

## Embedding Model Configuration

Currently, embedding models from these providers are supported:

```py
class EmbeddingModelProviderNames(str, Enum):
    HUGGING_FACE = "hugging_face"
    OPENAI = "openai"
    VOYAGE = "voyage"
```

Any model exposed by these providers can be used in the setup.

Minimal setup requires the use of embedding models in different processes. To configure this, adjust the following JSON entries:

```json
{
    "pipeline": {
        "augmentation": {
            "embedding_model": {
                "provider": "hugging_face",
                "name": "BAAI/bge-small-en-v1.5",
                "tokenizer_name": "BAAI/bge-small-en-v1.5",
                "splitting": {
                    "name": "basic",
                    "chunk_overlap_in_tokens": 50,
                    "chunk_size_in_tokens": 384
                }
            }
        }
    },
    {
        "evaluation": {
            "judge_embedding_model": {
                "provider": "hugging_face",
                "name": "BAAI/bge-small-en-v1.5",
                "tokenizer_name": "BAAI/bge-small-en-v1.5"
            }
        }
    }
}
```

Providers' secrets must be added to the environment's secret file. The `provider` field must be one of the values from `EmbeddingModelProviderNames`, and the `name` field indicates the specific model exposed by the provider. The `tokenizer_name` field indicates the tokenizer used in pair with the embedding model, and it should be compatible with the specified embedding model. The `splitting` field is optional and defines how the documents should be chunked in the embedding process. To check configurable options for specific providers, visit [embedding_model_configuration.json](https://github.com/feld-m/rag_blueprint/blob/main/src/common/bootstrap/configuration/pipeline/embedding/embedding_model/embedding_model_configuration.py).

**_Note_**: The same embedding model is used for embedding and retrieval processes, therefore it is defined in the `embedding` configuration only.

In the above case, embedding/retrieval and evaluation processes use the same embedding model, which might be suboptimal. To change it, simply adjust the entry of one of these:

```json
{
    "pipeline": {
        "augmentation": {
            "embedding_model": {
                "provider": "hugging_face",
                "name": "BAAI/bge-small-en-v1.5",
                "tokenizer_name": "BAAI/bge-small-en-v1.5",
                "splitting": {
                    "name": "basic",
                    "chunk_overlap_in_tokens": 50,
                    "chunk_size_in_tokens": 384
                }
            }
        }
    },
    {
        "evaluation": {
            "judge_embedding_model": {
                "provider": "openai",                       // different provider
                "name": "text-embedding-3-small",           // different embedding model
                "tokenizer_name": "text-embedding-3-small", // different tokenizer
                "batch_size": 64                            // different parameters
            }
        }
    }
}
```

## Vector Store Configuration

Currently, the following vector stores are supported:

```py
class VectorStoreName(str, Enum):
    QDRANT = "qdrant"
    CHROMA = "chroma"
```

To configure the vector store, update the following entry:

```json
{
    "pipeline": {
        "embedding": {
            "vector_store": {
                "name": "qdrant",
                "collection_name": "collection-default",
                "host": "qdrant",
                "protocol": "http",
                "ports": {
                    "rest": 6333
                }
            }
        }
    }
}
```

The `name` field indicates one of the vector stores from `VectorStoreName`, and the `collection_name` defines the vector store collection for embedded documents. The next fields define the connection to the vector store. Corresponding secrets must be added to the environment's secrets file. To check configurable options for specific datasources, visit [vector_store_configuration.json](https://github.com/feld-m/rag_blueprint/blob/main/src/common/bootstrap/configuration/pipeline/embedding/vector_store/vector_store_configuration.py).

**_Note_**: If `collection_name` already exists in the vector store, the embedding process will be skipped. To run it, delete the collection or use a different name.

## Langfuse and Chainlit Configuration

Configuration contains the entries related to Langfuse and Chainlit:

```json
{
    "pipeline": {
        "augmentation": {
            "langfuse": {
                "host": "langfuse",
                "protocol": "http",
                "port": 3000,
                "database": {
                    "host": "langfuse-db",
                    "port": 5432,
                    "db": "langfuse"
                }
            },
            "chainlit": {
                "port": 8000
            }
        }
    }
}
```

Field `chailit.port` defines on which port chat UI should be run. Fields in `langfuse` define connection details to Langfuse server and `langfuse.database` details of its database. Corresponding secrets for Langfuse have to be added to environment's secrets file. For more details check [langfuse_configuration.json](https://github.com/feld-m/rag_blueprint/blob/main/src/common/bootstrap/configuration/pipeline/augmentation/langfuse/langfuse_configuration.py)

## Upcoming Docs

Docs about configurable syntheziers, retrievers, postprocessors and others are in progress..
