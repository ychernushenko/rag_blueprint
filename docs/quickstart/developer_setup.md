# Local Developement Setup

This guide outlines the steps required to set up the RAG system on your local machine for development purposes.

Requirements:

- Python 3.12
- Docker

## Configuration & Secrets

The local configuration is located in [configuration.local.json](https://github.com/feld-m/rag_blueprint/blob/main/configurations/configuration.local.json). This file configures Notion as the document datasource and defines local settings for embedding, augmentation, and evaluation stages. To customize the setup, refer to the configuration guide [Docs in Progress].

### Secrets Configuration
You have to create secrets file at `configurations/secrets.local.env` file. Below is a template:

```sh
# Datasources
RAG__DATASOURCES__NOTION__API_TOKEN=...

# LLMs
RAG__LLMS__OPENAI__API_KEY=...

# Langfuse
RAG__LANGFUSE__DATABASE__USER=user
RAG__LANGFUSE__DATABASE__PASSWORD=password

RAG__LANGFUSE__SECRET_KEY=...
RAG__LANGFUSE__PUBLIC_KEY=...
```

- `RAG__DATASOURCES__NOTION__API_TOKEN`: Notion integration token to extract the documents.
- `RAG__LLMS__OPENAI__API_KEY`: Required for connecting to [OpenAI](https://openai.com/) LLM.
- **Langfuse Keys**: `RAG__LANGFUSE__SECRET_KEY` and `RAG__LANGFUSE__PUBLIC_KEY` are generated during initialization and will need to be updated later.

## Initialization

### Python Environment

1. Install uv on you OS following this [installation](https://docs.astral.sh/uv/getting-started/installation/) guide.

2. In the root of the project, create a virtual environment and activate it:

```sh
uv venv
source .venv/bin/activate
```

3. Install the required dependencies:

```sh
uv sync --all-extras
```

### Services Initialization

To initialize the Langfuse and vector store services, run the initialization script:

```sh
build/workstation/init.sh --env local
```

**_NOTE:_**  Depending on your OS and the setup you might need to give execute permission to the initialization script e.g. `chmod u+x build/workstation/init.sh`

Once initialized, access the Langfuse web server on your localhost (port defined in [configuration.default.json](https://github.com/feld-m/rag_blueprint/blob/main/configurations/configuration.default.json) under `pipeline.augmentation.langfuse.port`). Use the Langfuse UI to:

1. Create a user.
2. Set up a project for the application.
3. Generate secret and public keys for the project.

Add the generated keys to the `configurations/secrets.local.env` file as follows:

```sh
RAG__LANGFUSE__SECRET_KEY=<generated_secret_key>
RAG__LANGFUSE__PUBLIC_KEY=<generated_public_key>
```

## Development

### Running RAG

For the first run, it is recommended to execute the scripts in the specified order to ensure proper initialization of resources like vector store collections.

#### Embedding Stage

Run the embedding stage script:

```sh
python src/embed.py --env local
```

**_Note_:** The embedding process may take significant time, depending on the size of your datasource.

#### Augmentation Stage

Run the augmentation stage script:

```sh
python src/chat.py --env local
```

This initializes the RAG system's query engine and the Chainlit application, leveraging the embeddings generated in the previous step.

#### Evaluation Stage

Run the evaluation stage script:

```sh
python src/evaluation.py --env local
```

**_Important_:** For evaluation to proceed, Langfuse datasets must be populated either manually or via Chainlit's human feedback feature. For additional details, refer to the [Docs in Progress].

## Git setup

The `.pre-commit-config.yaml` file configures code formatters to enforce consistency before committing changes. After cloning the repository and installing dependencies, enable pre-commit hooks:

```sh
pre-commit install
```
