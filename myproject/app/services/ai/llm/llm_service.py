from .llm_provider import LLMProvider

_llm_instance = None


def get_llm():
    """
    Return shared LLM client.
    """
    global _llm_instance

    if _llm_instance is None:
        print("Loading LLM...")
        provider = LLMProvider()
        _llm_instance = provider.get_client()

    return _llm_instance

get_llm()