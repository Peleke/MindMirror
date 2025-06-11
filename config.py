import os
from dotenv import load_dotenv

# Only load the .env file if we're not running in a Docker container
if os.getenv("I_AM_IN_A_DOCKER_CONTAINER") is None:
    load_dotenv()

# --- Directories ---
PDF_DIR = os.getenv("PDF_DIR", "pdfs")
DATA_DIR = os.getenv("DATA_DIR", "data")
VECTOR_STORE_DIR = os.path.join(DATA_DIR, "vectorstore")
GRAPH_STORE_PATH = os.path.join(DATA_DIR, "graph_store.json")
DOCS_CACHE_PATH = os.path.join(DATA_DIR, "docs_cache.json")


# --- LLM ---
# Set the provider to "openai" or "ollama"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai") 

# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Ollama settings
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "llama3")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

# Embedding Provider: "openai" or "ollama"
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai")

# --- Text Splitting ---
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150 