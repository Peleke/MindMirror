# 📚 Librarian AI — Your Personal AI-Powered Library Agent

Librarian AI is an intelligent agent that transforms your private document corpus—starting with a massive PDF book collection—into a fully navigable, queryable digital librarian. It's built with LangChain and Graph RAG to support both deep semantic understanding and structural knowledge across your documents.

## 🔭 Vision

Information shouldn't be trapped in static documents. Librarian AI turns passive books into active agents that:

-   **Answer questions with citations**: Get answers grounded in your source material.
-   **Understand relationships**: Uncover connections between concepts, people, and ideas across your library.
-   **Generate new content**: Create summaries, quizzes, articles, and learning materials on demand.
-   **Scale with you**: From a personal library to an entire organization's knowledge base.

Think: ChatGPT meets your personal library—with memory and superpowers.

## 🧠 Architecture

The system follows a multi-stage pipeline from raw documents to an interactive chat application.

```mermaid
graph TD
    subgraph "1. Data Ingestion & Processing"
        A[📚 PDF Books] --> B{LangChain PDF Loader};
        B --> C{Text Splitter};
        C --> D[📄 Chunked Documents];
    end

    subgraph "2. Knowledge Extraction"
        D --> E{Embedding Model};
        E --> F[💾 Vector Store (FAISS)];
        D --> G{LLM for Graph Extraction};
        G --> H[🕸️ Knowledge Graph (NetworkX)];
    end

    subgraph "3. Retrieval & Generation"
        I[🧑‍💻 User Query] --> J{Graph-RAG Retriever};
        F --> J;
        H --> J;
        J --> K{LLM};
        K --> L[💬 Answer with Citations];
    end

    style F fill:#f9f,stroke:#333,stroke-width:2px
    style H fill:#ccf,stroke:#333,stroke-width:2px
```

## 🚀 Getting Started: One-Command Demo

This project is fully containerized with Docker, allowing you to launch the entire application stack—the GraphQL API and the Streamlit UI—with a single command.

**Prerequisites:**
*   Docker and Docker Compose

**Instructions:**

1.  **Clone the Repository**
    ```bash
    git clone <your-repo-url>
    cd librarian-ai
    ```

2.  **Set Your API Key**
    Create a `.env` file in the root of the project and add your OpenAI API key:
    ```
    OPENAI_API_KEY=your_key_here
    ```

3.  **Launch the Application**
    ```bash
    docker-compose up --build
    ```
    This command will:
    *   Build the Docker image for the application.
    *   Start the API service, which will first build the knowledge base from the documents in `/pdfs`.
    *   Start the Streamlit UI service.

4.  **Access the Coach**
    Once the build is complete, open your web browser and navigate to **http://localhost:8501** to start interacting with your AI Coach.

## 🛠️ Core Features

-   **RAG-based Chatbot**: Engage in conversations with your documents via a chatbot that uses embedded context.
-   **Graph-Enhanced Retrieval**: Detect and navigate complex relationships (e.g., *who invented what*, *what concepts are related*).
-   **LLM-Generated Citations**: Get citations with source filenames and page numbers for every answer.
-   **Extensible Agent Framework**: Add tools to generate flashcards, write summaries, or even quiz you on the material.

## 🧪 Project Status

| Component         | Status      |
| ----------------- | ----------- |
| PDF Loader        | ✅ Done      |
| Text Chunking     | ✅ Done      |
| Vector Store      | ✅ Done      |
| Graph Store       | ✅ Done      |
| Chatbot (CLI)     | ✅ Done      |
| Streamlit UI      | ✅ Done      |
| Multi-agent tools | 🟡 TODO      |

## 🧰 Tech Stack

| Layer           | Technology                   |
| --------------- | ---------------------------- |
| LLM             | OpenAI / Anthropic           |
| RAG Framework   | LangChain, LangGraph         |
| Graph Store     | NetworkX (local), Neo4j (scalable) |
| Vector DB       | FAISS (local), Chroma (scalable) |
| PDF Parser      | PyMuPDF                      |
| UI              | CLI, Streamlit    |
| Infrastructure  | Local-first, designed for cloud |

## 🧱 How it Works: Dev Flow

1.  **Clone the Repo**: Get the project structure on your local machine.
2.  **Install Dependencies**: Run `poetry install`.
3.  **Add Documents**: Drop your PDFs into the `/pdfs` directory.
4.  **Set Environment**: Create a `.env` file and add your `OPENAI_API_KEY`.
5.  **Run the App**: Launch the Streamlit UI with `poetry run streamlit run app.py`. The app will handle data ingestion on the first run.
6.  **Chat**: Start asking questions!

## 🗂️ Project Scaffold

Here's the full project structure. You can use this to set up your workspace.

```
librarian-ai/
├── pdfs/                      # Drop your PDFs here
├── data/
│   ├── vectorstore/           # Persisted vector DB
│   ├── graph_store.json       # Persisted graph data
│   └── docs_cache.json        # Cache for parsed docs
├── src/
│   ├── __init__.py
│   ├── loading.py             # Loads and chunks PDFs
│   ├── embedding.py           # Embeds docs to vector store
│   ├── graph.py               # Extracts and builds knowledge graph
│   └── chain.py               # RAG chain and chatbot logic
├── scripts/
│   ├── run_ingestion.py       # Script to run the full data pipeline
│   └── run_chat.py            # Script to start the chatbot
├── .env                       # Secrets (e.g., OPENAI_API_KEY)
├── config.py                  # Paths, model config, etc.
├── poetry.lock                # Poetry lock file
├── pyproject.toml             # Python dependencies
└── README.md
```

## 📄 pyproject.toml dependencies

```txt
langchain
langgraph
langchain-experimental
openai
tiktoken
faiss-cpu
PyMuPDF
networkx
python-dotenv
streamlit
```

## 🔧 config.py

```python
import os
from dotenv import load_dotenv

load_dotenv()

PDF_DIR = "./pdfs"
VECTOR_STORE_DIR = "./data/vectorstore"
GRAPH_STORE_PATH = "./data/graph_store.json"
DOCS_CACHE_PATH = "./data/docs_cache.json"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

📈 Scaling & Revenue Potential
This foundation unlocks:

Internal enterprise knowledge assistants

Custom book/course tutors

B2C learning assistants from proprietary content

Generative tools for authors, publishers, and coaches