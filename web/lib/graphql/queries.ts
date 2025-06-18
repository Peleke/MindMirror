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

// Chat-related mutations
export const ASK_QUERY = gql`
  mutation Ask($input: AskInput!) {
    ask(input: $input) {
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