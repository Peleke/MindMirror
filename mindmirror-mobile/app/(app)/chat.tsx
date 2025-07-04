import {
  Avatar,
  AvatarBadge,
  AvatarFallbackText,
  AvatarImage,
} from "@/components/ui/avatar"
import { Box } from "@/components/ui/box"
import { Button } from "@/components/ui/button"
import { HStack } from "@/components/ui/hstack"
import {
  Icon, MenuIcon,
} from "@/components/ui/icon"
import { Input, InputField } from "@/components/ui/input"
import { Pressable } from "@/components/ui/pressable"
import { SafeAreaView } from "@/components/ui/safe-area-view"
import { ScrollView } from "@/components/ui/scroll-view"
import { Text } from "@/components/ui/text"
import { VStack } from "@/components/ui/vstack"
import { LIST_TRADITIONS, ASK_QUERY } from '@/services/api/queries'
import { useQuery, useLazyQuery } from '@apollo/client'
import { useNavigation } from '@react-navigation/native'
import { useRouter } from 'expo-router'
import { Send } from "lucide-react-native"
import { useState, useRef, useEffect } from 'react'
import { Alert } from 'react-native'

interface Message {
  id: string
  text: string
  isUser: boolean
  timestamp: Date
}

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
        <Text className="text-xl">AI Chat</Text>
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

export default function ChatScreen() {
  const [selectedTradition, setSelectedTradition] = useState('canon-default')
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: `Hello! I'm your AI companion, here to chat with you about your journey, goals, and anything on your mind. I'm drawing from the ${selectedTradition} tradition to provide thoughtful guidance. What would you like to explore today?`,
      isUser: false,
      timestamp: new Date(),
    },
  ])
  const [inputText, setInputText] = useState('')
  const messagesEndRef = useRef<ScrollView>(null)

  // Fetch available traditions
  const { data: traditionsData } = useQuery(LIST_TRADITIONS, {
    errorPolicy: 'all',
  })

  const traditions = traditionsData?.listTraditions || []

  // Use lazy query for AI chat
  const [askQuery, { loading, error }] = useLazyQuery(ASK_QUERY, {
    onCompleted: (data) => {
      if (data?.ask) {
        const newMessage: Message = {
          id: Date.now().toString(),
          text: data.ask,
          isUser: false,
          timestamp: new Date(),
        }
        setMessages(prev => [...prev, newMessage])
      }
    },
    onError: (error) => {
      console.error('Chat error:', error)
      const errorMessage: Message = {
        id: Date.now().toString(),
        text: "I'm sorry, I encountered an error. Please try again.",
        isUser: false,
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMessage])
    }
  })

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    setTimeout(() => {
      messagesEndRef.current?.scrollToEnd({ animated: true })
    }, 100)
  }, [messages])

  const sendMessage = async () => {
    if (!inputText.trim() || loading) return

    const userMessageContent = inputText.trim()

    // Add user message to UI
    const userMessage: Message = {
      id: Date.now().toString(),
      text: userMessageContent,
      isUser: true,
      timestamp: new Date(),
    }
    
    const updatedMessages = [...messages, userMessage]
    setMessages(updatedMessages)
    setInputText('')

    // Construct the query with conversation history (similar to web app)
    const conversationHistory = updatedMessages.slice(-6).map(m => `${m.isUser ? 'user' : 'assistant'}: ${m.text}`).join('\n')
    const queryWithHistory = `CONVERSATION HISTORY:\n${conversationHistory}\n\nCURRENT QUERY: ${userMessageContent}`

    // Send to AI
    try {
      console.log('ChatScreen: selectedTradition =', selectedTradition)
      console.log('ChatScreen: About to call askQuery with variables:', {
        query: queryWithHistory,
        tradition: selectedTradition,
      })
      
      await askQuery({
        variables: {
          query: queryWithHistory,
          tradition: selectedTradition,
        }
      })
    } catch (err) {
      console.error('Error sending message:', err)
      Alert.alert('Error', 'Failed to send message')
    }
  }

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar />
        
        {/* Tradition Selector */}
        {traditions.length > 0 && (
          <Box className="px-4 py-2 bg-background-50 dark:bg-background-100 border-b border-border-200 dark:border-border-700">
            <HStack className="items-center justify-between">
              <Text className="text-sm text-typography-600 dark:text-gray-300">
                AI Tradition:
              </Text>
              <ScrollView 
                horizontal 
                showsHorizontalScrollIndicator={false}
                className="flex-row"
              >
                {traditions.map((tradition: string) => (
                  <Pressable
                    key={tradition}
                    onPress={() => setSelectedTradition(tradition)}
                    className={`px-3 py-1 rounded-full mr-2 border ${
                      selectedTradition === tradition
                        ? 'bg-primary-600 border-primary-600'
                        : 'bg-background-0 dark:bg-background-200 border-border-200 dark:border-border-700'
                    }`}
                  >
                    <Text className={`text-xs font-medium ${
                      selectedTradition === tradition
                        ? 'text-white'
                        : 'text-typography-600 dark:text-gray-300'
                    }`}>
                      {tradition}
                    </Text>
                  </Pressable>
                ))}
              </ScrollView>
            </HStack>
          </Box>
        )}

        {/* Messages Container */}
        <ScrollView
          ref={messagesEndRef}
          showsVerticalScrollIndicator={false}
          className="flex-1 px-4 py-4"
        >
          {messages.map((message) => (
            <Box
              key={message.id}
              className={`mb-4 p-4 rounded-lg max-w-[80%] ${
                message.isUser 
                  ? 'self-end bg-primary-600' 
                  : 'self-start bg-background-100 dark:bg-background-200'
              }`}
            >
              <Text className={`text-base leading-5 ${
                message.isUser 
                  ? 'text-white' 
                  : 'text-typography-900 dark:text-white'
              }`}>
                {message.text}
              </Text>
            </Box>
          ))}
          {loading && (
            <Box className="mb-4 p-4 rounded-lg max-w-[80%] self-start bg-background-100 dark:bg-background-200">
              <HStack className="items-center" space="sm">
                <Box className="w-2 h-2 bg-typography-400 dark:bg-gray-400 rounded-full animate-bounce" />
                <Box className="w-2 h-2 bg-typography-400 dark:bg-gray-400 rounded-full animate-bounce" />
                <Box className="w-2 h-2 bg-typography-400 dark:bg-gray-400 rounded-full animate-bounce" />
              </HStack>
            </Box>
          )}
        </ScrollView>

        {/* Input Container */}
        <Box className="p-4 border-t border-border-200 dark:border-border-700 bg-background-0">
          <HStack className="items-end" space="sm">
            <Input className="flex-1 bg-background-50 dark:bg-background-100 rounded-full">
              <InputField
                placeholder="Type your message..."
                value={inputText}
                onChangeText={setInputText}
                multiline
                maxLength={500}
                style={{ maxHeight: 100 }}
              />
            </Input>
            <Button
              onPress={sendMessage}
              disabled={!inputText.trim() || loading}
              className="rounded-full px-4 py-2"
            >
              <Icon as={Send} size="sm" className="text-white" />
            </Button>
          </HStack>
        </Box>
      </VStack>
    </SafeAreaView>
  )
} 