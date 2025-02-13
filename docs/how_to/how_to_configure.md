# How To Configure RAG System

This guides presents how to customize the RAG System pipeline through the configuration.

## Environments

### Definition

The code defines following possible environments:

```py
class EnvironmentName(str, Enum):
    DEFAULT = "default"
    LOCAL = "local"
    DEV = "dev"
    TEST = "test"
    PROD = "prod"
```

To use specific environment associated configuration and secrets files have to be present in  [configurations](https://github.com/feld-m/rag_blueprint/tree/main/configurations) directory. Configuration is a json file following this file naming pattern - `configuration.{environment}.json`, where `configuration.default.json` corresponds to `default` environment. Analogical pattern applies to secrets - `secrets.{environment}.env`, where `secrets.default.env` corresponds to `default` environment.

Configuration stores the setup of the pipeline and secrets keep corresponding credentials, tokens etc. needed for the services. For security purposes all the files in [configurations](https://github.com/feld-m/rag_blueprint/tree/main/configurations) are ignored from git apart from [configuration.default.json](https://github.com/feld-m/rag_blueprint/blob/main/configurations/configuration.default.json) and [configuration.local.json](https://github.com/feld-m/rag_blueprint/blob/main/configurations/configuration.local.json).

### Usage

In order to run the pipeline with specific configuration just use environment flat in the scripts e.g.:

```sh
build/workstation/init.sh --env default
python src/embed.py --env default
```

## Datasource Configuration

Currently the following datasources are available:

```py
class DatasourceName(str, Enum):
    NOTION = "notion"
    CONFLUENCE = "confluence"
    PDF = "pdf"
```

Blueprint allows the usage of single or multiple datasources, adjust corresponding configuration accordingly:

```json
{
    "pipeline": {
        "embedding": {
            "datasources": [
                {
                    "name": "notion",
                    "export_limit": 100,
                },
                {
                    "name": "pdf",
                    "export_limit": 100,
                    "base_path": "data/"
                }
            ],
        }
    }
}
```

Each entry in `datasources` corresponds to a single source that will be sequentially used for extraction of further processed documents. The `name` of each entry has to correspond to one of implemented enums. Datasources' secrets have to be added to environment's secret file. To check configurable options for specific datasources visit [datasources_configurtion.json](https://github.com/feld-m/rag_blueprint/blob/main/src/common/bootstrap/configuration/pipeline/embedding/datasources/datasources_configuration.py).

## LLM Configuration

Currently LLMs from these providers are supported:

```py
class LLMProviderNames(str, Enum):
    OPENAI = "openai"
    OPENAI_LIKE = "openai-like"
```

`OpenAI` indicates [OpenAI](https://openai.com/) provider, whereas `OPENAI_LIKE` indicates any LLM exposed through the API compatible with OpenAI's API e.g. self-hosted LLM exposed via [TabbyAPI](https://theroyallab.github.io/tabbyAPI/).

Minimal setup requires the use of LLMs in augmentation and evaluation processes. To configure this adjust the following json entries:

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
                },
            }
        },
        "evaluation": {
            "judge_llm": {
                "provider": "openai",
                "name": "gpt-4o-mini",
                "max_tokens": 1024,
                "max_retries": 3,
                "context_window": 16384
            },
        }
    }
}
```

Providers' secrets have to be added to environment's secret file. Field `provider` one of the values from `LLMProviderNames` and `name` field indicates specific model exposed by the provider. To check configurable options for specific providers visit [llm_configurtion.json](https://github.com/feld-m/rag_blueprint/blob/main/src/common/bootstrap/configuration/pipeline/augmentation/query_engine/llm_configuration.py).

In above case augmentation and evaluation processes use the same LLM, which might be suboptimal. To change it, simply adjust the entry of one of these:

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
                "max_tokens": 512,          // another parameters
            }
        }
    }
}
```

## Embedding Model Configuration

Currently embedding models from these providers are supported:

```py
class EmbeddingModelProviderNames(str, Enum):
    HUGGING_FACE = "hugging_face"
    OPENAI = "openai"
    VOYAGE = "voyage"
```

Any model exposed by these providers can be used in the setup.

Minimal setup requires the use of embedding models in different processes. To configure this adjust the following json entries:

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

Providers' secrets have to be added to environment's secret file. Field `provider` one of the values from `EmbeddingModelProviderNames` and `name` field indicates specific model exposed by the provider.
Field `tokenizer_name` indicates tokenizer used in pair with the embedding model, therefore it should be compatible one of the tokenizer compatible with specified embedding model. Field `splitting` is an optional field that defines how the documents should be chunked in an embedding process.
To check configurable options for specific providers visit [embedding_model_configurtion.json](https://github.com/feld-m/rag_blueprint/blob/main/src/common/bootstrap/configuration/pipeline/embedding/embedding_model/embedding_model_configuration.py).

**_Note_**: The same embedding model is used for embedding and retrieval process, therefore it is defined in `embedding` configuration only.

In above case embedding/retrieval and evaluation processes use the same embedding model, which might be suboptimal. To change it, simply adjust the entry of one of these:

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

Currently the following vector stores are supported:

```py
class VectorStoreName(str, Enum):
    QDRANT = "qdrant"
    CHROMA = "chroma"
```

To configure vector store update the following entry:

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

Field `name` indicates one of the vector stores from `VectorStoreName` and the `collection_name` defines vector store collection for embedded documents. The next fields define connection to the vector store. Correspodning secrets have to be added to environment's secrets file. To check configurable options for specific datasources visit [vector_store_configurtion.json](https://github.com/feld-m/rag_blueprint/blob/main/src/common/bootstrap/configuration/pipeline/embedding/vector_store/vector_store_configuration.py).

**_Note_** If `collection_name` already exists in the vector store, embedding process will be skipped. In order to run it, delete the collection or use different name.

## Langfuse and Chainlit Configuration

Configuration contains the entries related to Langufe and Chainlit:

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
        },
    }
}
```

Field `chailit.port` defines on which port chat UI should be run. Fields in `langfuse` define connection details to Langfuse server and `langfuse.database` details of its database. Corresponding secrets for Langfuse have to be added to environment's secrets file. For more details check [langfuse_configuration.json](https://github.com/feld-m/rag_blueprint/blob/main/src/common/bootstrap/configuration/pipeline/augmentation/langfuse/langfuse_configuration.py)
## Upcoming Docs

Docs about configurable syntheziers, retrievers, postprocessors and others are in progress..
