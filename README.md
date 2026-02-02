## Gestalt Question Generator

**About**  
LangGraph server responsible for generating Gestalt-style questions and related code.

## Install

From the repository root:
```bash
cd langgraph_server
poetry install
```

## Environment Setup

Create a .env file and set the following variables:

```bash
# LangSmith
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=ProjectName

# OpenAI
OPENAI_API_KEY=
EMBEDDINGS=text-embedding-3-large

# Vector Store (AstraDB)
ASTRA_DB_API_ENDPOINT=
ASTRA_DB_APPLICATION_TOKEN=
```

## Running

From the `langgraph_server` directory:

```bash
langgraph dev
```