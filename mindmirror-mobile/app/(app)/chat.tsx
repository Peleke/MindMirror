import React from 'react'
import { View, Text, StyleSheet } from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { Card } from '@/components/common'
import { colors, spacing, typography } from '@/theme'

export default function ChatScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>AI Chat</Text>
        <Text style={styles.subtitle}>Your personal AI assistant</Text>
      </View>
      
      <View style={styles.content}>
        <Card style={styles.card}>
          <Text style={styles.cardTitle}>Coming Soon</Text>
          <Text style={styles.cardText}>
            The AI chat feature is currently under development. 
            Soon you'll be able to have meaningful conversations 
            with your personal AI assistant about your thoughts, 
            feelings, and personal growth journey.
          </Text>
        </Card>
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
  content: {
    flex: 1,
    padding: spacing.lg,
    paddingTop: 0,
    justifyContent: 'center',
  },
  card: {
    padding: spacing.xl,
  },
  cardTitle: {
    fontSize: typography.sizes.xl,
    fontWeight: typography.weights.semibold,
    color: colors.text.primary,
    marginBottom: spacing.md,
    textAlign: 'center',
  },
  cardText: {
    fontSize: typography.sizes.base,
    color: colors.text.secondary,
    lineHeight: 24,
    textAlign: 'center',
  },
}) 