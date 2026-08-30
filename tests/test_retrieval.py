from app.rag.retriever import retrieve


def test_local_retrieval_returns_policy_source():
    results = retrieve("supplier delivery SLA on-time delivery below 90 percent", top_k=3)
    assert results
    names = {item.metadata.get("document_name") for item in results}
    assert "Supplier Delivery SLA" in names
