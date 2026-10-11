# Lenny Growth Assistant

A transcript-grounded AI assistant for exploring ideas from Lenny's Podcast. It combines semantic retrieval, conversation history, and an LLM to answer questions with source references. It also includes a dedicated Ship 30 for 30 essay-writing skill.

## Features

- **Transcript RAG:** Retrieves relevant excerpts from the available podcast transcript corpus.
- **Source references:** Returns episode titles, transcript excerpts, and source URLs alongside assistant responses.
- **Evidence-aware responses:** Avoids generating a transcript-based answer when retrieval finds no relevant evidence.
- **Persistent conversations:** Stores sessions and messages in PostgreSQL.
- **Vector search:** Uses pgvector embeddings for semantic retrieval.
- **Provider selection:** Switches between local Ollama and cloud Claude.
- **Essay skill:** Applies a dedicated writing workflow to explicitly requested Ship 30 for 30 essays.
- **Chat interface:** Provides conversation history, provider selection, and a source/artifact viewer.

## Architecture

```text
React frontend
     |
     | HTTP / JSON
     v
FastAPI backend
     |
     +--> Session and message services
     |
     +--> Retrieval service
     |        |
     |        v
     |    PostgreSQL + pgvector
     |
     +--> Prompt and essay-skill services
     |
     +--> LLM service
              |
              +--> Local Ollama
              |
              +--> Claude Agent SDK
```

## Prerequisites

- Python
- Node.js and npm
- PostgreSQL with the pgvector extension
- Ollama for local model inference
- A Claude API key if using the cloud provider

Docker is not required for the manual local setup below.

## Configuration

Create a local environment file:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and configure the database connection, provider, Ollama model, embedding model, and frontend origin.

Important settings:

| Setting | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `LLM_PROVIDER_TOGGLE` | Default provider: `local` or `cloud` |
| `OLLAMA_BASE_URL` | Ollama API base URL |
| `OLLAMA_MODEL` | Installed Ollama model name |
| `ANTHROPIC_API_KEY` | Cloud-provider credential; keep it private |
| `EMBEDDING_MODEL` | Sentence-transformers embedding model |
| `RETRIEVAL_TOP_K` | Maximum number of candidate transcript chunks |
| `FRONTEND_ORIGIN` | Frontend origin permitted by the backend |

Never commit `.env` or API credentials. `.env.example` should contain placeholders only.

## Local setup

### 1. Install Python dependencies

From the repository root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configure PostgreSQL

Install PostgreSQL and the pgvector extension. Ensure the PostgreSQL service is running and that the extension is available to the database server.

Create the application role and database using a PostgreSQL administrator account. Replace the example password with a strong local password:

```sql
CREATE USER lenny_app WITH PASSWORD 'YOUR_PASSWORD';
CREATE DATABASE lenny_assistant OWNER lenny_app;
```

Connect to the `lenny_assistant` database and enable pgvector:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Set `DATABASE_URL` in `.env` to match the role, password, host, port, and database:

```text
DATABASE_URL=postgresql+asyncpg://lenny_app:YOUR_PASSWORD@localhost:5432/lenny_assistant
```

Create the application tables from the repository root:

```powershell
python -m backend.init_db
```

The initialization script creates the tables defined by the application models. It does not create the PostgreSQL role or database, or install pgvector; those steps must be completed first.

### 3. Prepare Ollama

Install Ollama, start its service, and pull the model configured in `.env`.

For example:

```powershell
ollama pull llama3.2:1b
ollama list
```

The configured model must exist locally. The local provider sends generation requests to Ollama.

### 4. Download and ingest transcript data

The application expects transcript files from the [Lenny's Podcast transcript repository](https://github.com/ChatPRD/lennys-podcast-transcripts) under `data/raw/lennys-podcast-transcripts/episodes`. Download the repository into that location:

```powershell
New-Item -ItemType Directory -Force .\data\raw | Out-Null
git clone https://github.com/ChatPRD/lennys-podcast-transcripts.git .\data\raw\lennys-podcast-transcripts
```

Run ingestion from the project root:

```powershell
python -m backend.ingest_transcripts
```

The script finds files named `transcript.md`, parses their YAML metadata, splits transcript text into 1,200-character chunks with 200-character overlap, generates embeddings using the configured sentence-transformers model, and stores the chunks in PostgreSQL with pgvector.

The embedding model is downloaded when first needed, so initial ingestion may take time and require an internet connection. The script reports ingested, skipped, and failed episodes at the end. Review any failed episodes in the output.

The raw transcript corpus is not included in this repository. Download it before ingestion. Do not commit raw transcripts or generated embedding caches unless their distribution rights have been verified.

### 5. Start the backend

From the repository root, activate the virtual environment and run:

```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Check the health endpoint:

```text
http://127.0.0.1:8000/health
```

Interactive API documentation, when enabled, is available at:

```text
http://127.0.0.1:8000/docs
```

### 6. Start the frontend

In a second PowerShell terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by the frontend development server.

The frontend reads its backend URL from `VITE_API_BASE_URL`. The repository includes `frontend/.env.example` with the local default:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

If needed, copy the example to `frontend/.env` and adjust the URL for your environment. Restart the Vite development server after changing environment variables.

## Provider behavior

### Local — Ollama

Uses the locally installed model and Ollama API. This is the intended local demonstration path and does not require an Anthropic API key.

### Cloud — Claude

Uses the Claude Agent SDK and requires a valid `ANTHROPIC_API_KEY`. Keep the key in the backend environment; never expose it in frontend code.

If cloud generation fails, the current LLM service attempts to fall back to local Ollama. Therefore, Ollama must be running for that fallback to work.

The provider selector is a runtime choice; the configured default is controlled by `LLM_PROVIDER_TOGGLE`.

## Essay skill

To activate the dedicated essay workflow, ask explicitly for a Ship 30 for 30 essay, for example:

> Write a Ship 30 for 30 essay about product-led growth.

The skill provides the writing workflow. Factual claims about podcast discussions must still be supported by retrieved transcript evidence and cited in the answer.

## Testing

Run the existing test suite from the repository root:

```powershell
pytest
```

Some tests may require a configured database or other local services. Review the test configuration before running integration tests in a new environment.

## Project structure

```text
backend/
  app/
    api/
    core/
    models/
    services/
    skills/
      ship_30_for_30/
frontend/
data/
docs/
tests/
.env.example
requirements.txt
README.md
```

## Documentation

- [Product Requirements Document](docs/PRD.md)
- [Design Document](docs/design.md)
- [Architecture Document](docs/architecture.md)

These documents describe the product goals, interface, and implementation architecture.

## Limitations

- Answer quality depends on the coverage and quality of the ingested transcripts and retrieval results.
- Local model performance depends on available hardware and the selected Ollama model.
- Cloud use requires a valid API credential and may incur provider charges.
- Public deployment requires a reachable database with pgvector, configured credentials, and appropriate network settings.
- Transcript availability and reuse are subject to the source's terms and applicable rights.

## Security notes

- Do not commit `.env`, credentials, database dumps, or private logs.
- Treat retrieved transcript content as untrusted input.
- Keep cloud API keys on the backend.
- Any generated HTML displayed in the Artifact Viewer must be sanitized or isolated before rendering.

## License

Add the license required for your own code and verify the terms governing any third-party transcripts or assets before redistributing them.
