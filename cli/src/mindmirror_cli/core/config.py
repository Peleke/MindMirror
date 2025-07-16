"""Configuration for MindMirror CLI."""

import os
from typing import Dict, Optional

# Embedding model configurations
EMBEDDING_MODEL_CONFIGS = {
    "nomic-embed-text": {
        "dimensions": 768,
        "provider": "ollama",
        "description": "Nomic embedding model (768 dimensions)"
    },
    "rjmalagon/gte-qwen2-1.5b-instruct-embed-f16": {
        "dimensions": 1536,
        "provider": "ollama", 
        "description": "Qwen2 embedding model (1536 dimensions)"
    },
    "text-embedding-3-small": {
        "dimensions": 1536,
        "provider": "openai",
        "description": "OpenAI embedding model (1536 dimensions)"
    },
    "text-embedding-ada-002": {
        "dimensions": 768,
        "provider": "openai",
        "description": "OpenAI legacy embedding model (768 dimensions)"
    }
}

def get_embedding_model_config(model_name: str) -> Optional[Dict]:
    """Get configuration for an embedding model."""
    return EMBEDDING_MODEL_CONFIGS.get(model_name)

def get_embedding_dimensions(model_name: str) -> int:
    """Get the vector dimensions for an embedding model."""
    config = get_embedding_model_config(model_name)
    if config:
        return config["dimensions"]
    
    # Default fallback
    return 1536

def get_embedding_provider(model_name: str) -> str:
    """Get the provider for an embedding model."""
    config = get_embedding_model_config(model_name)
    if config:
        return config["provider"]
    
    # Default fallback
    return "ollama"

def set_embedding_environment(model_name: str):
    """Set environment variables for an embedding model."""
    config = get_embedding_model_config(model_name)
    if not config:
        # Unknown model, use defaults
        os.environ["EMBEDDING_VECTOR_SIZE"] = "1536"
        os.environ["EMBEDDING_PROVIDER"] = "ollama"
        return
    
    # Set provider-specific environment variables
    if config["provider"] == "ollama":
        os.environ["OLLAMA_EMBEDDING_MODEL"] = model_name
        os.environ["EMBEDDING_PROVIDER"] = "ollama"
    elif config["provider"] == "openai":
        os.environ["EMBEDDING_MODEL"] = model_name
        os.environ["EMBEDDING_PROVIDER"] = "openai"
    
    # Set vector size
    os.environ["EMBEDDING_VECTOR_SIZE"] = str(config["dimensions"]) 