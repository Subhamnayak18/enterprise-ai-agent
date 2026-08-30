from app.llm.provider import LLMUnavailable, invoke_text
from app.prompts.prompts import RAG_SYSTEM
from app.rag.retriever import retrieve


def answer_knowledge(question: str) -> dict:
    results = retrieve(question)
    if not results:
        return {"answer": "I could not find relevant policy evidence.", "sources": [], "contexts": []}

    contexts = []
    sources = []
    for item in results:
        source = {
            "document_name": item.metadata.get("document_name"),
            "policy_version": item.metadata.get("policy_version"),
            "effective_date": item.metadata.get("effective_date"),
            "source": item.metadata.get("source"),
        }
        contexts.append(f"SOURCE {source}:\n{item.text}")
        sources.append(source)

    prompt = f"Question: {question}\n\nRetrieved evidence:\n" + "\n\n".join(contexts)
    try:
        answer = invoke_text(RAG_SYSTEM, prompt)
    except LLMUnavailable:
        answer = (
            "Relevant policy evidence was retrieved. Configure an LLM API key for a synthesized answer.\n\n"
            + contexts[0][:1200]
        )
    return {"answer": answer, "sources": sources, "contexts": contexts}
