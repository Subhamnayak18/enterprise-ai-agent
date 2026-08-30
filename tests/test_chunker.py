import pytest
from app.rag.chunker import chunk_document
from app.rag.loader import Document

def test_chunking_preserves_metadata():
    d=Document("A sentence. "*200,{"source":"x.md","document_name":"X"})
    chunks=chunk_document(d,200,40); assert len(chunks)>1; assert chunks[0].metadata["document_name"]=="X"

def test_invalid_chunk_config():
    with pytest.raises(ValueError): chunk_document(Document("x",{"source":"x"}),100,100)
