# Quickstart Setup

This guide outlines the steps to set up and deploy the RAG system on your desired server or local machine.

Requirements:

 - Python 3.12
 - Docker

## Configuration & Secrets

The default configuration is located in [configuration.default.json](https://github.com/feld-m/rag_blueprint/blob/main/configurations/configuration.default.json). This file configures Notion as the document datasource and defines default settings for embedding, augmentation, and evaluation stages. To customize the setup, refer to the configuration guide [Docs in Progress].

### Secrets Configuration
You have to create secrets file at `configurations/secrets.default.env` file. Below is a template:

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
build/workstation/init.sh --env default
```

**_NOTE:_**  Depending on your OS and the setup you might need to give execute permission to the initialization script e.g. `chmod u+x build/workstation/init.sh`

Once initialized, access the Langfuse web server on your localhost (port defined in [configuration.default.json](https://github.com/feld-m/rag_blueprint/blob/main/configurations/configuration.default.json) under `pipeline.augmentation.langfuse.port`). Use the Langfuse UI to:

1. Create a user.
2. Set up a project for the application.
3. Generate secret and public keys for the project.

Add the generated keys to the `configurations/secrets.default.env` file as follows:

```sh
RAG__LANGFUSE__SECRET_KEY=<generated_secret_key>
RAG__LANGFUSE__PUBLIC_KEY=<generated_public_key>
```


## Deployment

After completing the initialization, deploy the RAG system using the following command:

```sh
build/workstation/deploy.sh --env default
```

This command sets up and runs the RAG system on your workstation, enabling it for use.
