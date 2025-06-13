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

### **Agent Kernel Implementation Plan**

This section outlines the concrete architectural blueprint for the `agent_kernel/` package. The kernel is designed as a **stateful computation graph**, where each user request initiates a traversal through the graph. This provides modularity, observability, and the ability to handle complex, branching logic.

#### **1. Foundational Directory Structure**
```
agent_kernel/
├── __init__.py           # Exposes the main `handle_request` entry point.
├── state.py              # Defines the central `AgentState` model.
├── graph.py              # Constructs and compiles the main computation graph.
├── registry.py           # Houses the `ToolRegistry` and `IntentRegistry`.
│
├── nodes/                # Directory for all graph nodes (processing functions).
│   ├── 1_route_intent.py   # Node to determine user's intent.
│   ├── 2_create_plan.py    # Node to generate a multi-step plan.
│   ├── 3_execute_tools.py  # Node to invoke tools from the toolbelt.
│   └── 4_format_response.py# Node to synthesize the final answer.
│
├── tools/                # The "Toolbelt": implementations of specific tools.
│   ├── _protocol.py        # Defines the `Tool` interface protocol.
│   ├── journal_tool.py     # Tool for journal entry creation/search.
│   └── knowledge_tool.py   # Tool for RAG against tradition knowledge.
│
└── intents/              # Definitions and recognizers for user intents.
    ├── _protocol.py        # Defines the `Intent` interface.
    ├── journal_intent.py
    └── question_intent.py
```

#### **2. Core Data Structure: `AgentState`**
The `AgentState` is the single object that flows through the graph, accumulating information at each step.

**(File: `agent_kernel/state.py`)**
```python
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class PlanStep(BaseModel):
    tool_name: str
    tool_input: Dict[str, Any]
    result: Optional[str] = None
    error: Optional[str] = None

class AgentState(BaseModel):
    raw_prompt: str
    user_id: str
    intent: Optional[str] = None
    plan: List[PlanStep] = []
    scratchpad: str = ""
    final_response: Optional[str] = None
```

#### **3. The "Toolbelt": A Protocol-Driven Registry**
Tools are the discrete capabilities of the agent. They adhere to a strict protocol and are managed by a central registry, forming a "supergraph" of actions.

**(File: `agent_kernel/tools/_protocol.py`)**
```python
from typing import Protocol, Dict, Any

class Tool(Protocol):
    name: str
    description: str # For the LLM planner to understand the tool's purpose.
    
    def execute(self, user_id: str, **kwargs) -> Any:
        ...
```
The `ToolRegistry` in `agent_kernel/registry.py` will dynamically discover and load all available `Tool` implementations, making them available to the graph.

#### **4. The Graph: Nodes and Conditional Edges**
The agent's logic is defined in the computation graph (`agent_kernel/graph.py`), likely using a library like LangGraph.

-   **Nodes:** Functions in `agent_kernel/nodes/` that accept `AgentState` and return a dictionary with updated fields.
    -   **`route_intent`**: Classifies the `raw_prompt` into a registered `Intent`.
    -   **`create_plan`**: Generates a `List[PlanStep]` based on the intent.
    -   **`execute_tools`**: Invokes tools from the `ToolRegistry` according to the plan.
-   **Edges:** Define the control flow. For example, after `execute_tools`, an edge can check if the plan is complete. If yes, proceed to `format_response`; if a tool failed, it could loop back to `create_plan` to re-plan.

---

## 4. Phased Implementation Plan

### ✅ Milestone 1: The Curated Canon & The Journal
*   **Status:** COMPLETE
*   **Outcome:** A functional monolith PoC where a user can select a knowledge base ("Tradition") and interact with a basic RAG and Journaling system.

### ✅ Milestone 2: The Aware Synthesist
*   **Status:** COMPLETE
*   **Outcome:** The PoC can synthesize data from mocked external services to provide contextual meal suggestions and bi-weekly performance reviews. Structured journaling (Gratitude, Reflection) is implemented and fully functional with proper database persistence.

### ✅ Milestone 3: The Production-Ready Foundation
*   **Status:** COMPLETE ✨
*   **Outcome:** The PoC has been hardened with a robust, database-backed foundation, containerization, and a comprehensive local development environment.

### ✅ Milestone 4: The Hybrid Intelligence Engine
*   **Status:** COMPLETE ✨
*   **Outcome:** A stable, production-ready application with a hybrid search system combining curated knowledge with real-time user journal entries. The system includes an out-of-band ingestion pipeline for "tradition" knowledge bases.
*   **Key Systems:**
    *   **✅ Vector Store:** Qdrant is fully integrated for all vector search.
    *   **✅ Real-time Indexing:** Journal entries are automatically indexed via a Celery-based task queue.
    *   **✅ Hybrid Search:** GraphQL API exposes a `semanticSearch` query for combined knowledge and journal retrieval.
    *   **✅ GCS Ingestion Pipeline:** A secure webhook, Celery task, and emulated GCS client are in place for out-of-band document processing.
    *   **✅ Containerized Environment:** The entire system (API, database, vector store, task queue) is managed via `docker-compose` for reliable, one-command startup.

---

## 5. Next Evolution: The AutoGen-Powered Agent Kernel

The next evolution of the Agent Service moves beyond a single planner to a collaborative **society of agents**, orchestrated by a framework like Microsoft's AutoGen. This allows for parallelized, specialized data retrieval and complex, stateful conversations. This architecture provides the foundation for true generative performance engineering.

The core workflow is as follows:

```
User Query ──> [Intent Filter] ──> [Query Decomposer] ──> [Multi-Agent Swarm] ──> [Synthesizer] ──> Final Response
```

### Phase 1: Intent Filtering & Query Decomposition

-   **Intent Filter:** A lightweight router that first classifies the user's request. Is it a simple Q&A, a complex data retrieval task, or an action-oriented command? The output determines which master agent (or "GroupChatManager" in AutoGen terms) will handle the request.
-   **Query Decomposer Agent:** For complex queries, this specialized agent's sole job is to break down the user's natural language request into a set of parallelizable sub-queries.
    -   **Example:** "What Stoic advice relates to the anxiety I mentioned in my journal this week?"
    -   **Decomposed Sub-Queries:**
        1.  "Retrieve journal entries from the last 7 days tagged with 'anxiety'."
        2.  "Perform a semantic search in the 'stoic-canon' knowledge base for concepts related to 'anxiety'."

### Phase 2: The Multi-Agent Swarm

This is a "GroupChat" of specialist agents, each an expert in a specific domain corresponding to our microservices. They receive the sub-queries and work in parallel.

-   **Specialist Agents:**
    -   `JournalAgent`: An expert on the Journaling service. It knows how to query for entries by date, mood, and content.
    -   `KnowledgeAgent`: An expert at performing advanced RAG against the Qdrant knowledge collections.
    -   `PracticeAgent`: An expert on the Practices service, capable of finding and modifying workout programs.
-   **Strategic Refinement:** Each agent can apply its own sub-strategies to its query. For instance, the `KnowledgeAgent` could use a "step-back" prompting technique to generalize a user's specific query into a broader, more fundamental question, leading to more relevant high-level concepts from the knowledge base.

### The "Magic" `@tool` Decorator

To make the agent swarm extensible, we introduce a powerful decorator. This is the key to velocity.

-   **Concept:** Any existing function in our codebase (e.g., a GraphQL resolver, a service-layer function) can be instantly converted into a tool for the agents.
-   **Implementation Sketch:**
    ```python
    # In a central tool registry
    from agent_kernel.registry import tool

    # In the journaling service code
    @tool
    def get_journal_entries_by_date(user_id: str, start_date: date, end_date: date) -> List[JournalEntry]:
        """Fetches all journal entries for a user between two dates."""
        # ... existing implementation ...
    ```
-   **How it Works:** The `@tool` decorator uses Python's introspection capabilities to automatically:
    1.  Read the function name (`get_journal_entries_by_date`).
    2.  Read the docstring for its `description`.
    3.  Analyze the type-hinted signature to build a structured schema (e.g., an OpenAI Function-Calling JSON schema).
    4.  Register this fully-defined tool in a central registry, making it immediately available to the planning agents.

### Phase 3: Synthesis

A final `SynthesizerAgent` (or the initial GroupChatManager) is responsible for collecting the structured outputs from all the specialist agents and weaving them into a single, coherent, and insightful response for the user.

---

## The Knowledge Store: Evolving to a Graph RAG System

This is a critical architectural decision. Sticking with Postgres + Qdrant is viable, but introducing a Knowledge Graph like Memgraph unlocks a new paradigm.

| Aspect | Current Stack (Postgres + Qdrant) | Future Stack (Postgres + Qdrant + Memgraph) |
| :--- | :--- | :--- |
| **Core Strength** | **Best-of-breed services.** Each DB is optimized for its purpose: relational integrity (Postgres) and vector search speed (Qdrant). | **Explicit Relationships.** The graph makes the connections *between* data points a first-class citizen. |
| **How it Works** | Connections are **inferred at query time**. We find a journal entry in Postgres, then use its text to find similar vectors in Qdrant. | Connections are **stored and directly queryable**. `(User)-[:WROTE]->(Journal)-[:MENTIONS]->(Concept)` |
| **Example Query** | "Find stoic advice for anxiety." <br/> *Requires two separate queries orchestrated by application logic.* | "Find `(Advice)` nodes connected to the `(Stoic)` tradition that are also connected to the `(Concept)` 'anxiety', which was mentioned in a `(Journal)` entry you wrote last week." <br/> *This is a single, elegant graph query.* |
| **Pros** | - Simpler stack to manage <br/> - Clear separation of concerns <br/> - Mature and highly scalable components | - Unlocks deep, multi-hop queries <br/> - A natural "brain" for an agent to traverse <br/> - Enables powerful analytics and recommendations |
| **Cons** | - Complex queries require app-level orchestration <br/> - Relationships are not explicit or persistent | - Adds another database to deploy and manage <br/> - Requires a data synchronization pipeline (e.g., CDC) to keep the graph up-to-date with Postgres. |

### Recommendation: A Phased Evolution

The current Postgres + Qdrant stack is the **perfect foundation**. The next revolutionary step is not to *replace* it, but to **augment it with Memgraph as a synthesizing layer**.

1.  **Continue with the Current Stack:** It is robust and solves the immediate problems of storage and retrieval.
2.  **Introduce Memgraph as a Projection:** In a future milestone, we'll build a pipeline (e.g., using Celery tasks or a Change-Data-Capture tool like Debezium) that **projects** data from our source-of-truth services (Postgres) into Memgraph.
    -   A new `User` in Postgres creates a `(User)` node in Memgraph.
    -   A new `JournalEntry` creates a `(Journal)` node and a `[:WROTE]` edge.
    -   An NLP process extracts key concepts from the journal entry, creating `(Concept)` nodes and `[:MENTIONS]` edges.

This approach gives us the best of both worlds: the reliability of our current stack and the profound analytical power of a Knowledge Graph, providing the perfect foundation for the highly intelligent, multi-agent system we've envisioned.