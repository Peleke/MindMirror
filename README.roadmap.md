# 🧠 AI Coaching Platform: Roadmap & Architecture

## 1. Executive Vision: From Passive Tracker to Active Coach

Today's health and fitness apps are excellent at collecting data, but they fail at converting that data into wisdom. Users are left with a dashboard of disconnected metrics, struggling to understand *why* they feel a certain way or *what* they should do next.

**This project fundamentally changes that paradigm.**

We are building a platform that transforms a user's health data and a library of trusted knowledge into a **personalized, evidence-based AI coach**. Our system doesn't just track what you did; it understands *why* you did it, synthesizes it with world-class expertise, and provides proactive, actionable insights to help you achieve your goals faster.

Our vision is to give every user a personal performance scientist in their pocket, creating a feedback loop of engagement, trust, and results that is impossible for generic fitness apps to replicate.

---

## 2. Phase 1: The Personalized Science Dashboard (The MVP)

**Goal:** To build a high-impact, demonstrable PoC that showcases the core value proposition: "Your Data, Your Experts, Your Insights." This MVP will be ready to integrate as a standalone `coach` service into the existing production architecture.

### Key Features

1.  **Bring Your Own Canon:** Users upload their trusted sources (books, articles, coach's notes), and the AI grounds all of its analysis in that specific knowledge base. The demo will come pre-loaded with several canonical texts to show immediate value.
2.  **The Bi-Weekly "Performance & Reflection" Summary:** A one-click summary of the user's recent performance, highlighting a key success and an area for improvement, followed by a guided journal prompt to connect quantitative data with qualitative feeling.
3.  **The "In-the-Moment" Food Architect:** A conversational feature allowing users to ask highly contextual questions like, "I have 500 calories left, what's an optimal final meal for muscle recovery?"

### PoC Architecture

The initial PoC will use Streamlit as a lightweight UI to demonstrate the backend engine. The core logic will be encapsulated in a `CoachingEngine` class and exposed via a Strawberry GraphQL server, ensuring it is decoupled and ready for integration.

```mermaid
graph TD
    subgraph "Proof of Concept"
        A[Streamlit UI (Temporary)] --> B{Strawberry GraphQL Server};
        B --> C[Coaching Engine];
        C --> D[RAG & Graph Pipeline];
        D --> E[Ollama / OpenAI];
    end
```

### Target Integration Architecture

The `CoachingEngine` and Strawberry server are designed to be packaged and deployed as a new `coach` service within the existing backend mesh. The Flutter frontend will communicate with it via the federated GraphQL gateway.

```mermaid
graph TD
    subgraph "User Layer"
        F[Flutter Mobile App]
    end
    subgraph "Backend Infrastructure"
        G[Hive Gateway (GraphQL Federation)]
        H[Workout Service]
        I[Meals Service]
        J[User Data Service]
        K[<b>Coach Service (This Project)</b>]
    end

    F -->|GraphQL Query/Mutation| G;
    G --> H;
    G --> I;
    G --> J;
    G -->|Routes coaching requests| K;

    subgraph "Coach Service Internals"
        direction LR
        L[Strawberry Server (GraphQL)] --> M[Coaching Engine] --> N[RAG & Graph Pipeline] --> O[Ollama / OpenAI]
    end
    
    K --> L
```

---

## 3. Phase 1: Implementation Plan & TDD Roadmap (✅ Complete)

This phase established the core architectural foundation.

### ✅ **Milestone 1: Encapsulate Core Logic into a Reusable Engine**
*   [x] **Task 1.1:** Create a new `src/engine.py` file.
*   [x] **Task 1.2:** Implement a `CoachingEngine` class within it.
*   [x] **Task 1.3:** Move the core logic from `app.py`'s `get_retriever` and `get_rag_chain` functions into methods within the `CoachingEngine` class.
*   [x] **Task 1.4:** Create a new test file `tests/test_engine.py`.
*   [x] **Task 1.5 (TDD):** Write tests to confirm the `CoachingEngine` can be initialized, can load documents, and can return a valid RAG chain.

### ✅ **Milestone 2: Expose the Engine via a Decoupled API**
*   [x] **Task 2.1:** Create a new `api.py` at the root of the project.
*   [x] **Task 2.2:** Implement a Strawberry GraphQL server in `api.py`.
*   [x] **Task 2.3:** On startup, initialize a global instance of the `CoachingEngine`.
*   [x] **Task 2.4 (TDD):** Implement a `ask` query that takes a user query, calls the engine's RAG chain, and returns the response.
*   [x] **Task 2.5 (TDD):** Implement a `generateReview` mutation that simulates grabbing user data and calling the engine with a structured prompt.
*   [x] **Task 2.6:** Implement an `uploadDocument` mutation that saves a file to the `pdfs` directory and triggers the engine to reload its knowledge base.

### ✅ **Milestone 3: Adapt the Streamlit UI to be a Pure API Client**
*   [x] **Task 3.1:** Refactor `app.py` to remove all direct calls to the backend logic.
*   [x] **Task 3.2:** All functionality (chat, file uploads) in `app.py` now make GraphQL requests to the local Strawberry server.
*   [x] **Task 3.3:** Implement the "Generate My Bi-Weekly Review" button and the guided journal UI components.
*   [x] **Task 3.4:** Ensure the UI correctly handles the loading states while waiting for API responses.

### ✅ **Milestone 4: Finalize PoC for Demo**
*   [ ] **Task 4.1:** Pre-load the `./pdfs` directory with 2-3 canonical nutrition/fitness texts.
*   [ ] **Task 4.2:** Create a `docker-compose.yml` file to easily run the Strawberry server and the Streamlit UI together.
*   [ ] **Task 4.3:** Write a final `README.md` with simple, clear instructions on how to run the demo.

---

## 4. Phase 2: The Cyborg Coach (The Vision)

**Goal:** To evolve from a personalized dashboard into a personal science platform where users can prove causation in their own lives, fine-tune a truly personal AI, and maintain complete ownership over their data and models.

The detailed, multi-milestone plan for this next major phase of development is outlined in the vision document:

### ➡️ **[Read the Full Plan: README.vision.md](./README.vision.md)** 