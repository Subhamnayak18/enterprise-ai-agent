# Interview Guide

## 30-second explanation

I built an enterprise procurement AI agent that answers both policy and operational questions. Policy documents are retrieved through a RAG pipeline, current supplier data is queried from PostgreSQL through a guarded SQL tool, and a LangGraph workflow routes requests to RAG, SQL, a hybrid path, deterministic supplier-risk logic or an escalation-report workflow. FastAPI exposes the system, Streamlit provides a simple UI, and I added source grounding, SQL safety, prompt-injection handling, tests, Docker and CI.

## 60-second explanation

The problem I wanted to solve was that procurement decisions often require combining two different sources of evidence: unstructured policies and current operational data. I created synthetic supplier, purchase-order, performance and quality-incident data in PostgreSQL and a separate knowledge base of seven internal-style policies. For document questions, the system chunks policies, creates embeddings and retrieves relevant chunks from Chroma. For quantitative questions, an LLM generates SQL against an approved schema, but the query is validated before execution so only read-only approved-table queries are allowed. LangGraph routes requests to RAG, SQL, hybrid, supplier-risk or report workflows. The supplier-risk score itself is deterministic Python rather than an LLM-generated number. I exposed everything with FastAPI, added a small Streamlit UI, tests, evaluation, Docker and GitHub Actions.

## 2-minute explanation

The project is an Enterprise AI Knowledge and Workflow Agent for supply-chain and procurement operations. The main business problem is that a buyer might ask something like, “Which suppliers currently violate our delivery SLA, and what action should procurement take?” That question cannot be answered reliably by only searching documents or only querying a database.

I therefore separated structured and unstructured evidence. Structured data lives in PostgreSQL and includes suppliers, purchase orders, monthly supplier performance, quality incidents, products and warehouses. The data is synthetic but intentionally noisy and operationally plausible. Unstructured knowledge consists of seven synthetic internal-style policies covering delivery SLA, vendor escalation, procurement, quality incidents, inventory and PO approvals.

For policy questions, documents are parsed, chunked with overlap, enriched with metadata such as policy version and effective date, embedded, and stored in Chroma. Retrieved text is treated as untrusted data and sanitized for obvious prompt-injection instructions. For operational questions, the SQL tool provides the LLM only an approved schema, validates the generated query, blocks mutation statements, checks table allowlists, applies row limits and uses a timeout.

LangGraph orchestrates five explicit routes: RAG, SQL, hybrid, deterministic supplier risk and supplier escalation report. The risk score is normal Python with documented project thresholds so it is reproducible and auditable. The report workflow combines the latest supplier metrics, the risk result and relevant policy evidence, and always marks high-impact action as requiring human approval.

I exposed the backend through FastAPI, built a minimal Streamlit client, added Pytest, evaluation, Docker and GitHub Actions, and documented limitations and Responsible AI. On the included curated checks, routing was 50/50, policy source hit@3 was 7/7 and unsafe SQL rejection was 6/6. I treat these as internal engineering checks, not production business impact.

## Architecture walkthrough

1. User sends a message from Streamlit or directly to FastAPI.
2. FastAPI validates the request and passes the query to the LangGraph workflow.
3. Router classifies the request as `rag`, `sql`, `both`, `business`, or `report`.
4. RAG queries the policy vector store; SQL queries PostgreSQL through a safety layer; business executes deterministic risk logic; report combines the relevant tools.
5. The response includes the answer plus sources, tools used, SQL/result data where relevant, and errors if any.
6. High-impact recommendations remain advisory and require human approval.

## STAR-style story

**Situation:** Procurement questions frequently require combining current supplier metrics with internal policies, while basic chat-with-PDF demos cannot handle structured operational analysis safely.

**Task:** Build a portfolio-grade AI system that could answer policy, SQL and hybrid questions while being explainable, testable and safe enough to discuss in an engineering interview.

**Action:** Designed separate PostgreSQL and RAG layers, implemented guarded NL-to-SQL, created a deterministic supplier-risk tool, orchestrated routes with LangGraph, exposed the system through FastAPI, and added evaluation, Docker, CI and Responsible-AI controls.

**Result:** The completed synthetic MVP supports five query workflows and measured 50/50 routing checks, 7/7 retrieval source hit@3 checks and 6/6 unsafe SQL rejections. These are internal project metrics rather than real-company business outcomes.

## Likely interview questions and answers

### RAG

1. **Why RAG?** Policies change frequently and answers need evidence. RAG lets me update documents without retraining and return source metadata.
2. **Why not fine-tuning?** Fine-tuning is better for behavior or task adaptation; it is not an efficient way to keep changing factual policies current.
3. **What is an embedding?** A numerical vector representation where semantically related text should be close in vector space.
4. **Why chunk documents?** Embedding an entire long policy gives weak retrieval granularity and wastes context; chunks let the retriever return the relevant rule.
5. **Why overlap?** A rule can span a chunk boundary, so modest overlap reduces loss of context.
6. **How did you choose chunk size?** I started around 900 characters with 120 overlap because the policies contain short operational sections; the correct value should be tuned through retrieval evaluation.
7. **What is cosine similarity?** It measures the angle between vectors and is commonly used to compare embedding similarity independent of vector magnitude.
8. **Why Chroma?** It is lightweight, persistent and easy for a small portfolio corpus. For production I would consider pgvector or managed vector search.
9. **Why metadata?** It improves traceability and enables filtering by document name, department, version, effective date or source.
10. **What happens when retrieval fails?** The system should state that evidence is insufficient rather than inventing a policy.
11. **How do you evaluate RAG?** Retrieval hit/relevance, answer relevance, faithfulness, source correctness and latency.
12. **How do you reduce hallucination?** Limit the answer to retrieved evidence, require source attribution, handle insufficient context and keep deterministic logic outside the model.

### LangGraph / agents

13. **Why LangGraph?** I wanted explicit state and constrained routing instead of a free-form autonomous loop.
14. **Agent vs workflow?** An agent usually has more freedom to choose repeated actions; my system is a controlled workflow with known routes and tools.
15. **What is graph state?** The shared typed data passed between nodes, including query, route, SQL, retrieved evidence, sources, errors and final answer.
16. **What are nodes and edges?** Nodes execute logic; edges determine which node can run next.
17. **Why not call one LLM with everything?** That mixes concerns, increases hallucination risk, makes SQL access harder to control and reduces testability.
18. **How do you avoid infinite loops?** There is no open-ended tool loop: one routing node selects one terminal workflow path.
19. **How do you validate tool outputs?** SQL is parsed and constrained, risk scores are deterministic, and retrieved policy evidence is carried separately with source metadata.

### SQL

20. **How is SQL generated?** The model receives a restricted schema and instruction to generate one read-only query.
21. **How do you protect the database?** SELECT/CTE-only validation, blocked mutations, approved-table checks, row limits, timeouts and read-only credentials in production.
22. **Why SQLGlot?** Parsing SQL is safer than relying only on regex because it lets me inspect query structure and referenced tables.
23. **What if the model generates invalid SQL?** It is rejected before execution or fails safely at the database layer. A future version could allow one bounded repair attempt.
24. **Why not let the LLM connect directly?** A mediated tool enforces least privilege and gives me an auditable validation boundary.
25. **What about SQL injection?** User text is not concatenated directly into execution SQL; the model output itself is parsed and restricted before execution.

### Supplier risk / business logic

26. **Why deterministic risk scoring?** A business risk score needs reproducibility, auditability and unit tests. The LLM can explain the result but should not invent the number.
27. **Are your thresholds industry standards?** No. They are documented project assumptions created for the synthetic demo.
28. **What inputs are used?** On-time delivery, fill rate, defect rate, average delay and severe quality incidents.
29. **How would you improve the risk model?** Calibrate thresholds on historical outcomes, weight by category criticality, add trends and validate fairness/stability.

### Backend and deployment

30. **Why FastAPI?** Typed validation, good performance, automatic OpenAPI docs and straightforward container deployment.
31. **Why Streamlit?** UI was not the engineering focus; Streamlit gives a usable client quickly while the backend remains cleanly separated.
32. **Docker image vs container?** An image is the packaged immutable template; a container is a running instance of that image.
33. **What does CI/CD do here?** Push/PR triggers dependency installation, lint/tests and Docker image build. Deployment automation can be layered on later.
34. **What changes in production?** RBAC, private networking, managed secrets, durable document/object storage, managed vector search, observability, database replicas/backups and stronger governance.
35. **How would you deploy cheaply on AWS?** Containerized API on App Runner or ECS, RDS PostgreSQL, Secrets Manager/Parameter Store, plus budget alerts and teardown when not in use.

### Responsible AI / evaluation

36. **How do you handle prompt injection?** Retrieved text is considered data, not instructions; known instruction-like patterns are sanitized and system-level constraints remain separate.
37. **Why human approval?** Supplier suspension or sourcing holds are high-impact procurement actions; the model should support a decision, not autonomously execute it.
38. **What metrics did you actually measure?** 50/50 routing checks, 7/7 policy source hit@3 checks and 6/6 unsafe SQL rejections on the included curated synthetic evaluation.
39. **Why are these not production metrics?** The corpus and data are synthetic and the tests are curated, so they measure engineering behavior only.
40. **Biggest limitation?** General NL-to-SQL and RAG quality depend on the configured LLM/embedding model and would need a much larger real evaluation set before production use.
