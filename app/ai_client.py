import os
from openrouter import OpenRouter

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY environment variable not set!")

_openrouter_client = None

def get_openrouter_client() -> OpenRouter:
    """Возвращает клиент OpenRouter (синглтон)."""
    global _openrouter_client
    if _openrouter_client is None:
        _openrouter_client = OpenRouter(api_key=OPENROUTER_API_KEY)
    return _openrouter_client