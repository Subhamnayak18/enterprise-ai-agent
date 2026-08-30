import hashlib
import math
import re
from collections import Counter

from app.llm.provider import LLMUnavailable, get_embedding_model


class LocalHashEmbeddings:
    """Deterministic offline fallback for development/tests, not a semantic production model."""
    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        counts = Counter(tokens)
        for token, count in counts.items():
            digest = hashlib.md5(token.encode()).hexdigest()
            index = int(digest[:8], 16) % self.dimensions
            sign = -1.0 if int(digest[8:10], 16) % 2 else 1.0
            vector[index] += sign * count
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


def get_embeddings():
    try:
        return get_embedding_model()
    except LLMUnavailable:
        return LocalHashEmbeddings()
