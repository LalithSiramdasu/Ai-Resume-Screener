from functools import lru_cache
from typing import List

from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL


class SentenceTransformerEmbeddings:
    """Minimal embedding wrapper with LangChain-like interface."""

    def __init__(self, model_name: str) -> None:
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        vectors = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return vectors.tolist()

    def embed_query(self, text: str) -> List[float]:
        return self.model.encode(text, show_progress_bar=False).tolist()


@lru_cache(maxsize=1)
def get_embeddings() -> SentenceTransformerEmbeddings:
    """Get a cached SentenceTransformer embedding model."""

    return SentenceTransformerEmbeddings(EMBEDDING_MODEL)
