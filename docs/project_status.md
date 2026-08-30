# Project Status

## Implemented

- FastAPI backend and health endpoint
- PostgreSQL/SQLAlchemy data model
- Synthetic supply-chain dataset generator and database seeder
- Seven synthetic enterprise procurement/quality/inventory policy documents
- Document loader, chunker, metadata and embeddings abstraction
- Chroma retrieval path with an offline in-memory fallback for development
- LLM provider abstraction using LangChain OpenAI integration
- Safe natural-language-to-SQL tool
- Deterministic supplier risk tool
- Hybrid SQL + policy workflow
- Supplier escalation report workflow
- Constrained LangGraph routing graph with five routes
- Streamlit UI
- Upload/index/source/conversation API endpoints
- Responsible-AI and prompt-injection safeguards
- Pytest suite
- Curated evaluation suite and measured results
- Dockerfile, Docker Compose and GitHub Actions workflow
- AWS deployment design
- Interview guide and resume bullets

## Verified in this build environment

- Python compilation passed
- 20/20 tests passed
- Synthetic data generation passed
- SQLite development database seed passed
- RAG route passed using local retrieval fallback
- SQL route passed using safe development SQL templates
- Hybrid route passed
- Supplier-risk route passed
- Escalation-report route passed
- FastAPI `/chat`, `/sources`, and `/documents/index` passed with TestClient
- Routing evaluation: 50/50
- Retrieval source hit@3 checks: 7/7
- Unsafe SQL rejection checks: 6/6

## Not externally executed here

The sandbox cannot install additional packages from the internet and has no cloud credentials. Therefore the installed-package Chroma/LangGraph/OpenAI path, Docker image build, PostgreSQL Docker service, and public AWS deployment were not executed in this environment. The source code and dependency/API usage were aligned with current official documentation, but you should run the README setup once on your machine before putting the repository on your resume.
