# Enterprise AI Knowledge & Workflow Agent

A production-oriented portfolio project for **supply-chain and procurement operations**. It combines enterprise policy retrieval, operational SQL analytics, deterministic supplier-risk logic and constrained agent orchestration behind a FastAPI API.

## Business problem

Procurement teams often need to combine two evidence types: internal policies/SOPs and current operational data. A plain chatbot cannot reliably answer questions such as *"Which suppliers violate our SLA, and what action does policy require?"* This project routes each query to the right evidence source and exposes the tools and sources used.

## Key capabilities

- RAG over synthetic procurement, SLA, quality and inventory policies with source metadata
- PostgreSQL operational model for suppliers, POs, performance, incidents, products and warehouses
- Natural-language-to-SQL with SELECT-only validation, approved-table checks, row limits and timeouts
- LangGraph routes: RAG / SQL / hybrid / supplier-risk / escalation report
- Deterministic supplier risk score with explainable reasons
- Grounded supplier escalation report with human-approval flag
- FastAPI endpoints and minimal Streamlit client
- Prompt-injection sanitization for retrieved documents
- Pytest suite, evaluation set, Docker, Compose and GitHub Actions

## Architecture

```text
User
  -> Streamlit
  -> FastAPI
  -> LangGraph router
      -> RAG -> Chroma -> policy documents
      -> SQL -> PostgreSQL
      -> Supplier Risk -> deterministic Python
      -> Report -> SQL + Risk + RAG
  -> answer + sources + tools used + SQL evidence
```

See [docs/architecture.md](docs/architecture.md).

## Example queries

- `What action is required when a supplier repeatedly violates delivery SLA?`
- `Which five suppliers had the lowest latest on-time delivery rate?`
- `Which suppliers currently violate our SLA and what action should procurement take?`
- `Assess risk score for SUP001.`
- `Generate escalation report for SUP001.`

## Tech stack

Python, FastAPI, PostgreSQL, SQLAlchemy, OpenAI-compatible LangChain client, Chroma, LangGraph, SQLGlot, Streamlit, Pytest, Docker, GitHub Actions.

## Repository structure

```text
app/
  agents/          # routing + LangGraph orchestration
  api/             # FastAPI routes and schemas
  core/            # settings, logging, security
  database/        # SQLAlchemy schema/repository
  llm/             # model provider boundary
  prompts/         # concise prompts
  rag/             # loading, chunking, embeddings, retrieval
  tools/           # SQL, RAG, risk and report tools
frontend/app.py
data/documents/    # synthetic enterprise policies
data/raw/          # generated synthetic operational CSVs
scripts/           # data generation, DB seed, document indexing
evaluation/        # labeled routing/evaluation set
tests/
docs/
```

## Local setup

### 1. Environment

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # Windows PowerShell: Copy-Item .env.example .env
```

Add `OPENAI_API_KEY` to `.env` for LLM-generated SQL and synthesized RAG answers. The retrieval layer has an offline embedding fallback for development, but production-quality semantic retrieval should use the configured embedding API.

### 2. Start PostgreSQL

```bash
docker compose up -d db
```

### 3. Generate and seed data

```bash
python scripts/generate_data.py
python scripts/seed_database.py
```

The repository data is **synthetic** and is not copied from a real company.

### 4. Index policy documents

```bash
python scripts/index_documents.py
```

### 5. Run API

```bash
uvicorn app.main:app --reload
```

API docs: `http://localhost:8000/docs`

### 6. Run UI

```bash
streamlit run frontend/app.py
```

## API

- `GET /health`
- `POST /chat`
- `POST /documents/upload`
- `POST /documents/index`
- `GET /sources`
- `GET /conversations/{conversation_id}`

Example:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Assess risk score for SUP001"}'
```

## Evaluation

The evaluation set contains representative RAG, SQL, hybrid and business-tool questions. Run:

```bash
python evaluation/run_evaluation.py
```

Current included evaluation results:

- deterministic routing accuracy: **100% on 50 curated questions**
- policy retrieval source hit@3: **100% on 7 canonical checks**
- unsafe SQL rejection: **100% on 6 safety checks**

These are internal project checks on a synthetic environment, not external benchmarks. Only measured results from `evaluation/results.json` should be used in a resume. Do not claim synthetic-data business impact.

## Security and design decisions

- SQL is validated before execution and restricted to approved operational tables.
- Agent SQL credentials should be read-only in production.
- Retrieved document content is treated as untrusted data.
- Secrets are environment variables and `.env` is excluded from Git.
- Supplier suspension and similar high-impact actions require human approval.

See [docs/responsible_ai.md](docs/responsible_ai.md).

## Testing

```bash
pytest -q
ruff check app scripts tests evaluation
```

Tests focus on deterministic safety-critical behavior: SQL validation, routing, chunking, metadata, prompt-injection sanitization and supplier risk scoring.

## Docker

```bash
docker compose up --build
```

API: `http://localhost:8000`
UI: `http://localhost:8501`

Then generate/seed/index from the API container if needed:

```bash
docker compose exec api python scripts/generate_data.py
docker compose exec api python scripts/seed_database.py
docker compose exec api python scripts/index_documents.py
```

## Deployment

A low-cost AWS path is documented in [docs/deployment.md](docs/deployment.md). For real enterprise use, add authentication/RBAC, private networking, durable document storage, managed vector search, observability and stricter governance.

## Limitations

- Synthetic data and policies do not establish real business impact.
- LLM SQL generation can be incorrect even when syntactically safe.
- Offline hashed embeddings are only a development fallback, not semantic production retrieval.
- In-memory conversation history is not durable.
- Upload indexing is synchronous and intended for a small demo corpus.

## Future improvements

RBAC, conversation persistence, retrieval reranking, pgvector/managed vector search, asynchronous ingestion, SQL repair with bounded retries, tracing/observability and role-aware policy access.

## Interview preparation

See [docs/interview_guide.md](docs/interview_guide.md) for the project story, architecture rationale and likely interview questions.
