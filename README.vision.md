# 🧠 The Cyborg Coach: A Roadmap for Hyper-Personalized Performance

## 1. The Vision: From AI Coach to Digital Twin

The current PoC is an *AI Coach*. It's powerful, but it's still external. The next evolution is to create a **Cyborg Coach**—a symbiotic system that fuses trusted, external wisdom with a user's own internal, subjective experience.

This system won't just answer questions; it will become a digital twin of the user's performance journey. It will understand their goals, learn their preferences from their history, process their reflections from their journal, and synthesize it all with world-class knowledge bases (`Traditions`).

The ultimate goal is to create a generative performance engine. A user shouldn't just ask "What should I eat?"; they should be able to ask, "Generate a 7-day meal plan, in the style of my coach's notes, that helps me get conditioned for combat sports, avoids shellfish, and costs less than $15 a day." This is a generative, goal-oriented, and hyper-personalized system.

---

## 2. Phased Implementation Plan

This plan is broken into distinct, demo-able milestones. Each milestone delivers a tangible leap in user value and gets us closer to the full vision.

### ✅ **Milestone 1: The Curated Canon & The Journal**
*   **Goal:** Establish the foundation of user-specific knowledge and subjective experience capture.
*   **Demo Target:** A user can select a "Tradition" (e.g., "Stoic Fitness", "Paleo Performance") which grounds the AI's personality and advice. They can write and save a journal entry, which is then visible in their history.

*   **TDD Roadmap:**
    *   [ ] **Task 1.1 (Data):** Create subdirectories in `/pdfs` for different "traditions" (e.g., `/pdfs/canon-paleo`, `/pdfs/canon-keto`). Pre-load with 1-2 documents each.
    *   [ ] **Task 1.2 (Engine):** Modify `build_knowledge_base` in `src/data_processing.py` to be parameterized, building stores into tradition-specific subdirectories (e.g., `data/paleo/vectorstore`).
    *   [ ] **Task 1.3 (Engine):** Modify the `CoachingEngine` to be initialized with a specific `tradition`, loading from the correct data path.
      - CONSTRAINT: Abstract the `Tradition` here; we want this to be "injectable"/fetchable from a database.
    *   [ ] **Task 1.4 (API):** Update the `ask` query to take a `tradition` argument, which will require a mechanism to dynamically load the correct engine instance (or re-initialize it). A simple dictionary mapping traditions to engine instances would suffice for the PoC.
      - CONSTRAINT: Similar to above; ensure an interface abstraction.
    *   [ ] **Task 1.5 (API):** Create `saveJournalEntry` and `getJournalEntries` mutations (takes `userId` and `text`). For the PoC, this can save to a simple `journal_entries.json` file.
      - CONSTRAINT: Similar to above. Let's create `repository` layers to handle data writes; we'll then wrap these in passthrough services, which we'll use in the resolvers.
    *   [ ] **Task 1.6 (UI):** Add a dropdown in the Streamlit sidebar to select the active "Tradition." All subsequent `ask` calls from the UI will use this selection.
    *   [ ] **Task 1.7 (UI):** Add a "My Journal" section to the UI with a text area and a "Save Entry" button. Display past entries for the current user below the text area.
      - CONSTRAINT: similar; repo pattern should make it easy to use local files for this for now but easily swap for a DB

### ✅ **Milestone 2: The Goal-Oriented Coach**
*   **Goal:** Make the AI aware of the user's specific objectives and enable basic, goal-oriented recommendations.
*   **Demo Target:** A user can define a simple goal profile (e.g., "gain muscle," "3500 calories/day"). They can then ask "What should I eat for dinner?" and get a reasonable, context-aware suggestion based on their goal and trusted "Tradition."

*   **TDD Roadmap:**
    *   [ ] **Task 2.1 (API):** Define a `UserProfile` GraphQL type (goals, calorie targets, macros, free-text objective).
    *   [ ] **Task 2.2 (API):** Create `saveUserProfile` and `getUserProfile` mutations/queries. Store this in a `user_profiles.json` file for the PoC.
    *   [ ] **Task 2.3 (API):** Create a `getMealSuggestion` query. This query will orchestrate the magic:
        *   It takes `userId` and `meal_type` (e.g., "dinner").
        *   It fetches the user's profile.
        *   It constructs a detailed, structured prompt for the RAG chain (e.g., "Based on the context, suggest a dinner for a user whose goal is to 'gain muscle'...").
        *   It calls the appropriate engine's `ask` method with the detailed prompt.
    *   [ ] **Task 2.4 (UI):** Create a "My Profile" section in the Streamlit app where a user can input and save their goals.
    *   [ ] **Task 2.5 (UI):** Add a "What Should I Eat?" button/feature that triggers the new `getMealSuggestion` query and displays the structured recommendation.

### ✅ **Milestone 3: The Integrated Cyborg (Connecting External Data)**
*   **Goal:** Begin the true synthesis by integrating external, objective data with the user's subjective journal and trusted knowledge.
*   **Demo Target:** The "What should I eat?" recommendation now cross-references the user's (mocked) food history, actively avoiding disliked foods and suggesting favorites. The AI can now answer questions like, "Based on my journal, what should I eat for better energy?"

*   **TDD Roadmap:**
    *   [ ] **Task 3.1 (Engine):** The journal entries for a user should be included as part of the context for the RAG chain. This may involve creating a simple retriever for the user's journal entries and adding it to the `MergerRetriever`.
    *   [ ] **Task 3.2 (API):** Create a mocked "Meals Service" client in a new `src/external/meals_client.py`. It will have a function like `get_user_nutritional_history(user_id)` that returns a hardcoded list of favorite and disliked foods.
    *   [ ] **Task 3.3 (API):** Update the `getMealSuggestion` query logic to call the new `meals_client`.
    *   [ ] **Task 3.4 (API):** Augment the RAG prompt for `getMealSuggestion` to include this new context (e.g., "...The user's favorite foods are 'steak' and 'eggs'. They dislike 'broccoli'.").
    *   [ ] **Task 3.5 (TDD):** Write an integration test for the `getMealSuggestion` query that mocks the `meals_client` and confirms the prompt includes the nutritional history.

---
## 3. Packaging the Demo

Before beginning the next phase, we must package the current work for a clean, impressive demo.

*   **Goal:** A one-command launch that brings up the UI and API, ready for interaction.
*   **TDD Roadmap:**
    *   [ ] **Task 1:** Pre-load the `./pdfs` directory with 2-3 canonical nutrition/fitness texts for a compelling default "Tradition."
    *   [ ] **Task 2:** Create a `docker-compose.yml` file to run the API server and the Streamlit UI as separate services.
    *   [ ] **Task 3:** Add a `build` step in the `docker-compose.yml` for the API service that runs the `scripts/build_knowledge_base.py` script, ensuring the data is ready before the server starts.
    *   [ ] **Task 4:** Update the main `README.md` with simple, clear instructions: `git clone ...`, `docker-compose up`, and a link to the Streamlit UI. 