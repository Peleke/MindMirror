import React, { useState } from 'react'
import { View, Text, StyleSheet, ScrollView, Alert } from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { Button, Input, Card } from '@/components/common'
import { colors, spacing, typography } from '@/theme'
import { useRouter } from 'expo-router'

export default function FreeformJournalScreen() {
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const handleSubmit = async () => {
    if (!content.trim()) {
      Alert.alert('Error', 'Please write something in your journal')
      return
    }

    setLoading(true)
    try {
      // TODO: Implement GraphQL mutation to save freeform journal entry
      console.log('Saving freeform entry:', { content })
      
      Alert.alert(
        'Success',
        'Your journal entry has been saved!',
        [{ text: 'OK', onPress: () => router.back() }]
      )
    } catch (error) {
      Alert.alert('Error', 'Failed to save your entry')
    } finally {
      setLoading(false)
    }
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <Text style={styles.title}>Freeform Journal</Text>
          <Text style={styles.subtitle}>Write freely about anything on your mind</Text>
        </View>
        
        <View style={styles.content}>
          <Card style={styles.card}>
            <Input
              label="Your Thoughts"
              placeholder="Write whatever comes to mind..."
              value={content}
              onChangeText={setContent}
              multiline
              numberOfLines={12}
              textAlignVertical="top"
              style={styles.input}
            />
            
            <Button
              title="Save Entry"
              onPress={handleSubmit}
              loading={loading}
              style={styles.button}
            />
          </Card>
        </View>
      </ScrollView>
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background.primary,
  },
  scrollView: {
    flex: 1,
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
    padding: spacing.lg,
    paddingTop: 0,
  },
  card: {
    padding: spacing.lg,
  },
  input: {
    marginBottom: spacing.md,
    minHeight: 200,
  },
  button: {
    marginTop: spacing.md,
  },
}) 