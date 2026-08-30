# Architecture

```text
User -> Streamlit -> FastAPI -> LangGraph Router
                            |-> RAG Tool -> Chroma -> Policy chunks
                            |-> SQL Tool -> PostgreSQL
                            |-> Supplier Risk Tool -> Deterministic rules
                            |-> Report Tool -> SQL + Risk + RAG
                                      -> Grounded response + sources + tools used
```

## Key boundaries

- PostgreSQL is the source of truth for structured operational data.
- Chroma stores policy chunks and embeddings, not business transactions.
- LangGraph orchestrates tool selection; it does not own deterministic business rules.
- The SQL tool has no mutation capability and should use read-only DB credentials in production.
- FastAPI is the boundary used by the UI and future clients.

## RAG choices

Documents are normalized and chunked to roughly 900 characters with 120-character overlap. This keeps related policy rules together while avoiding very large context blocks. Metadata includes document name, type, department, version, effective date and source. Chroma uses cosine distance. OpenAI embeddings are used when an API key is configured; a deterministic hashed-vector fallback exists strictly for local development/tests and is not presented as semantic production quality.

## Agent state

The graph tracks the user query, conversation ID, route, retrieved evidence, generated SQL, SQL results, business-tool result, sources, errors, final answer and tools used. Routes are constrained to `rag`, `sql`, `both`, `business`, and `report`; there is no open-ended autonomous loop.
