from dataclasses import dataclass

from app.core.config import get_settings
from app.core.security import sanitize_retrieved_text
from app.rag.chunker import chunk_documents
from app.rag.embeddings import get_embeddings
from app.rag.loader import load_documents

COLLECTION_NAME = "enterprise_policies"


@dataclass
class RetrievalResult:
    text: str
    metadata: dict
    distance: float


def _local_retrieve(query: str, top_k: int) -> list[RetrievalResult]:
    chunks = chunk_documents(load_documents())
    if not chunks:
        return []
    embedding_model = get_embeddings()
    query_vector = embedding_model.embed_query(query)
    chunk_vectors = embedding_model.embed_documents([chunk.text for chunk in chunks])

    scored = []
    for chunk, vector in zip(chunks, chunk_vectors):
        similarity = sum(a * b for a, b in zip(query_vector, vector))
        scored.append((1.0 - similarity, chunk))
    scored.sort(key=lambda item: item[0])
    return [
        RetrievalResult(
            text=sanitize_retrieved_text(chunk.text),
            metadata=chunk.metadata,
            distance=float(distance),
        )
        for distance, chunk in scored[:top_k]
    ]


def index_documents(reset: bool = True) -> int:
    chunks = chunk_documents(load_documents())
    if not chunks:
        return 0
    try:
        import chromadb
    except ImportError:
        # Development fallback: retrieval is computed in memory from the same chunks.
        return len(chunks)

    settings = get_settings()
    settings.chroma_path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(settings.chroma_path))
    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    embeddings = get_embeddings().embed_documents([chunk.text for chunk in chunks])
    collection.add(
        ids=[chunk.chunk_id for chunk in chunks],
        documents=[chunk.text for chunk in chunks],
        metadatas=[chunk.metadata for chunk in chunks],
        embeddings=embeddings,
    )
    return len(chunks)


def retrieve(
    query: str,
    top_k: int | None = None,
    filters: dict | None = None,
) -> list[RetrievalResult]:
    settings = get_settings()
    result_count = top_k or settings.retrieval_top_k

    try:
        import chromadb
    except ImportError:
        return _local_retrieve(query, result_count)

    settings.chroma_path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(settings.chroma_path))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    if collection.count() == 0:
        index_documents(reset=False)
    embedding = get_embeddings().embed_query(query)
    result = collection.query(
        query_embeddings=[embedding],
        n_results=result_count,
        where=filters or None,
        include=["documents", "metadatas", "distances"],
    )

    output = []
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]
    for text, metadata, distance in zip(docs, metas, distances):
        output.append(
            RetrievalResult(
                sanitize_retrieved_text(text),
                metadata or {},
                float(distance),
            )
        )
    return output
