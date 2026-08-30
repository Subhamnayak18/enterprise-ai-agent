# Enterprise AI Knowledge & Workflow Agent

> **Agentic AI system for supply-chain and procurement intelligence using RAG, natural-language SQL, LangGraph, deterministic risk scoring, and policy-grounded workflows.**

A production-oriented AI engineering project that combines **enterprise knowledge retrieval, operational analytics, supplier risk assessment, and agentic workflow orchestration** in a single application.

The system can answer questions that require both **structured operational data** and **unstructured enterprise policies**, while exposing the evidence, tools, and sources used to generate each response.

---

## What This Project Does

Procurement teams often need to answer questions that cannot be solved using only a database or only a chatbot.

For example:

> **"Which suppliers are violating our delivery SLA, and what action should procurement take according to policy?"**

Answering this requires two different forms of reasoning:

1. Query operational supplier-performance data.
2. Retrieve the relevant SLA and escalation policies.
3. Combine both evidence sources.
4. Recommend the appropriate workflow while preserving human approval for high-impact decisions.

This project implements that workflow using a **LangGraph-based AI agent**.

---

## System Architecture

```text
                         ┌─────────────────────┐
                         │        User         │
                         └──────────┬──────────┘
                                    │
                              Streamlit UI
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       FastAPI       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  LangGraph Router   │
                         └──────────┬──────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
      ┌─────────────┐        ┌─────────────┐       ┌──────────────┐
      │     RAG     │        │  SQL Agent  │       │ Supplier Risk│
      │   Chroma    │        │ PostgreSQL  │       │ Deterministic│
      └──────┬──────┘        └──────┬──────┘       └──────┬───────┘
             │                      │                      │
             └──────────────────────┼──────────────────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Escalation Workflow │
                         │ Evidence + Sources  │
                         └─────────────────────┘
```

The router determines whether a query requires:

- **RAG** — enterprise policy/SOP retrieval
- **SQL** — operational analytics
- **Hybrid reasoning** — SQL + policy retrieval
- **Supplier Risk** — deterministic risk assessment
- **Escalation Report** — operational data + risk + policy evidence

See [`docs/architecture.md`](docs/architecture.md) for the detailed design.

---

## Key Capabilities

### Enterprise RAG

Indexes synthetic procurement, supplier SLA, quality, escalation, and inventory policies.

Retrieved evidence includes metadata such as:

- document name
- policy version
- effective date
- source file

Retrieved documents are treated as **untrusted context** and sanitized before use.

### Natural-Language SQL

Converts business questions into operational SQL queries.

The SQL execution layer includes:

- SELECT-only validation
- approved-table restrictions
- row limits
- query timeouts
- SQL parsing with SQLGlot
- read-only production design

Example:

```text
Which five suppliers had the lowest on-time delivery rate?
```

### Hybrid SQL + RAG Reasoning

Some questions require both operational and policy evidence.

Example:

```text
Which suppliers violate our delivery SLA and what action
should procurement take according to policy?
```

The agent retrieves supplier-performance data and relevant policy evidence before producing the response.

### Deterministic Supplier Risk Engine

Supplier risk is calculated using explicit business rules rather than allowing an LLM to invent risk scores.

Example:

```text
Why is SUP001 considered high risk?
```

Risk explanations can include factors such as:

- delivery performance
- defect rate
- fill rate
- quality incidents

This keeps risk assessment **reproducible and explainable**.

### Supplier Escalation Workflow

The system combines:

```text
Supplier Operational Data
        +
Risk Assessment
        +
Enterprise Policy Retrieval
        ↓
Grounded Escalation Report
```

High-impact actions such as supplier suspension remain subject to **human approval**.

---

## Evaluation

The repository contains a curated evaluation suite covering routing, retrieval, and SQL safety.

| Evaluation | Result |
|---|---:|
| Agent routing | **50/50 (100%)** |
| Policy retrieval source hit@3 | **7/7 (100%)** |
| Unsafe SQL rejection | **6/6 (100%)** |
| Pytest suite | **21 tests passing** |

Run the evaluation:

```bash
python evaluation/run_evaluation.py
```

Run the tests:

```bash
pytest -q
```

> These results are internal engineering checks on a synthetic environment, not external production benchmarks. No synthetic-data business impact is claimed.

---

## Example Queries

### Policy / RAG

```text
What action should be taken when a supplier repeatedly violates its delivery SLA?
```

### Operational Analytics

```text
Which five suppliers had the lowest on-time delivery rate?
```

### Hybrid Reasoning

```text
Which suppliers violate our delivery SLA and what action should procurement take according to policy?
```

### Supplier Risk

```text
Assess risk score for SUP001.
```

### Workflow Generation

```text
Generate an escalation report for SUP001.
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python |
| Agent Orchestration | LangGraph |
| LLM Integration | LangChain / OpenAI-compatible provider |
| RAG | Chroma |
| Database | PostgreSQL / SQLite development fallback |
| ORM | SQLAlchemy |
| SQL Safety | SQLGlot |
| Backend | FastAPI |
| Frontend | Streamlit |
| Validation | Pydantic |
| Testing | Pytest |
| Containers | Docker / Docker Compose |
| CI | GitHub Actions |

---

## Repository Structure

```text
enterprise-ai-agent/
│
├── app/
│   ├── agents/          # LangGraph routing and orchestration
│   ├── api/             # FastAPI routes and schemas
│   ├── core/            # configuration, logging and security
│   ├── database/        # SQLAlchemy models and repositories
│   ├── llm/             # model-provider abstraction
│   ├── prompts/         # system/tool prompts
│   ├── rag/             # loading, chunking, embeddings, retrieval
│   └── tools/           # SQL, RAG, risk and report tools
│
├── frontend/
│   └── app.py           # Streamlit application
│
├── data/
│   ├── documents/       # synthetic enterprise policies
│   └── raw/             # synthetic operational datasets
│
├── evaluation/          # evaluation questions and results
├── scripts/             # generation, seeding and indexing
├── tests/               # automated tests
├── docs/                # architecture and engineering docs
│
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

# Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/Subhamnayak18/enterprise-ai-agent.git
cd enterprise-ai-agent
```

## 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements-dev.txt
```

Create the environment configuration:

```powershell
Copy-Item .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

---

## 3. Choose Database Mode

### PostgreSQL

The production-oriented configuration uses PostgreSQL.

```bash
docker compose up -d db
```

Configure `DATABASE_URL` in `.env`.

### Lightweight Local Development

The application can also use SQLite for development without Docker:

```env
DATABASE_URL=sqlite:///./enterprise_ai.db
```

This is useful for quickly running and demonstrating the project locally.

---

## 4. Generate Synthetic Data

```bash
python scripts/generate_data.py
python scripts/seed_database.py
```

The generated dataset contains synthetic:

- suppliers
- products
- warehouses
- purchase orders
- supplier-performance records
- quality incidents

**No proprietary company data is included.**

---

## 5. Index Enterprise Policies

```bash
python scripts/index_documents.py
```

The RAG corpus includes synthetic policies covering areas such as:

- supplier delivery SLA
- supplier performance management
- vendor escalation
- quality incidents
- procurement procedures
- inventory replenishment
- purchase-order approval

---

## 6. Run the Backend

```bash
uvicorn app.main:app --reload
```

Swagger API documentation:

```text
http://localhost:8000/docs
```

---

## 7. Run the Frontend

Open another terminal:

```bash
streamlit run frontend/app.py
```

The application will normally be available at:

```text
http://localhost:8501
```

---

# LLM and Offline Development Modes

The architecture supports an OpenAI-compatible LLM provider for:

- synthesized RAG responses
- model-generated SQL
- higher-quality semantic embeddings

Configure:

```env
OPENAI_API_KEY=your_key
```

The repository also contains deterministic/offline development fallbacks so the core architecture can be demonstrated without requiring a paid API.

Offline mode supports:

- deterministic query routing
- local development embeddings
- predefined SQL handling for supported analytical questions
- deterministic supplier-risk assessment
- policy evidence retrieval

The local hashed embedding implementation is intentionally a **development fallback** and should not be presented as equivalent to production semantic embeddings.

---

# API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Service health |
| `POST` | `/chat` | Agent interaction |
| `POST` | `/documents/upload` | Upload policy document |
| `POST` | `/documents/index` | Re-index documents |
| `GET` | `/sources` | Available knowledge sources |
| `GET` | `/conversations/{conversation_id}` | Conversation history |

Example:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Assess risk score for SUP001"}'
```

---

# Security & Responsible AI

The project deliberately separates probabilistic AI reasoning from deterministic business controls.

Key safeguards include:

- SQL validation before execution
- SELECT-only SQL
- approved operational tables
- configurable row limits
- prompt-injection sanitization
- environment-based secret management
- source attribution for policy evidence
- deterministic supplier-risk scoring
- human approval for high-impact supplier actions

In production, the SQL agent should operate using **read-only database credentials**.

See [`docs/responsible_ai.md`](docs/responsible_ai.md).

---

# Testing

Run:

```bash
pytest -q
```

Static checks:

```bash
ruff check app scripts tests evaluation
```

Tests focus particularly on deterministic and safety-critical behavior:

- SQL validation
- agent routing
- document chunking
- metadata preservation
- prompt-injection sanitization
- supplier-risk calculations

---

# Docker

Run the complete stack:

```bash
docker compose up --build
```

Services:

```text
API       → http://localhost:8000
Streamlit → http://localhost:8501
```

Initialize data from the API container when required:

```bash
docker compose exec api python scripts/generate_data.py
docker compose exec api python scripts/seed_database.py
docker compose exec api python scripts/index_documents.py
```

---

# Design Decisions

### Why LangGraph?

The workflow contains multiple specialized tools and requires explicit routing between RAG, SQL, risk assessment, and reporting. A graph-based architecture makes these transitions visible and testable.

### Why deterministic risk scoring?

Risk scores can influence business decisions. Keeping the calculation outside the LLM makes the result reproducible, testable, and explainable.

### Why separate SQL and RAG?

Structured operational data and enterprise documents require different retrieval strategies. Separating them also makes hybrid questions explicit rather than hiding the reasoning inside one large prompt.

### Why human approval?

The system can recommend escalations but does not autonomously execute high-impact actions such as supplier suspension.

---

# Limitations

- All operational data and enterprise policies are synthetic.
- LLM-generated SQL may be incorrect even when syntactically safe.
- Offline hashed embeddings are intended only for development.
- Conversation history is currently stored in memory.
- Document indexing is synchronous and designed for a small demonstration corpus.
- The current project is a portfolio system, not a deployed enterprise application.

---

# Future Improvements

Potential production extensions include:

- authentication and RBAC
- durable conversation persistence
- hybrid retrieval and reranking
- pgvector or managed vector search
- asynchronous document ingestion
- bounded SQL-repair loops
- tracing and observability
- role-aware policy access
- managed cloud deployment
- evaluation monitoring

---

# Documentation

Additional documentation is available in:

- [`docs/architecture.md`](docs/architecture.md) — system architecture
- [`docs/deployment.md`](docs/deployment.md) — deployment approach
- [`docs/responsible_ai.md`](docs/responsible_ai.md) — safety and governance
- [`docs/interview_guide.md`](docs/interview_guide.md) — architecture rationale and interview preparation
- [`docs/resume_bullets.md`](docs/resume_bullets.md) — measured project bullets

---

## Project Status

**Functional portfolio implementation**

Verified locally with:

- FastAPI backend
- Streamlit frontend
- SQL analytics
- deterministic supplier-risk assessment
- RAG policy retrieval
- hybrid SQL + policy workflow
- escalation-report generation
- automated tests

The system is designed as a demonstration of **enterprise AI engineering patterns**, with emphasis on grounded responses, explainable business logic, safety controls, and modular architecture.
