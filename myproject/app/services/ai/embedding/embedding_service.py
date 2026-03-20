from .embedding_provider import EmbeddingProvider

_embedding_instance = None


def get_embedding_provider() -> EmbeddingProvider:
    """
    Return a shared embedding provider instance.
    Loads model only once.
    """
    global _embedding_instance

    if _embedding_instance is None:
        print("Loading embedding model...")
        _embedding_instance = EmbeddingProvider()

    return _embedding_instance

get_embedding_provider()