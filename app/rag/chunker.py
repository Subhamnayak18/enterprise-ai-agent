from dataclasses import dataclass
import re

from app.rag.loader import Document


@dataclass
class Chunk:
    chunk_id: str
    text: str
    metadata: dict


def chunk_document(document: Document, chunk_size: int = 900, overlap: int = 120) -> list[Chunk]:
    if chunk_size <= overlap or overlap < 0:
        raise ValueError("chunk_size must be greater than overlap")
    text = " ".join(document.text.split())
    chunks = []
    start = 0
    index = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        if end < len(text):
            boundary = text.rfind(". ", start, end)
            if boundary > start + chunk_size // 2:
                end = boundary + 1
        chunk_text = text[start:end].strip()
        if chunk_text:
            metadata = {**document.metadata, "chunk_index": index}
            chunk_id = f"{document.metadata['source']}::{index}"
            chunks.append(Chunk(chunk_id=chunk_id, text=chunk_text, metadata=metadata))
            index += 1
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks


def chunk_documents(documents: list[Document], chunk_size: int = 900, overlap: int = 120) -> list[Chunk]:
    return [chunk for doc in documents for chunk in chunk_document(doc, chunk_size, overlap)]
