# Responsible AI

This portfolio system is decision support, not an autonomous procurement authority.

- **Hallucination:** policy answers are grounded in retrieved excerpts and should admit insufficient evidence.
- **Human review:** supplier suspension, sourcing hold and high-impact procurement decisions require authorized human approval.
- **Privacy:** the demo uses synthetic operational data. Real deployments require data classification, least-privilege access and retention controls.
- **Prompt injection:** retrieved documents are treated as untrusted data; common instruction-like injection text is stripped before generation.
- **SQL safety:** generated SQL is restricted to SELECT/CTE queries, approved tables, row limits, read-only credentials and database timeouts.
- **Auditability:** responses expose route, tools used, SQL (when applicable) and document sources.
- **Bias:** deterministic risk rules can encode poor assumptions and must be reviewed against business context and disparate impacts.
- **Non-determinism:** LLM output can vary even with low temperature; deterministic validation is kept outside the model.
- **Limitations:** retrieval can miss relevant evidence, model-generated SQL can be wrong, and synthetic data does not prove real business impact.
