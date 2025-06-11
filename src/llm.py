from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.language_models import BaseChatModel

from config import (
    LLM_PROVIDER,
    OPENAI_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_CHAT_MODEL,
)


def get_llm(provider: str = LLM_PROVIDER) -> BaseChatModel:
    """
    Returns the language model instance based on the provider.
    """
    if provider == "ollama":
        return ChatOllama(model=OLLAMA_CHAT_MODEL, base_url=OLLAMA_BASE_URL)
    elif provider == "openai":
        return ChatOpenAI(temperature=0, model_name=OPENAI_MODEL)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}") 