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
  query GetJournalEntries($limit: Int, $offset: Int) {
    journalEntries(limit: $limit, offset: $offset) {
      id
      type
      content
      createdAt
      metadata
    }
  }
`

// Chat-related queries
export const ASK_QUERY = gql`
  query Ask($query: String!, $tradition: String!) {
    ask(query: $query, tradition: $tradition) {
      response
      timestamp
    }
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