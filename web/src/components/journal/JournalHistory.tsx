'use client'

import { useState, useMemo } from 'react'
import { useQuery } from '@apollo/client'
import { GET_JOURNAL_ENTRIES } from '../../../lib/graphql/queries'
import { Calendar, Search, Filter, Heart, FileText, Lightbulb, ChevronDown, ChevronUp, Loader2, RefreshCw } from 'lucide-react'

// --- TypeScript Interfaces Matching GraphQL Schema ---

interface GratitudePayload {
  gratefulFor: string[]
  excitedAbout: string[]
  focus: string
  affirmation: string
  mood?: string | null
}

interface ReflectionPayload {
  wins: string[]
  improvements: string[]
  mood?: string | null
}

interface GratitudeJournalEntry {
  __typename: 'GratitudeJournalEntry'
  id: string
  createdAt: string
  payload: GratitudePayload
}

interface ReflectionJournalEntry {
  __typename: 'ReflectionJournalEntry'
  id: string
  createdAt: string
  payload: ReflectionPayload
}

interface FreeformJournalEntry {
  __typename: 'FreeformJournalEntry'
  id: string
  createdAt: string
  content: string
}

type JournalEntry = GratitudeJournalEntry | ReflectionJournalEntry | FreeformJournalEntry

// --- Component ---

export function JournalHistory() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedType, setSelectedType] = useState<string>('all')
  const [expandedEntries, setExpandedEntries] = useState<Set<string>>(new Set())

  const { data, loading, error, refetch } = useQuery(GET_JOURNAL_ENTRIES, {
    errorPolicy: 'all',
  })

  const getEntryType = (entry: JournalEntry) => {
    switch (entry.__typename) {
      case 'GratitudeJournalEntry': return 'Gratitude'
      case 'ReflectionJournalEntry': return 'Reflection'
      case 'FreeformJournalEntry': return 'Freeform'
    }
  }

  const filteredEntries = useMemo(() => {
    if (!data?.journalEntries) return []
    
    let entries: JournalEntry[] = [...data.journalEntries]
    
    // Filter by type
    if (selectedType !== 'all') {
      entries = entries.filter(entry => getEntryType(entry).toLowerCase() === selectedType)
    }
    
    // Search in content
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase()
      entries = entries.filter(entry => {
        let contentToSearch = ''
        if (entry.__typename === 'FreeformJournalEntry') {
          contentToSearch = entry.content
        } else {
          contentToSearch = JSON.stringify(entry.payload)
        }
        return contentToSearch.toLowerCase().includes(searchLower)
      })
    }
    
    return entries.slice().sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
  }, [data?.journalEntries, selectedType, searchTerm])

  const toggleExpanded = (entryId: string) => {
    setExpandedEntries(prev => {
      const newSet = new Set(prev)
      if (newSet.has(entryId)) {
        newSet.delete(entryId)
      } else {
        newSet.add(entryId)
      }
      return newSet
    })
  }

  const getTypeIcon = (entry: JournalEntry) => {
    switch (entry.__typename) {
      case 'GratitudeJournalEntry':
        return <Heart className="w-4 h-4 text-red-500" />
      case 'ReflectionJournalEntry':
        return <Lightbulb className="w-4 h-4 text-yellow-500" />
      case 'FreeformJournalEntry':
        return <FileText className="w-4 h-4 text-blue-500" />
      default:
        return <FileText className="w-4 h-4 text-gray-500" />
    }
  }

  const getTypeColor = (entry: JournalEntry) => {
    switch (entry.__typename) {
      case 'GratitudeJournalEntry':
        return 'bg-red-50 text-red-700 border-red-200'
      case 'ReflectionJournalEntry':
        return 'bg-yellow-50 text-yellow-700 border-yellow-200'
      case 'FreeformJournalEntry':
        return 'bg-blue-50 text-blue-700 border-blue-200'
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200'
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString([], { 
      weekday: 'long',
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    })
  }

  const renderList = (title: string, items: string[]) => {
    if (!items || items.length === 0) return null
    return (
      <div>
        <h4 className="font-semibold text-gray-900 mb-1">{title}:</h4>
        <ul className="list-disc list-inside text-gray-700 space-y-1">
          {items.map((item, i) => <li key={i}>{item}</li>)}
        </ul>
      </div>
    )
  }

  const renderContent = (entry: JournalEntry) => {
    const isExpanded = expandedEntries.has(entry.id)
    
    switch (entry.__typename) {
      case 'GratitudeJournalEntry':
        const { payload } = entry
        return (
          <div className="space-y-4">
            {renderList('Grateful For', payload.gratefulFor.slice(0, isExpanded ? undefined : 2))}
            {!isExpanded && payload.gratefulFor.length > 2 && (
              <p className="text-gray-500 text-sm">... and {payload.gratefulFor.length - 2} more</p>
            )}
            
            {isExpanded && (
              <>
                {renderList('Excited About', payload.excitedAbout)}
                {payload.focus && <div><h4 className="font-semibold text-gray-900 mb-1">Focus:</h4><p className="text-gray-700">{payload.focus}</p></div>}
                {payload.affirmation && <div><h4 className="font-semibold text-gray-900 mb-1">Affirmation:</h4><p className="text-gray-700 italic">"{payload.affirmation}"</p></div>}
                {payload.mood && <div><h4 className="font-semibold text-gray-900 mb-1">Mood:</h4><p className="text-gray-700">{payload.mood}</p></div>}
              </>
            )}
          </div>
        )
      
      case 'ReflectionJournalEntry':
        const { payload: reflectionPayload } = entry
        return (
          <div className="space-y-4">
            {renderList('Wins', reflectionPayload.wins.slice(0, isExpanded ? undefined : 2))}
            {!isExpanded && reflectionPayload.wins.length > 2 && (
              <p className="text-gray-500 text-sm">... and {reflectionPayload.wins.length - 2} more</p>
            )}

            {isExpanded && (
              <>
                {renderList('Improvements', reflectionPayload.improvements)}
                {reflectionPayload.mood && <div><h4 className="font-semibold text-gray-900 mb-1">Mood:</h4><p className="text-gray-700">{reflectionPayload.mood}</p></div>}
              </>
            )}
          </div>
        )
      
      case 'FreeformJournalEntry':
        const text = entry.content
        const truncatedText = isExpanded ? text : text.slice(0, 250) + (text.length > 250 ? '...' : '')
        return (
          <div>
            <p className="text-gray-700 whitespace-pre-wrap">{truncatedText}</p>
          </div>
        )
      
      default:
        return (
          <div>
            <p className="text-gray-700">Unsupported entry type.</p>
          </div>
        )
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <div className="flex items-center justify-center gap-3 mb-4">
          <Calendar className="w-8 h-8 text-purple-500" />
          <h1 className="text-3xl font-bold text-gray-900">Journal History</h1>
        </div>
        <p className="text-gray-600">
          Explore your past reflections and track your growth over time.
        </p>
      </div>

      <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm mb-6 sticky top-4 z-10">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="md:col-span-3 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search all entries..."
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 outline-none transition-all"
            />
          </div>
          <div className="md:col-span-2 relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border appearance-none border-gray-200 rounded-lg focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 outline-none transition-all"
            >
              <option value="all">All Types</option>
              <option value="gratitude">Gratitude</option>
              <option value="reflection">Reflection</option>
              <option value="freeform">Freeform</option>
            </select>
          </div>
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center p-8">
          <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
          <span className="ml-3 text-gray-600">Loading journal entries...</span>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
          <h3 className="font-semibold text-red-800 mb-2">Failed to Load Journal</h3>
          <p className="text-red-700 text-sm mb-4">There was a problem fetching your entries. Please check your connection and try again.</p>
          <p className="text-xs text-red-600 bg-red-100 p-2 rounded-md font-mono">{error.message}</p>
          <button 
            onClick={() => refetch()}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center justify-center gap-2 mx-auto"
          >
            <RefreshCw className="w-4 h-4" />
            Retry
          </button>
        </div>
      )}

      {!loading && !error && (
        <div className="space-y-6">
          {filteredEntries.length > 0 ? (
            filteredEntries.map(entry => (
              <div key={entry.id} className={`bg-white rounded-2xl p-6 border ${getTypeColor(entry)} shadow-sm`}>
                <div className="flex justify-between items-start">
                  <div>
                    <div className="flex items-center gap-3">
                      <span className={`p-1.5 rounded-full ${getTypeColor(entry)}`}>
                        {getTypeIcon(entry)}
                      </span>
                      <h3 className="text-lg font-semibold text-gray-900">{getEntryType(entry)}</h3>
                    </div>
                    <p className="text-sm text-gray-500 mt-1 ml-10">{formatDate(entry.createdAt)}</p>
                  </div>
                  <button onClick={() => toggleExpanded(entry.id)} className="p-2 text-gray-500 hover:bg-gray-100 rounded-full">
                    {expandedEntries.has(entry.id) ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                  </button>
                </div>
                <div className="mt-4 pl-10">
                  {renderContent(entry)}
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-16 px-6 bg-white rounded-2xl border border-gray-200">
              <h3 className="text-xl font-semibold text-gray-800">No Entries Found</h3>
              <p className="text-gray-500 mt-2">
                {searchTerm || selectedType !== 'all'
                  ? "Your search or filter didn't match any entries. Try something else!"
                  : "You haven't written any journal entries yet. Start today!"
                }
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
} 