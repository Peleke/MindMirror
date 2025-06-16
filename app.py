import asyncio
import base64
import os
from datetime import datetime

import streamlit as st

from src.api_client import DEMO_USER_ID, run_graphql_query

# --- GraphQL Queries and Mutations ---
ASK_QUERY = """
    query Ask($query: String!, $tradition: String!) {
      ask(query: $query, tradition: $tradition)
    }
"""

GENERATE_REVIEW_MUTATION = """
    mutation GenerateReview($tradition: String!) {
      generateReview(tradition: $tradition) {
        keySuccess
        improvementArea
        journalPrompt
      }
    }
"""

UPLOAD_DOCUMENT_MUTATION = """
    mutation UploadDocument($fileName: String!, $content: Base64!, $tradition: String!) {
      uploadDocument(fileName: $fileName, content: $content, tradition: $tradition)
    }
"""

LIST_TRADITIONS_QUERY = """
    query ListTraditions {
      listTraditions
    }
"""

CREATE_FREEFORM_JOURNAL_ENTRY_MUTATION = """
    mutation CreateFreeformJournalEntry($input: FreeformEntryInput!) {
        createFreeformJournalEntry(input: $input) {
            id
        }
    }
"""

CREATE_GRATITUDE_JOURNAL_ENTRY_MUTATION = """
    mutation CreateGratitudeJournalEntry($input: GratitudeEntryInput!) {
        createGratitudeJournalEntry(input: $input) {
            id
        }
    }
"""

CREATE_REFLECTION_JOURNAL_ENTRY_MUTATION = """
    mutation CreateReflectionJournalEntry($input: ReflectionEntryInput!) {
        createReflectionJournalEntry(input: $input) {
            id
        }
    }
"""

GET_JOURNAL_ENTRIES_QUERY = """
    query GetJournalEntries {
        journalEntries {
            __typename
            ... on FreeformJournalEntry {
                id
                createdAt
                payload
            }
            ... on GratitudeJournalEntry {
                id
                createdAt
                gratitudePayload: payload {
                    gratefulFor
                    excitedAbout
                    focus
                    affirmation
                    mood
                }
            }
            ... on ReflectionJournalEntry {
                id
                createdAt
                reflectionPayload: payload {
                    wins
                    improvements
                    mood
                }
            }
        }
    }
"""

JOURNAL_ENTRY_EXISTS_QUERY = """
    query JournalEntryExistsToday($entryType: String!) {
        journalEntryExistsToday(entryType: $entryType)
    }
"""

GET_MEAL_SUGGESTION_QUERY = """
    query GetMealSuggestion($mealType: String!, $tradition: String!) {
      getMealSuggestion(mealType: $mealType, tradition: $tradition) {
        suggestion
      }
    }
"""


def main():
    """
    Main function to run the Streamlit UI as a pure API client.
    """
    st.title("🏋️‍♂️ Cyborg Coach - Your AI Performance Companion")

    # Show current user info and environment
    if os.getenv("I_AM_IN_A_DOCKER_CONTAINER"):
        st.sidebar.info(f"🐳 Docker Mode | Demo User: {DEMO_USER_ID}")
    else:
        st.sidebar.info(f"🖥️ Local Mode | Demo User: {DEMO_USER_ID}")

    # --- Sidebar ---
    with st.sidebar:
        st.header("Settings")

        # --- Tradition Selection ---
        try:
            traditions_result = asyncio.run(run_graphql_query(LIST_TRADITIONS_QUERY))
            if "errors" in traditions_result:
                st.error(
                    f"Failed to load traditions: {traditions_result['errors'][0]['message']}"
                )
                traditions = ["canon-default"]  # fallback
            else:
                traditions = traditions_result["data"]["listTraditions"]
                # Ensure traditions is not empty or None
                if not traditions:
                    traditions = ["canon-default"]
        except Exception as e:
            st.error(f"Network error loading traditions: {str(e)}")
            traditions = ["canon-default"]

        # Ensure traditions is a list and not empty
        if not isinstance(traditions, list) or len(traditions) == 0:
            traditions = ["canon-default"]

        # Set default if session state is not initialized
        if "tradition" not in st.session_state:
            st.session_state.tradition = (
                "canon-default" if "canon-default" in traditions else traditions[0]
            )

        st.selectbox(
            "Select Knowledge Base (Tradition):",
            options=traditions,
            key="tradition",  # Bind selection to session state
        )

        st.markdown("---")

        st.header("Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload new PDF or TXT files to the knowledge base.",
            type=["pdf", "txt"],
            accept_multiple_files=True,
        )
        if uploaded_files:
            for uploaded_file in uploaded_files:
                with st.spinner(f"Uploading {uploaded_file.name}..."):
                    try:
                        file_content = uploaded_file.getvalue()
                        encoded_content = base64.b64encode(file_content).decode("utf-8")
                        variables = {
                            "fileName": uploaded_file.name,
                            "content": encoded_content,
                            "tradition": st.session_state.tradition,
                        }
                        result = asyncio.run(
                            run_graphql_query(UPLOAD_DOCUMENT_MUTATION, variables)
                        )
                        if "errors" in result:
                            st.error(
                                f"Failed to upload {uploaded_file.name}: {result['errors'][0]['message']}"
                            )
                        else:
                            st.success(
                                f"✅ Successfully uploaded {uploaded_file.name}!"
                            )
                    except Exception as e:
                        st.error(f"Error uploading {uploaded_file.name}: {str(e)}")
            st.rerun()

        st.header("Actions")
        if st.button("Generate Bi-Weekly Review"):
            with st.spinner("Analyzing your progress..."):
                try:
                    variables = {"tradition": st.session_state.tradition}
                    result = asyncio.run(
                        run_graphql_query(GENERATE_REVIEW_MUTATION, variables)
                    )
                    if "errors" in result:
                        st.error(
                            f"Could not generate review: {result['errors'][0]['message']}"
                        )
                    else:
                        review = result["data"]["generateReview"]
                        st.session_state.review = review
                except Exception as e:
                    st.error(f"Error generating review: {str(e)}")

        st.markdown("---")
        st.header("Smart Actions")

        if st.button("Suggest My Next Meal"):
            with st.spinner("Thinking about your next meal..."):
                try:
                    # For PoC, let's just ask for dinner
                    variables = {
                        "mealType": "dinner",
                        "tradition": st.session_state.tradition,
                    }
                    result = asyncio.run(
                        run_graphql_query(GET_MEAL_SUGGESTION_QUERY, variables)
                    )

                    if "errors" in result:
                        st.error(
                            f"Could not generate meal suggestion: {result['errors'][0]['message']}"
                        )
                    else:
                        suggestion = result["data"]["getMealSuggestion"]["suggestion"]
                        st.session_state.meal_suggestion = suggestion
                except Exception as e:
                    st.error(f"Error generating meal suggestion: {str(e)}")

    # --- Main Content Area ---

    # Display meal suggestion if it exists
    if "meal_suggestion" in st.session_state:
        st.subheader("🍽️ Your Meal Suggestion")
        st.success(st.session_state.meal_suggestion)
        st.markdown("---")

    # Display the performance review if it exists in the session state
    if "review" in st.session_state:
        st.subheader("📊 Your Bi-Weekly Performance Review")
        review = st.session_state.review
        st.success(f"**Key Success:** {review['keySuccess']}")
        st.warning(f"**Area for Improvement:** {review['improvementArea']}")
        st.info(f"**Journal Prompt:** {review['journalPrompt']}")
        st.markdown("---")  # Visual separator

    # --- Daily Routine Section ---
    st.subheader("📝 Daily Routine")

    # Check for Gratitude Entry
    try:
        gratitude_exists = asyncio.run(
            run_graphql_query(JOURNAL_ENTRY_EXISTS_QUERY, {"entryType": "GRATITUDE"})
        )
        show_gratitude_form = not gratitude_exists.get("data", {}).get(
            "journalEntryExistsToday", True
        )
    except Exception as e:
        st.warning(f"Could not check gratitude entry status: {str(e)}")
        show_gratitude_form = True

    if show_gratitude_form:
        with st.expander("☀️ Morning Gratitude", expanded=True):
            with st.form("gratitude_form"):
                st.markdown("Start your day with intention.")
                g_grateful_input = st.text_input(
                    "I am grateful for... (3 items, comma-separated)",
                    placeholder="coffee, sunshine, friends",
                )
                g_excited_input = st.text_input(
                    "I am excited about... (3 items, comma-separated)",
                    placeholder="workout, meeting, weekend",
                )
                g_focus = st.text_input("My focus for today is...")
                g_affirmation = st.text_input("My affirmation is...")
                g_mood = st.text_input("My current mood is...")

                submitted = st.form_submit_button("Save Morning Entry")
                if submitted:
                    try:
                        g_grateful = [
                            item.strip()
                            for item in g_grateful_input.split(",")
                            if item.strip()
                        ]
                        g_excited = [
                            item.strip()
                            for item in g_excited_input.split(",")
                            if item.strip()
                        ]

                        if (
                            len(g_grateful) >= 3
                            and len(g_excited) >= 3
                            and g_focus
                            and g_affirmation
                        ):
                            variables = {
                                "input": {
                                    "gratefulFor": g_grateful[:3],  # Take first 3
                                    "excitedAbout": g_excited[:3],  # Take first 3
                                    "focus": g_focus,
                                    "affirmation": g_affirmation,
                                    "mood": g_mood or "neutral",
                                }
                            }
                            result = asyncio.run(
                                run_graphql_query(
                                    CREATE_GRATITUDE_JOURNAL_ENTRY_MUTATION, variables
                                )
                            )

                            if "errors" in result:
                                st.error(
                                    f"Failed to save entry: {result['errors'][0]['message']}"
                                )
                            else:
                                st.success("Gratitude entry saved!")
                                st.rerun()
                        else:
                            st.warning(
                                "Please fill out all fields (at least 3 items for grateful/excited)."
                            )
                    except Exception as e:
                        st.error(f"Error saving gratitude entry: {str(e)}")

    # Check for Reflection Entry
    try:
        reflection_exists = asyncio.run(
            run_graphql_query(JOURNAL_ENTRY_EXISTS_QUERY, {"entryType": "REFLECTION"})
        )
        show_reflection_form = not reflection_exists.get("data", {}).get(
            "journalEntryExistsToday", True
        )
    except Exception as e:
        st.warning(f"Could not check reflection entry status: {str(e)}")
        show_reflection_form = True

    if show_reflection_form:
        with st.expander("🌙 Evening Reflection", expanded=True):
            with st.form("reflection_form"):
                st.markdown("Reflect on your day.")
                r_wins_input = st.text_input(
                    "My wins today were... (3 items, comma-separated)",
                    placeholder="deployed feature, helped colleague, exercised",
                )
                r_improvements_input = st.text_input(
                    "I can improve on... (2 items, comma-separated)",
                    placeholder="time management, communication",
                )
                r_mood = st.text_input("My final mood is...")

                submitted = st.form_submit_button("Save Evening Entry")
                if submitted:
                    try:
                        r_wins = [
                            item.strip()
                            for item in r_wins_input.split(",")
                            if item.strip()
                        ]
                        r_improvements = [
                            item.strip()
                            for item in r_improvements_input.split(",")
                            if item.strip()
                        ]

                        if len(r_wins) >= 3 and len(r_improvements) >= 2:
                            variables = {
                                "input": {
                                    "wins": r_wins[:3],  # Take first 3
                                    "improvements": r_improvements[:2],  # Take first 2
                                    "mood": r_mood or "neutral",
                                }
                            }
                            result = asyncio.run(
                                run_graphql_query(
                                    CREATE_REFLECTION_JOURNAL_ENTRY_MUTATION, variables
                                )
                            )
                            if "errors" in result:
                                st.error(
                                    f"Failed to save entry: {result['errors'][0]['message']}"
                                )
                            else:
                                st.success("Reflection entry saved!")
                                st.rerun()
                        else:
                            st.warning(
                                "Please list at least 3 wins and 2 areas for improvement."
                            )
                    except Exception as e:
                        st.error(f"Error saving reflection entry: {str(e)}")

    st.markdown("---")

    # --- Journaling Section ---
    st.subheader("📖 My Journal")

    with st.expander("New Freeform Entry"):
        with st.form("freeform_journal_form"):
            journal_entry_content = st.text_area(
                "Write a new journal entry:", height=150
            )
            submitted = st.form_submit_button("Save Entry")

            if submitted:
                if journal_entry_content.strip():
                    with st.spinner("Saving entry..."):
                        try:
                            variables = {"input": {"content": journal_entry_content}}
                            result = asyncio.run(
                                run_graphql_query(
                                    CREATE_FREEFORM_JOURNAL_ENTRY_MUTATION, variables
                                )
                            )

                            if "errors" in result:
                                st.error(
                                    f"Failed to save entry: {result['errors'][0]['message']}"
                                )
                            else:
                                st.success("Journal entry saved!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error saving journal entry: {str(e)}")
                else:
                    st.warning("Please write something before saving.")

    # Display past journal entries
    with st.spinner("Loading journal entries..."):
        try:
            entries_result = asyncio.run(run_graphql_query(GET_JOURNAL_ENTRIES_QUERY))

            if "errors" in entries_result:
                st.error(
                    f"Could not load journal entries: {entries_result['errors'][0]['message']}"
                )
            else:
                entries = entries_result["data"]["journalEntries"]
                if entries:
                    st.write("### Your Past Entries")
                    sorted_entries = sorted(
                        entries, key=lambda x: x["createdAt"], reverse=True
                    )
                    for entry in sorted_entries:
                        entry_type = entry["__typename"]
                        created_at = datetime.fromisoformat(
                            entry["createdAt"]
                        ).strftime("%Y-%m-%d %H:%M")

                        if entry_type == "FreeformJournalEntry":
                            with st.expander(f"📓 Freeform Entry from {created_at}"):
                                st.write(entry["payload"])
                        elif entry_type == "GratitudeJournalEntry":
                            with st.expander(f"☀️ Gratitude Entry from {created_at}"):
                                payload = entry["gratitudePayload"]
                                st.subheader("Grateful For:")
                                for item in payload["gratefulFor"]:
                                    st.markdown(f"- {item}")
                                st.subheader("Excited About:")
                                for item in payload["excitedAbout"]:
                                    st.markdown(f"- {item}")
                                if payload.get("focus"):
                                    st.subheader("Focus:")
                                    st.markdown(payload["focus"])
                                if payload.get("affirmation"):
                                    st.subheader("Affirmation:")
                                    st.markdown(payload["affirmation"])
                        elif entry_type == "ReflectionJournalEntry":
                            with st.expander(f"🌙 Reflection Entry from {created_at}"):
                                payload = entry["reflectionPayload"]
                                st.subheader("Wins:")
                                for item in payload["wins"]:
                                    st.markdown(f"- {item}")
                                st.subheader("Improvements:")
                                for item in payload["improvements"]:
                                    st.markdown(f"- {item}")
                else:
                    st.info("You have no journal entries yet.")
        except Exception as e:
            st.error(f"Network error loading journal entries: {str(e)}")

    st.markdown("---")

    # --- Chat Interface ---
    st.subheader("🤖 Conversational AI Coach")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I am your AI Coach. Ask me anything about your documents or your performance.",
            }
        ]

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Ask a question..."):
        # Display user message in chat message container
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    variables = {
                        "query": prompt,
                        "tradition": st.session_state.tradition,
                    }
                    result = asyncio.run(run_graphql_query(ASK_QUERY, variables))

                    if "errors" in result:
                        response = f"Sorry, there was an error: {result['errors'][0]['message']}"
                    else:
                        response = result["data"]["ask"]

                    st.markdown(response)
                    # Add assistant response to chat history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response}
                    )
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.markdown(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )


if __name__ == "__main__":
    main()
