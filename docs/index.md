# RAG Blueprint Documentation

## Overview
The RAG blueprint project is a Retrieval-Augmented Generation system that integrates with several datasources to provide intelligent document search and analysis. The system combines the power of different large language models with knowledge bases to deliver accurate, context-aware responses through a chat interface.

## Data Sources

| Data Source | Description |
|-------------|-------------|
| Confluence | Enterprise wiki and knowledge base integration |
| Notion | Workspace and document management integration |
| PDF | PDF document processing and text extraction |

Check how to configure datasources [here](how_to/how_to_configure/#datasource-configuration).

## Embeddding Models

| Models | Provider | Description |
|-------|----------|-------------|
|   *   | [HuggingFace](https://huggingface.co/) | Open-sourced, run locally embedding models provided by HuggingFace |
|   *   | [OpenAI](https://openai.com/) | Embedding models provided by OpenAI |
|   *   | [VoyageAI](https://www.voyageai.com/) | Embedding models provided by VoyageAI |

Check how to configure embedding model [here](how_to/how_to_configure/#embedding-model-configuration).

## Language Models

| Model | Provider | Description |
|-------|----------|-------------|
|   *   |  [OpenAI](https://openai.com/)  | Language models provided by OpenAI |
|   *   |  OpenAILike  | Self-hosted language models shared through OpenAI like API |


Check how to configure LLM [here](how_to/how_to_configure/#llm-configuration).

## Vector Databases

| Vector Store | Description |
|--------------|-------------|
| Qdrant | High-performance vector similarity search engine |
| Chroma |  Lightweight embedded vector database |


Check how to configure vector store [here](how_to/how_to_configure/#vector-store-configuration).

## Key Features

- **Multiple Knowledge Base Integration**: Seamless extraction from several Data Sources(Confluence, Notion, PDF)
- **Wide Models Support**: Availability of numerous embedding and language models
- **Vector Search**: Efficient similarity search using vector stores
- **Interactive Chat**: User-friendly interface for querying knowledge on [Chainlit](https://chainlit.io/)
- **Performance Monitoring**: Query and response tracking with [Langfuse](https://langfuse.com/)
- **Setup flexibility**: Easy and flexible setup process of the pipeline

### Quick Start
- [QuickStart Setup](quickstart/quickstart_setup.md)
- [Dveloper Setup](quickstart/developer_setup.md)
