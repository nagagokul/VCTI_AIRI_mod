from __future__ import annotations

from typing import List, Sequence

from langchain_ollama import OllamaEmbeddings
from ollama import ResponseError

from ..ollama_server import ensure_ollama_running
from ....config import settings


MAX_EMBED_CHARS = 3000
CHUNK_OVERLAP_CHARS = 200


class EmbeddingProvider:
    """Handles generating embeddings using Ollama."""

    def __init__(self, model_name: str = None):
        ensure_ollama_running()
        self.model_name = model_name or settings.embedding_default_model
        self.embeddings_client = OllamaEmbeddings(
            model=self.model_name,
            base_url=settings.base_url,
        )
        self.vector_size: int | None = None

    def generate(self, text: str) -> List[float]:
        """Generate an embedding for a single text string."""
        return self._embed_text(text)

    def batch_generate(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts, safely handling oversized inputs."""
        return [self._embed_text(text) for text in texts]

    def _embed_text(self, text: str) -> List[float]:
        cleaned = (text or "").strip()
        if not cleaned:
            return self._zero_vector()

        chunks = self._split_text(cleaned, max_chars=MAX_EMBED_CHARS)
        chunk_vectors = [self._embed_chunk_with_retry(chunk) for chunk in chunks]
        if len(chunk_vectors) == 1:
            return chunk_vectors[0]

        weights = [max(len(chunk.strip()), 1) for chunk in chunks]
        return self._weighted_average(chunk_vectors, weights)

    def _embed_chunk_with_retry(self, text: str, max_chars: int | None = None) -> List[float]:
        chunk = (text or "").strip()
        if not chunk:
            return self._zero_vector()

        current_limit = max_chars or MAX_EMBED_CHARS

        try:
            vector = self.embeddings_client.embed_documents([chunk])[0]
            if self.vector_size is None:
                self.vector_size = len(vector)
            return vector
        except ResponseError as exc:
            if not self._is_context_length_error(exc):
                raise

            if len(chunk) <= 1:
                raise

            next_limit = min(current_limit // 2 if current_limit > 1 else 1, max(len(chunk) // 2, 1))
            next_limit = max(next_limit, 1)

            smaller_chunks = self._split_text(chunk, max_chars=next_limit)
            if len(smaller_chunks) == 1 and smaller_chunks[0] == chunk:
                midpoint = max(len(chunk) // 2, 1)
                smaller_chunks = [chunk[:midpoint], chunk[midpoint:]]
            smaller_vectors = [self._embed_chunk_with_retry(part, max_chars=next_limit) for part in smaller_chunks]
            if len(smaller_vectors) == 1:
                return smaller_vectors[0]

            weights = [max(len(part.strip()), 1) for part in smaller_chunks]
            return self._weighted_average(smaller_vectors, weights)

    def _split_text(self, text: str, max_chars: int) -> List[str]:
        normalized = (text or "").strip()
        if not normalized:
            return [""]
        if len(normalized) <= max_chars:
            return [normalized]

        chunks: List[str] = []
        start = 0
        text_length = len(normalized)

        while start < text_length:
            end = min(start + max_chars, text_length)
            if end < text_length:
                split_at = self._find_split_point(normalized, start, end)
                if split_at and split_at > start:
                    end = split_at

            piece = normalized[start:end].strip()
            if piece:
                chunks.append(piece)

            if end >= text_length:
                break

            next_start = max(end - CHUNK_OVERLAP_CHARS, start + 1)
            start = next_start

        return chunks or [normalized[:max_chars].strip()]

    def _find_split_point(self, text: str, start: int, end: int) -> int:
        for marker in ("\n\n", "\n", ". ", "; ", ", ", " "):
            idx = text.rfind(marker, start, end)
            if idx != -1:
                return idx + len(marker)
        return end

    def _weighted_average(self, vectors: Sequence[Sequence[float]], weights: Sequence[int]) -> List[float]:
        if not vectors:
            return self._zero_vector()

        total_weight = sum(weights) or len(vectors)
        width = len(vectors[0])
        averaged = [0.0] * width

        for vector, weight in zip(vectors, weights):
            for i, value in enumerate(vector):
                averaged[i] += float(value) * weight

        return [value / total_weight for value in averaged]

    def _zero_vector(self) -> List[float]:
        if self.vector_size is None:
            probe = self.embeddings_client.embed_documents(["placeholder"])[0]
            self.vector_size = len(probe)
        return [0.0] * self.vector_size

    @staticmethod
    def _is_context_length_error(exc: ResponseError) -> bool:
        return "context length" in str(exc).lower() or "input length exceeds" in str(exc).lower()
