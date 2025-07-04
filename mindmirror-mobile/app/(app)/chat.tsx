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
import { LIST_TRADITIONS } from '@/services/api/queries'
import { useQuery } from '@apollo/client'
import { useNavigation } from '@react-navigation/native'
import { useRouter } from 'expo-router'
import { Send } from "lucide-react-native"
import { useState } from 'react'
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
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello! I\'m your AI assistant. How can I help you today?',
      isUser: false,
      timestamp: new Date(),
    },
  ])
  const [inputText, setInputText] = useState('')
  const [loading, setLoading] = useState(false)
  const [selectedTradition, setSelectedTradition] = useState('')

  // Fetch available traditions
  const { data: traditionsData } = useQuery(LIST_TRADITIONS, {
    errorPolicy: 'all',
  })

  const traditions = traditionsData?.listTraditions || []

  const sendMessage = async () => {
    if (!inputText.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      isUser: true,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInputText('')
    setLoading(true)

    try {
      // TODO: Implement actual AI chat with GraphQL mutation
      // For now, simulate AI response
      setTimeout(() => {
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: `I understand you said: "${inputText}". This is a placeholder response. The AI chat feature is coming soon!`,
          isUser: false,
          timestamp: new Date(),
        }
        setMessages(prev => [...prev, aiMessage])
        setLoading(false)
      }, 1000)
    } catch (error) {
      Alert.alert('Error', 'Failed to send message')
      setLoading(false)
    }
  }

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar />
        
        {/* Messages Container */}
        <ScrollView
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
              <Text className="text-base leading-5 text-typography-900 dark:text-white">
                AI is thinking...
              </Text>
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