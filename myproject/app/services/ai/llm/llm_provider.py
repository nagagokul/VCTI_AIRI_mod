from langchain_ollama import ChatOllama
from ....config import settings
from ..ollama_server import ensure_ollama_running


class LLMProvider:
    """Handles LLM calls using Ollama."""

    def __init__(self, model_name: str = None, temperature: float = 0.0):
        self.model_name = model_name or settings.arrange_llm
        self.temperature = temperature
        self.base_url = settings.base_url

    def get_client(self) -> ChatOllama:
        """Return a ChatOllama client instance."""
        ensure_ollama_running()
        return ChatOllama(
            model=self.model_name,
            temperature=self.temperature,
            base_url=self.base_url
        )