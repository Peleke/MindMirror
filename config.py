import os
import sys

from dotenv import load_dotenv

# Only load the .env file if we're not running in a Docker container
if os.getenv("I_AM_IN_A_DOCKER_CONTAINER") is None:
    load_dotenv()


def _is_docker_environment() -> bool:
    """Check if running inside Docker container."""
    # Check if we're running a script locally (force local mode)
    # Only apply this override if we're actually running a script from scripts/ directory
    if len(sys.argv) > 0 and sys.argv[0].endswith(".py") and "scripts/" in sys.argv[0]:
        return False

    return (
        os.path.exists("/.dockerenv")
        or os.getenv("DOCKER_CONTAINER") == "true"
        or os.getenv("IN_DOCKER") == "true"
        or os.getenv("I_AM_IN_A_DOCKER_CONTAINER") is not None
    )


# --- Directories ---
PDF_DIR = os.getenv("PDF_DIR", "pdfs")
DATA_DIR = os.getenv("DATA_DIR", "data")
VECTOR_STORE_DIR = os.path.join(DATA_DIR, "vectorstore")
GRAPH_STORE_PATH = os.path.join(DATA_DIR, "graph_store.json")
DOCS_CACHE_PATH = "./data/docs_cache.json"


# --- LLM ---
# Set the provider to "openai" or "ollama"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Ollama settings - auto-detect environment
_default_ollama_url = (
    "http://host.docker.internal:11434"
    if _is_docker_environment()
    else "http://localhost:11434"
)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", _default_ollama_url)

# Force localhost for scripts even if .env has Docker URL
if (
    not _is_docker_environment()
    and OLLAMA_BASE_URL == "http://host.docker.internal:11434"
):
    OLLAMA_BASE_URL = "http://localhost:11434"

OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "llama3")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

# Embedding Provider: "openai" or "ollama"
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai")

# --- Text Splitting ---
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/cyborg_coach"
)
