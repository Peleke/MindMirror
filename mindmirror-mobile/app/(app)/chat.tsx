import React, { useState } from 'react'
import { View, Text, StyleSheet, ScrollView, TextInput, TouchableOpacity, Alert } from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { Card, Button } from '@/components/common'
import { colors, spacing, typography } from '@/theme'
import { useQuery } from '@apollo/client'
import { ASK_QUERY, LIST_TRADITIONS } from '@/services/api/queries'

interface Message {
  id: string
  text: string
  isUser: boolean
  timestamp: Date
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
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>AI Chat</Text>
        <Text style={styles.subtitle}>Your personal AI assistant</Text>
      </View>
      
      <ScrollView style={styles.messagesContainer}>
        {messages.map((message) => (
          <View
            key={message.id}
            style={[
              styles.messageContainer,
              message.isUser ? styles.userMessage : styles.aiMessage,
            ]}
          >
            <Text style={[
              styles.messageText,
              message.isUser ? styles.userMessageText : styles.aiMessageText,
            ]}>
              {message.text}
            </Text>
          </View>
        ))}
        {loading && (
          <View style={[styles.messageContainer, styles.aiMessage]}>
            <Text style={[styles.messageText, styles.aiMessageText]}>
              AI is thinking...
            </Text>
          </View>
        )}
      </ScrollView>

      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          value={inputText}
          onChangeText={setInputText}
          placeholder="Type your message..."
          multiline
          maxLength={500}
        />
        <TouchableOpacity
          style={[styles.sendButton, !inputText.trim() && styles.sendButtonDisabled]}
          onPress={sendMessage}
          disabled={!inputText.trim() || loading}
        >
          <Text style={styles.sendButtonText}>Send</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background.primary,
  },
  header: {
    padding: spacing.lg,
    paddingBottom: spacing.md,
  },
  title: {
    fontSize: typography.sizes['2xl'],
    fontWeight: typography.weights.bold,
    color: colors.text.primary,
    marginBottom: spacing.xs,
  },
  subtitle: {
    fontSize: typography.sizes.base,
    color: colors.text.secondary,
  },
  messagesContainer: {
    flex: 1,
    padding: spacing.md,
  },
  messageContainer: {
    marginBottom: spacing.md,
    padding: spacing.md,
    borderRadius: 12,
    maxWidth: '80%',
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: colors.primary[600],
  },
  aiMessage: {
    alignSelf: 'flex-start',
    backgroundColor: colors.background.secondary,
  },
  messageText: {
    fontSize: typography.sizes.base,
    lineHeight: 20,
  },
  userMessageText: {
    color: colors.text.inverse,
  },
  aiMessageText: {
    color: colors.text.primary,
  },
  inputContainer: {
    flexDirection: 'row',
    padding: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.border.light,
    backgroundColor: colors.background.primary,
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: colors.border.medium,
    borderRadius: 20,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    marginRight: spacing.sm,
    fontSize: typography.sizes.base,
    color: colors.text.primary,
    backgroundColor: colors.background.primary,
  },
  sendButton: {
    backgroundColor: colors.primary[600],
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButtonDisabled: {
    backgroundColor: colors.gray[300],
  },
  sendButtonText: {
    color: colors.text.inverse,
    fontSize: typography.sizes.base,
    fontWeight: typography.weights.medium,
  },
}) 