import { gql } from '@apollo/client'

// Tradition-related queries
export const LIST_TRADITIONS = gql`
  query ListTraditions {
    listTraditions
  }
`

// Journal entry queries
export const JOURNAL_ENTRY_EXISTS_TODAY = gql`
  query JournalEntryExistsToday($entryType: String!) {
    journalEntryExistsToday(entryType: $entryType)
  }
`

export const GET_JOURNAL_ENTRIES = gql`
  query GetJournalEntries {
    journalEntries {
      __typename
      ... on GratitudeJournalEntry {
        id
        createdAt
        payload {
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
        payload {
          wins
          improvements
          mood
        }
      }
      ... on FreeformJournalEntry {
        id
        createdAt
        content: payload
      }
    }
  }
`

// Chat-related query
export const ASK_QUERY = gql`
  query Ask($query: String!, $tradition: String!, $includeJournalContext: Boolean) {
    ask(query: $query, tradition: $tradition, includeJournalContext: $includeJournalContext)
  }
`

// Meal suggestion query
export const GET_MEAL_SUGGESTION = gql`
  query GetMealSuggestion($mealType: String!, $tradition: String!) {
    getMealSuggestion(mealType: $mealType, tradition: $tradition) {
      suggestion
      reasoning
    }
  }
`

// Journal summarization query
export const SUMMARIZE_JOURNALS_QUERY = gql`
  query SummarizeJournals {
    summarizeJournals {
      summary
      generatedAt
    }
  }
`