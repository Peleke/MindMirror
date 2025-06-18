import { gql } from '@apollo/client'

// Journal entry mutations
export const CREATE_GRATITUDE_JOURNAL_ENTRY = gql`
  mutation CreateGratitudeJournalEntry($input: GratitudeEntryInput!) {
    createGratitudeJournalEntry(input: $input) {
      id
      createdAt
    }
  }
`

export const CREATE_REFLECTION_JOURNAL_ENTRY = gql`
  mutation CreateReflectionJournalEntry($input: ReflectionEntryInput!) {
    createReflectionJournalEntry(input: $input) {
      id
      createdAt
    }
  }
`

export const CREATE_FREEFORM_JOURNAL_ENTRY = gql`
  mutation CreateFreeformJournalEntry($input: FreeformEntryInput!) {
    createFreeformJournalEntry(input: $input) {
      id
      createdAt
    }
  }
`

// Document upload mutation
export const UPLOAD_DOCUMENT = gql`
  mutation UploadDocument($fileName: String!, $content: String!, $tradition: String!) {
    uploadDocument(fileName: $fileName, content: $content, tradition: $tradition) {
      success
      message
    }
  }
`

// Review generation mutation
export const GENERATE_REVIEW = gql`
  mutation GenerateReview($tradition: String!) {
    generateReview(tradition: $tradition) {
      keySuccess
      improvementArea
      journalPrompt
    }
  }
` 