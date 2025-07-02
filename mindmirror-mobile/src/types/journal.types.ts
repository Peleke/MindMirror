export interface JournalEntry {
  id: string
  createdAt: string
  updatedAt: string
  userId: string
  type: JournalEntryType
  content: JournalContent
}

export type JournalEntryType = 'gratitude' | 'reflection' | 'freeform'

export interface GratitudeContent {
  gratefulFor: string[]
  excitedAbout: string[]
  focus: string
  affirmation: string
  mood: string
}

export interface ReflectionContent {
  wins: string[]
  improvements: string[]
  mood: string
}

export interface FreeformContent {
  content: string
}

export type JournalContent = GratitudeContent | ReflectionContent | FreeformContent

export interface CreateJournalEntryInput {
  type: JournalEntryType
  content: JournalContent
}

export interface JournalEntryExistsResponse {
  exists: boolean
}

export interface JournalEntriesResponse {
  entries: JournalEntry[]
  total: number
  hasMore: boolean
}

export interface JournalFilters {
  type?: JournalEntryType
  startDate?: string
  endDate?: string
  search?: string
}

export interface JournalPagination {
  page: number
  limit: number
} 