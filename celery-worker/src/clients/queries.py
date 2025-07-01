# GraphQL queries for journal service

GET_JOURNAL_ENTRY_BY_ID = """
query GetJournalEntry($entryId: UUID!) {
    journalEntry(entryId: $entryId) {
        __typename
        id
        userId
        entryType
        createdAt
        modifiedAt
        ... on FreeformJournalEntry {
            content: payload
        }
        ... on GratitudeJournalEntry {
            payload {
                gratefulFor
                excitedAbout
                focus
                affirmation
                mood
            }
        }
        ... on ReflectionJournalEntry {
            payload {
                wins
                improvements
                mood
            }
        }
    }
}
"""

GET_JOURNAL_ENTRIES = """
query GetJournalEntries($limit: Int) {
    journalEntries(limit: $limit) {
        __typename
        id
        userId
        entryType
        createdAt
        modifiedAt
        ... on FreeformJournalEntry {
            content: payload
        }
        ... on GratitudeJournalEntry {
            payload {
                gratefulFor
                excitedAbout
                focus
                affirmation
                mood
            }
        }
        ... on ReflectionJournalEntry {
            payload {
                wins
                improvements
                mood
            }
        }
    }
}
"""

# Additional queries for future use
GET_JOURNAL_ENTRIES_BY_USER = """
query GetJournalEntriesByUser($userId: UUID!, $limit: Int) {
    journalEntries(userId: $userId, limit: $limit) {
        __typename
        id
        userId
        entryType
        createdAt
        modifiedAt
        ... on FreeformJournalEntry {
            content: payload
        }
        ... on GratitudeJournalEntry {
            payload {
                gratefulFor
                excitedAbout
                focus
                affirmation
                mood
            }
        }
        ... on ReflectionJournalEntry {
            payload {
                wins
                improvements
                mood
            }
        }
    }
}
"""

GET_JOURNAL_ENTRIES_BY_DATE_RANGE = """
query GetJournalEntriesByDateRange($startDate: DateTime!, $endDate: DateTime!, $limit: Int) {
    journalEntries(startDate: $startDate, endDate: $endDate, limit: $limit) {
        __typename
        id
        userId
        entryType
        createdAt
        modifiedAt
        ... on FreeformJournalEntry {
            content: payload
        }
        ... on GratitudeJournalEntry {
            payload {
                gratefulFor
                excitedAbout
                focus
                affirmation
                mood
            }
        }
        ... on ReflectionJournalEntry {
            payload {
                wins
                improvements
                mood
            }
        }
    }
}
"""
