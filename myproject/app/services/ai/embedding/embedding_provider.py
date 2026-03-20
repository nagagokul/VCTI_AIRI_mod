from typing import List
from langchain_ollama import OllamaEmbeddings
from ..ollama_server import ensure_ollama_running
from ....config import settings

class EmbeddingProvider:
    """Handles generating embeddings using Ollama."""

    def __init__(self, model_name: str = None):
        ensure_ollama_running()
        self.model_name = model_name or settings.embedding_default_model
        self.embeddings_client = OllamaEmbeddings(
            model=self.model_name,
            base_url=settings.base_url
        )
        self.vector_size: int | None = None

    def generate(self, text: str) -> List[float]:
        """Generate embedding for a single text string."""
        if not text.strip():
            if self.vector_size is None:
                raise ValueError("Vector size unknown for empty input")
            return [0.0] * self.vector_size

        vector = self.embeddings_client.embed_documents([text])[0]
        if self.vector_size is None:
            self.vector_size = len(vector)
        return vector

    def batch_generate(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        vectors = self.embeddings_client.embed_documents(texts)
        if self.vector_size is None and vectors:
            self.vector_size = len(vectors[0])
        return vectors
