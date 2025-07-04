import {
  Avatar,
  AvatarBadge,
  AvatarFallbackText,
  AvatarImage,
} from "@/components/ui/avatar"
import { Box } from "@/components/ui/box"
import { Heading } from "@/components/ui/heading"
import { HStack } from "@/components/ui/hstack"
import { ChevronRightIcon, Icon, MenuIcon } from "@/components/ui/icon"
import { Input, InputField } from "@/components/ui/input"
import { Pressable } from "@/components/ui/pressable"
import { SafeAreaView } from "@/components/ui/safe-area-view"
import { ScrollView } from "@/components/ui/scroll-view"
import { Text } from "@/components/ui/text"
import { VStack } from "@/components/ui/vstack"
import { useNavigation } from '@react-navigation/native'
import { useRouter } from 'expo-router'
import { Heart, Lightbulb, PenTool } from "lucide-react-native"
import { useState } from 'react'

type JournalType = 'all' | 'gratitude' | 'reflection' | 'freeform'

interface JournalEntry {
  id: string
  type: JournalType
  title: string
  content: string
  date: string
}

// Mock data for now
const mockEntries: JournalEntry[] = [
  {
    id: '1',
    type: 'gratitude',
    title: 'Grateful for today',
    content: 'I am grateful for the beautiful weather and the opportunity to spend time with family...',
    date: '2024-01-15',
  },
  {
    id: '2',
    type: 'reflection',
    title: 'Daily reflection',
    content: 'Today was productive. I accomplished my main goals and learned something new...',
    date: '2024-01-14',
  },
  {
    id: '3',
    type: 'freeform',
    title: 'Random thoughts',
    content: 'Sometimes I wonder about the nature of consciousness and how we perceive reality...',
    date: '2024-01-13',
  },
  {
    id: '4',
    type: 'gratitude',
    title: 'Thankful for health',
    content: 'I am grateful for my health and the ability to move freely...',
    date: '2024-01-12',
  },
]

const typeOptions: { value: JournalType; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'gratitude', label: 'Gratitude' },
  { value: 'reflection', label: 'Reflection' },
  { value: 'freeform', label: 'Freeform' },
]

function AppBar() {
  const router = useRouter()
  const navigation = useNavigation()

  const handleMenuPress = () => {
    (navigation as any).openDrawer()
  }

  const handleProfilePress = () => {
    router.push('/(app)/profile')
  }

  return (
    <HStack
      className="py-6 px-4 border-b border-border-300 bg-background-0 items-center justify-between"
      space="md"
    >
      <HStack className="items-center" space="sm">
        <Pressable onPress={handleMenuPress}>
          <Icon as={MenuIcon} />
        </Pressable>
        <Text className="text-xl">Archive</Text>
      </HStack>
      
      <Pressable onPress={handleProfilePress}>
        <Avatar className="h-9 w-9">
          <AvatarFallbackText>U</AvatarFallbackText>
          <AvatarImage source={{ uri: "https://i.pravatar.cc/300" }} />
          <AvatarBadge />
        </Avatar>
      </Pressable>
    </HStack>
  )
}

export default function ArchiveScreen() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedType, setSelectedType] = useState<JournalType>('all')

  const filteredEntries = mockEntries.filter(entry => {
    const matchesSearch = entry.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         entry.content.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesType = selectedType === 'all' || entry.type === selectedType
    return matchesSearch && matchesType
  })

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    })
  }

  const getTypeIcon = (type: JournalType) => {
    switch (type) {
      case 'gratitude':
        return Heart
      case 'reflection':
        return Lightbulb
      case 'freeform':
        return PenTool
      default:
        return Heart
    }
  }

  const getTypeColor = (type: JournalType) => {
    switch (type) {
      case 'gratitude':
        return 'bg-blue-50 dark:bg-blue-950'
      case 'reflection':
        return 'bg-indigo-50 dark:bg-indigo-950'
      case 'freeform':
        return 'bg-purple-50 dark:bg-purple-950'
      default:
        return 'bg-gray-50 dark:bg-gray-950'
    }
  }

  const getTypeIconColor = (type: JournalType) => {
    switch (type) {
      case 'gratitude':
        return 'text-blue-600 dark:text-blue-400'
      case 'reflection':
        return 'text-indigo-600 dark:text-indigo-400'
      case 'freeform':
        return 'text-purple-600 dark:text-purple-400'
      default:
        return 'text-gray-600 dark:text-gray-400'
    }
  }

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar />
        
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

          {/* Journal Entries */}
          <VStack className="px-6 py-6" space="md">
            {filteredEntries.length === 0 ? (
              <VStack className="items-center justify-center py-12" space="md">
                <Icon as={PenTool} size="xl" className="text-typography-400 dark:text-gray-500" />
                <VStack className="items-center" space="xs">
                  <Text className="text-lg font-semibold text-typography-900 dark:text-white">
                    No entries found
                  </Text>
                  <Text className="text-base text-typography-600 dark:text-gray-200 text-center">
                    Try adjusting your search or filter criteria
                  </Text>
                </VStack>
              </VStack>
            ) : (
              filteredEntries.map((entry) => (
                <Pressable key={entry.id} className="mb-4">
                  <Box 
                    className={`p-6 min-h-[120px] rounded-lg ${getTypeColor(entry.type)} border border-border-200 dark:border-border-700`}
                  >
                    {/* Card Header */}
                    <HStack className="justify-between items-center mb-4">
                      <HStack className="items-center" space="sm">
                        <Icon 
                          as={getTypeIcon(entry.type)}
                          size="md"
                          className={getTypeIconColor(entry.type)}
                        />
                        <Text className="text-sm font-medium text-typography-700 dark:text-gray-300">
                          {entry.type.charAt(0).toUpperCase() + entry.type.slice(1)}
                        </Text>
                      </HStack>
                      <Text className="text-sm text-typography-500 dark:text-gray-400">
                        {formatDate(entry.date)}
                      </Text>
                    </HStack>
                    
                    {/* Card Title */}
                    <Text className="text-lg font-semibold text-typography-900 dark:text-white mb-2">
                      {entry.title}
                    </Text>
                    
                    {/* Card Description */}
                    <Text className="text-base text-typography-600 dark:text-gray-200 leading-6 flex-1 mb-4">
                      {entry.content}
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
        </ScrollView>
      </VStack>
    </SafeAreaView>
  )
} 