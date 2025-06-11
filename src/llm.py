from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.language_models import BaseChatModel
from typing import Any

from config import (
    LLM_PROVIDER,
    OPENAI_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_CHAT_MODEL,
)


def get_llm(provider: str = LLM_PROVIDER, **kwargs: Any) -> BaseChatModel:
    """
    Returns the language model instance based on the provider.
    Accepts additional keyword arguments to pass to the model constructor.
    """
    if provider == "ollama":
        # Ensure the base_url is passed explicitly
        kwargs.setdefault("base_url", OLLAMA_BASE_URL)
        return ChatOllama(model=OLLAMA_CHAT_MODEL, **kwargs)
    elif provider == "openai":
        # Ensure 'model_name' is passed to ChatOpenAI, not 'model'
        kwargs.setdefault("model_name", OPENAI_MODEL)
        if "model" in kwargs:
            del kwargs["model"]
        return ChatOpenAI(**kwargs)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}") 