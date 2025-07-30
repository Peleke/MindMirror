import { Box } from "@/components/ui/box"
import { Heading } from "@/components/ui/heading"
import { HStack } from "@/components/ui/hstack"
import { ChevronRightIcon, Icon } from "@/components/ui/icon"
import { Input, InputField } from "@/components/ui/input"
import { Pressable } from "@/components/ui/pressable"
import { SafeAreaView } from "@/components/ui/safe-area-view"
import { ScrollView } from "@/components/ui/scroll-view"
import { Text } from "@/components/ui/text"
import { VStack } from "@/components/ui/vstack"
import { GET_JOURNAL_ENTRIES } from '@/services/api/queries'
import { useQuery } from '@apollo/client'
import { useRouter } from 'expo-router'
import { Heart, Lightbulb, PenTool } from "lucide-react-native"
import { useState, useMemo } from 'react'
import { AppBar } from '@/components/common/AppBar'

type JournalType = 'all' | 'gratitude' | 'reflection' | 'freeform'

// TypeScript Interfaces Matching GraphQL Schema
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

const typeOptions: { value: JournalType; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'gratitude', label: 'Gratitude' },
  { value: 'reflection', label: 'Reflection' },
  { value: 'freeform', label: 'Freeform' },
]



export default function ArchiveScreen() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedType, setSelectedType] = useState<JournalType>('all')

  const { data, loading, error, refetch } = useQuery(GET_JOURNAL_ENTRIES, {
    errorPolicy: 'all',
  })

  const getEntryType = (entry: JournalEntry): string => {
    switch (entry.__typename) {
      case 'GratitudeJournalEntry': return 'gratitude'
      case 'ReflectionJournalEntry': return 'reflection'
      case 'FreeformJournalEntry': return 'freeform'
      default: return 'unknown'
    }
  }

  const filteredEntries = useMemo(() => {
    if (!data?.journalEntries) return []
    
    let entries: JournalEntry[] = [...data.journalEntries]
    
    // Filter by type
    if (selectedType !== 'all') {
      entries = entries.filter(entry => getEntryType(entry) === selectedType)
    }
    
    // Search in content
    if (searchQuery) {
      const searchLower = searchQuery.toLowerCase()
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
  }, [data?.journalEntries, selectedType, searchQuery])

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    })
  }

  const getTypeIcon = (entry: JournalEntry) => {
    switch (entry.__typename) {
      case 'GratitudeJournalEntry':
        return Heart
      case 'ReflectionJournalEntry':
        return Lightbulb
      case 'FreeformJournalEntry':
        return PenTool
      default:
        return Heart
    }
  }

  const getTypeColor = (entry: JournalEntry) => {
    switch (entry.__typename) {
      case 'GratitudeJournalEntry':
        return 'bg-blue-50 dark:bg-blue-950'
      case 'ReflectionJournalEntry':
        return 'bg-indigo-50 dark:bg-indigo-950'
      case 'FreeformJournalEntry':
        return 'bg-purple-50 dark:bg-purple-950'
      default:
        return 'bg-gray-50 dark:bg-gray-950'
    }
  }

  const getTypeIconColor = (entry: JournalEntry) => {
    switch (entry.__typename) {
      case 'GratitudeJournalEntry':
        return 'text-blue-600 dark:text-blue-400'
      case 'ReflectionJournalEntry':
        return 'text-indigo-600 dark:text-indigo-400'
      case 'FreeformJournalEntry':
        return 'text-purple-600 dark:text-purple-400'
      default:
        return 'text-gray-600 dark:text-gray-400'
    }
  }

  const getEntryTitle = (entry: JournalEntry): string => {
    switch (entry.__typename) {
      case 'GratitudeJournalEntry':
        return `Grateful for ${entry.payload.gratefulFor[0] || 'today'}`
      case 'ReflectionJournalEntry':
        return `Reflection on ${entry.payload.wins[0] || 'today'}`
      case 'FreeformJournalEntry':
        return entry.content.slice(0, 50) + (entry.content.length > 50 ? '...' : '')
      default:
        return 'Journal Entry'
    }
  }

  const getEntryContent = (entry: JournalEntry): string => {
    switch (entry.__typename) {
      case 'GratitudeJournalEntry':
        const gratefulItems = entry.payload.gratefulFor.slice(0, 2).join(', ')
        return `Grateful for: ${gratefulItems}${entry.payload.gratefulFor.length > 2 ? '...' : ''}`
      case 'ReflectionJournalEntry':
        const wins = entry.payload.wins.slice(0, 2).join(', ')
        return `Wins: ${wins}${entry.payload.wins.length > 2 ? '...' : ''}`
      case 'FreeformJournalEntry':
        return entry.content.slice(0, 150) + (entry.content.length > 150 ? '...' : '')
      default:
        return 'Journal Entry'
    }
  }

  const handleEntryPress = (entry: JournalEntry) => {
    const entryType = entry.__typename.replace('JournalEntry', '').toLowerCase();
    router.push(`/journal/detail/${entryType}/${entry.id}`);
  };

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title="Archive" />
        
        <ScrollView
          showsVerticalScrollIndicator={false}
          className="flex-1"
        >
          {/* Search Section */}
          <VStack className="px-6 py-6" space="md">
            <VStack space="xs">
              <Heading size="lg" className="font-roboto text-typography-900 dark:text-white">
                Journal Archive
              </Heading>
              <Text className="text-typography-600 dark:text-gray-200">
                Search and filter your past entries
              </Text>
            </VStack>
            
            {/* Search Bar */}
            <Input className="bg-background-50 dark:bg-background-100">
              <InputField
                placeholder="Search journal entries..."
                value={searchQuery}
                onChangeText={setSearchQuery}
              />
            </Input>

            {/* Type Filter */}
            <ScrollView 
              horizontal 
              showsHorizontalScrollIndicator={false}
              className="flex-row"
            >
              {typeOptions.map((option) => (
                <Pressable
                  key={option.value}
                  onPress={() => setSelectedType(option.value)}
                  className={`px-4 py-2 rounded-full mr-3 border ${
                    selectedType === option.value
                      ? 'bg-primary-600 border-primary-600'
                      : 'bg-background-50 dark:bg-background-100 border-border-200 dark:border-border-700'
                  }`}
                >
                  <Text className={`text-sm font-medium ${
                    selectedType === option.value
                      ? 'text-white'
                      : 'text-typography-600 dark:text-gray-300'
                  }`}>
                    {option.label}
                  </Text>
                </Pressable>
              ))}
            </ScrollView>
          </VStack>

          {/* Divider */}
          <Box className="h-px bg-border-200 dark:bg-border-700 mx-6" />

          {/* Loading State */}
          {loading && (
            <VStack className="px-6 py-6" space="md">
              <VStack className="items-center justify-center py-12" space="md">
                <Icon as={PenTool} size="xl" className="text-typography-400 dark:text-gray-500" />
                <Text className="text-base text-typography-600 dark:text-gray-200 text-center">
                  Loading journal entries...
                </Text>
              </VStack>
            </VStack>
          )}

          {/* Error State */}
          {error && (
            <VStack className="px-6 py-6" space="md">
              <VStack className="items-center justify-center py-12" space="md">
                <Icon as={PenTool} size="xl" className="text-red-500" />
                <VStack className="items-center" space="xs">
                  <Text className="text-lg font-semibold text-red-600 dark:text-red-400">
                    Failed to load entries
                  </Text>
                  <Text className="text-base text-typography-600 dark:text-gray-200 text-center">
                    Please check your connection and try again
                  </Text>
                </VStack>
              </VStack>
            </VStack>
          )}

          {/* Journal Entries */}
          {!loading && !error && (
          <VStack className="px-6 py-6" space="md">
            {filteredEntries.length === 0 ? (
              <VStack className="items-center justify-center py-12" space="md">
                <Icon as={PenTool} size="xl" className="text-typography-400 dark:text-gray-500" />
                <VStack className="items-center" space="xs">
                  <Text className="text-lg font-semibold text-typography-900 dark:text-white">
                    No entries found
                  </Text>
                  <Text className="text-base text-typography-600 dark:text-gray-200 text-center">
                      {searchQuery || selectedType !== 'all'
                        ? "Try adjusting your search or filter criteria"
                        : "You haven't written any journal entries yet. Start today!"
                      }
                  </Text>
                </VStack>
              </VStack>
            ) : (
              filteredEntries.map((entry) => (
                <Pressable 
                  key={entry.id} 
                  className="mb-4"
                  onPress={() => handleEntryPress(entry)}
                >
                  <Box 
                      className={`p-6 min-h-[120px] rounded-lg ${getTypeColor(entry)} border border-border-200 dark:border-border-700`}
                  >
                    {/* Card Header */}
                    <HStack className="justify-between items-center mb-4">
                      <HStack className="items-center" space="sm">
                        <Icon 
                            as={getTypeIcon(entry)}
                          size="md"
                            className={getTypeIconColor(entry)}
                        />
                        <Text className="text-sm font-medium text-typography-700 dark:text-gray-300">
                            {getEntryType(entry).charAt(0).toUpperCase() + getEntryType(entry).slice(1)}
                          </Text>
                        </HStack>
                        <Text className="text-sm text-typography-500 dark:text-gray-400">
                          {formatDate(entry.createdAt)}
                      </Text>
                    </HStack>
                    
                    {/* Card Title */}
                    <Text className="text-lg font-semibold text-typography-900 dark:text-white mb-2">
                        {getEntryTitle(entry)}
                    </Text>
                    
                    {/* Card Description */}
                    <Text className="text-base text-typography-600 dark:text-gray-200 leading-6 flex-1 mb-4">
                        {getEntryContent(entry)}
                    </Text>
                    
                    {/* Card Footer */}
                    <Box className="items-end">
                      <Icon 
                        as={ChevronRightIcon}
                        size="sm"
                        className="text-typography-400 dark:text-typography-500"
                      />
                    </Box>
                  </Box>
                </Pressable>
              ))
            )}
          </VStack>
          )}
        </ScrollView>
      </VStack>
    </SafeAreaView>
  )
} 