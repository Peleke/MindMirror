# 🏋️‍♂️ Cyborg Coach — Your AI-Powered Performance Companion

Cyborg Coach (evolved from Librarian AI) is an intelligent agent that combines journaling, meal suggestions, and performance reviews into a comprehensive coaching system. Built with FastAPI, GraphQL, and LangChain, it provides personalized guidance based on your goals, activities, and reflections.

## 🔭 Vision

Your personal development shouldn't exist in silos. Cyborg Coach connects:

-   **Reflective Journaling**: Structured gratitude, reflection, and freeform entries
-   **Intelligent Meal Suggestions**: Based on your goals, recent workouts, and preferences  
-   **Performance Reviews**: AI-generated insights from your activity and journal history
-   **Document-Based Coaching**: RAG-powered advice from your uploaded knowledge base

Think: A personal coach that remembers everything and learns from your patterns.

## 🧠 Architecture

The system follows a multi-layer architecture from data ingestion to interactive applications.

```mermaid
graph TD
    subgraph "Frontend Layer"
        A[🖥️ Streamlit UI] --> B[📱 Mobile App];
        B --> C[🌐 Web Dashboard];
    end

    subgraph "API Gateway"
        D[🚪 Auth Gateway] --> E[🔑 JWT + User ID];
        E --> F[📊 GraphQL API];
    end

    subgraph "Service Layer"
        F --> G[📝 Journal Service];
        F --> H[🍽️ Suggestion Service];
        F --> I[📈 Review Service];
        G --> J[🗄️ PostgreSQL];
        H --> K[🤖 RAG Engine];
        I --> K;
    end

    subgraph "Data & AI"
        K --> L[📚 Vector Store];
        K --> M[🕸️ Knowledge Graph];
        L --> N[📄 PDF Documents];
        M --> N;
    end

    style F fill:#f9f,stroke:#333,stroke-width:2px
    style J fill:#ccf,stroke:#333,stroke-width:2px
```

## 🚀 Getting Started: Production Setup

This project is designed for a microservices architecture with proper authentication and database infrastructure.

**Prerequisites:**
*   Docker and Docker Compose
*   OpenAI API Key

**Quick Start:**

1.  **Clone the Repository**
    ```bash
    git clone <your-repo-url>
    cd librarian-ai
    ```

2.  **Set Environment Variables**
    Create a `.env` file:
    ```env
    OPENAI_API_KEY=your_key_here
    DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/cyborg_coach
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    POSTGRES_DB=cyborg_coach
    ```

3.  **Launch the Stack**
    ```bash
    docker-compose up --build
    ```

4.  **Access the Applications**
    - **GraphQL API**: http://localhost:8000/graphql
    - **Streamlit UI**: http://localhost:8501 (TODO)
    - **Documentation**: http://localhost:8000/docs

## 🛠️ Core Features

-   **✅ GraphQL API**: Full CRUD operations for journal entries with type-safe schema
-   **✅ Structured Journaling**: Gratitude, reflection, and freeform entry types
-   **✅ Meal Suggestions**: AI-powered recommendations based on goals and activity
-   **✅ Performance Reviews**: Bi-weekly insights from integrated data sources
-   **✅ RAG Integration**: Document-based coaching advice with citations
-   **🟡 Authentication**: Gateway-based JWT + user ID system (in progress)
-   **🟡 Streamlit UI**: Interactive frontend (in progress)
-   **🟡 Production Docker**: Full stack deployment (in progress)

## 🧪 Project Status

| Component         | Status      | Notes |
| ----------------- | ----------- | ----- |
| GraphQL API       | ✅ Done      | Full schema with unions, mutations |
| Journal Service   | ✅ Done      | CRUD with validation constraints |
| Suggestion Service| ✅ Done      | Meal recommendations + reviews |
| RAG Engine        | ✅ Done      | Document-based Q&A with citations |
| Test Suite        | ✅ Done      | 17 passing tests with Docker DB |
| Authentication    | 🟡 In Progress | Gateway-based JWT system |
| Streamlit UI      | 🟡 TODO      | Interactive frontend |
| Production Setup  | 🟡 TODO      | Docker-compose with real DB |

## 🧰 Tech Stack

| Layer           | Technology                   |
| --------------- | ---------------------------- |
| **API**         | FastAPI + Strawberry GraphQL |
| **Database**    | PostgreSQL + SQLAlchemy Async |
| **AI/RAG**      | LangChain + OpenAI |
| **Frontend**    | Streamlit (planned: React) |
| **Auth**        | Gateway JWT + User Headers |
| **Infrastructure** | Docker + Docker Compose |
| **Testing**     | Pytest + AsyncIO + Docker |

## 🔧 Development Flow

1.  **Clone & Setup**: `poetry install` for dependencies
2.  **Environment**: Copy `.env.example` and add your API keys
3.  **Database**: `docker-compose up postgres` for local DB
4.  **Run API**: `poetry run uvicorn api:app --reload`
5.  **Run Tests**: `poetry run pytest`
6.  **GraphQL Playground**: Visit http://localhost:8000/graphql

## 📊 API Examples

**Create a Journal Entry:**
```graphql
mutation CreateReflection($input: ReflectionEntryInput!) {
  createReflectionJournalEntry(input: $input) {
    id
    userId
    payload {
      wins
      improvements
    }
  }
}
```

**Get Meal Suggestion:**
```graphql
query GetMealSuggestion($tradition: String!, $mealType: String!) {
  mealSuggestion(tradition: $tradition, mealType: $mealType)
}
```

## 🔐 Authentication Architecture

The system is designed to work with a gateway-based auth system:

```
[Client] → [Auth Gateway] → [Cyborg Coach API]
           ↓
         - Validates JWT
         - Adds x-internal-id header
         - Forwards to service
```

The service receives:
- `request.extensions.jwt` (parsed by gateway)
- `x-internal-id` header (business logic user ID)

## 📈 Next Steps

1. **🎯 Streamlit Frontend**: Interactive UI for journaling and suggestions
2. **🐳 Production Docker**: Full stack with PostgreSQL container
3. **🔑 Auth Integration**: Proper JWT + user ID handling
4. **📱 Mobile-First**: Responsive design for daily use
5. **🚀 Deployment**: Cloud hosting with CI/CD

---

**Vision**: Transform scattered personal development practices into a unified, AI-enhanced coaching experience.