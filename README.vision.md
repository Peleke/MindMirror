# 🧠 Cyborg Coach: Vision & Roadmap

## 1. The Vision: Your Generative Performance Engine

The Cyborg Coach is a symbiotic system that fuses trusted, external wisdom with a user's own internal, subjective experience. It is not merely a tool, but a digital twin of the user's performance journey.

The ultimate goal is to create a **generative performance engine**. A user shouldn't just ask "What should I eat?"; they should be able to state a complex, multi-faceted goal in natural language and have the system generate a complete, actionable plan.

---

## 2. Personas We Serve

We are building for individuals who are proactive about their well-being but face common, complex challenges. Our target personas include:

*   **The Overwhelmed Beginner:** Knows they need to make a change but is paralyzed by information overload and a fear of getting it wrong. They need clear guidance, a low barrier to entry, and a plan that feels achievable.
    *   *"I've been running and lifting some weights for a while but don't really know what to do next. I like yoga a lot. Can you make me a 6-week program for getting started with strength? I'm scared of gyms though."*

*   **The Life-Constrained Optimizer:** Already has an established routine and goals but needs to adapt them to the messy reality of life—travel, stress, lack of equipment, or fluctuating energy levels.
    *   *"I'm going on vacation for two weeks with no equipment. I'd like to keep working out to the same goals; can you update my plans?"*

*   **The Holistic Explorer:** Views their body and mind as a single system and is keen to experiment with different philosophies (e.g., Ayurveda, Stoicism, Paleo) to see how they impact mood, energy, and performance.
    *   *"I'm having trouble sleeping; I'm pretty sure it's my eating. Can you give me an Ayurvedic diet and adjust my yoga flows? I've been having lots of kapha energy."*

*   **The Habit Builder:** Feels "off track" and needs help building foundational habits to regain a sense of control and well-being, starting with small, atomic actions.
    *   *"I'm a fucking wreck lately. Give me 4 habits to build that will help me with sleep and eating a reasonable diet."*

---

## 3. The Architecture: A Federated Agentic System

To serve these needs, we are building a distributed system of specialized microservices, orchestrated by a central **Agent Service**.

### Core Domain Services

These are standard, "dumb" CRUD services that manage a specific domain of data. They expose their functionality via a federated GraphQL schema.

*   **Users:** The source of truth for user identity. Maps auth provider IDs to internal IDs and manages service access/subscriptions.
*   **Practices:** Manages workout templates, programs (sequences of workouts), and user enrollments. Includes a local RBAC system for coaches and clients.
*   **Meals:** Tracks food items, recipes, meal logs, and user-specific nutritional goals.
*   **Journaling:** (To be extracted from the current monolith) Manages structured (Gratitude, Reflection) and unstructured journal entries.
*   **Movements (The "Brain"):** A data-only service with a graph-native representation of exercises, their relationships (progressions, regressions, variants), and contraindications.
*   **Future Services:** `Sleep`, `Menstrual Tracking`, `Causal AI/Experiments`.

### The Agent Service (The "Heart")

This is the only service with direct access to LLMs. It consumes the federated GraphQL API of the other services to execute complex, multi-step plans. Its workflow is:
1.  Receive a natural language command from the user.
2.  **Intent Router:** Classify the command. Is it a simple RAG query or a complex action?
3.  **LangGraph Planner:** If it's an action, create a multi-step plan using a "Tool Belt" of available functions.
4.  **Tool Execution:** Execute the plan by calling the necessary GraphQL queries/mutations on the federated gateway.
5.  **Synthesize Response:** Formulate a human-readable summary of the actions taken.

---

## 4. Phased Implementation Plan

### ✅ Milestone 1: The Curated Canon & The Journal
*   **Status:** COMPLETE
*   **Outcome:** A functional monolith PoC where a user can select a knowledge base ("Tradition") and interact with a basic RAG and Journaling system.

### ✅ Milestone 2: The Aware Synthesist
*   **Status:** COMPLETE
*   **Outcome:** The PoC can synthesize data from mocked external services to provide contextual meal suggestions and bi-weekly performance reviews. Structured journaling (Gratitude, Reflection) is implemented.

### 🟡 Milestone 3: The Production-Ready Foundation
*   **Status:** IN PROGRESS
*   **Goal:** Harden the PoC by migrating critical services to a robust, database-backed foundation, preparing for the distributed architecture.
*   **TDD Roadmap:**
    *   **Task 3.1 (Database):** Introduce SQLAlchemy. Migrate the `JournalRepository` from a JSON file to a PostgreSQL database.
    *   **Task 3.2 (Services):** Formally define the `JournalService` and `PracticeService` boundaries within the monolith. Begin building out the `PracticeRepository` with SQLAlchemy models.
    *   **Task 3.3 (Containerization):** Finalize `docker-compose.yml` for a one-command launch of the application and its database. Ensure data persistence across restarts.

### 🤖 Milestone 4: The Distributed Agent
*   **Status:** TODO
*   **Goal:** Refactor the monolith into the target federated microservices architecture.
*   **TDD Roadmap:**
    *   **Task 4.1 (Contracts):** Define the full GraphQL schemas for `Journals`, `Practices`, and `Users`.
    *   **Task 4.2 (Federation):** Introduce a Hive GraphQL Gateway. Decompose the monolith and stand up the `JournalService` and `PracticeService` as independent microservices federated under the gateway.
    *   **Task 4.3 (Agent Extraction):** Create the new `Agent Service`. Lift and shift the LLM-based logic (currently in `SuggestionService`) into this new service.
    *   **Task 4.4 (Tooling):** Implement the agent's Tool Belt. The tools will not call Python services directly but will instead make GraphQL calls to the Hive Gateway, completing the decoupling.

# Cyborg Coach Vision: Milestone 2 & 3

This document outlines the product vision for the next phases of the Cyborg Coach, building upon the foundational RAG and API architecture.

## Milestone 2: The Aware Synthesist (In Progress)

**Goal:** Make the coach's advice contextual to the user's immediate goals and history. The coach moves from being a passive Q&A agent to a proactive, aware partner.

### Features

1.  **Reactive Meal Suggestions (`getMealSuggestion`) - ✅ COMPLETE**
    *   **User Story:** As a user, when I'm wondering what to eat, I can ask the coach for a suggestion that aligns with my calorie/protein goals and my last workout.
    *   **Implementation:** An API endpoint that takes user context (goals, history) and uses the RAG engine to generate a specific, tradition-aligned meal suggestion.

2.  **Reflective Performance Reviews (`generateReview`) - ✅ COMPLETE**
    *   **User Story:** As a user, every two weeks, I want the coach to analyze my workout, meal, and journal history to give me a summary of what I did well, where I can improve, and what to focus on next.
    *   **Implementation:** An API endpoint that synthesizes data from multiple (mocked) client services and the user's journal, feeding it into a comprehensive prompt for the RAG engine to generate a structured review.

3.  **Structured Journaling (`createGratitudeJournalEntry`, `createReflectionJournalEntry`) - 🟡 TODO**
    *   **User Story (Morning):** As a user, at the start of my day, I want the coach to prompt me to list things I'm grateful for and excited about, set a focus, and state an affirmation, so I can begin my day with intention.
    *   **User Story (Evening):** As a user, at the end of my day, I want the coach to prompt me to list my wins and identify areas for improvement, so I can close my day with reflection.
    *   **Implementation:** The application will feature distinct "Gratitude" and "Reflection" journaling modes. These will be structured forms presented to the user daily. The data will be stored with a specific type, distinguishing it from regular free-form journal entries, and will be incorporated into the bi-weekly performance reviews to provide deeper insights into the user's mindset and progress.

## Milestone 3: The Proactive Companion

**Goal:** Enable the coach to initiate interactions, manage long-term memory, and perform actions on the user's behalf.

*   **Proactive Nudges:** The coach will send notifications (e.g., "You haven't logged a workout in 3 days, how about a short one today?") based on user patterns.
*   **Long-Term Memory & Evolution:** The coach will remember key conversations, user preferences, and evolving goals over months, not just days.
*   **Agentic Actions:** The coach will be able to perform actions like "add this suggested meal to my cronometer" or "schedule a 30-min workout on my calendar." 