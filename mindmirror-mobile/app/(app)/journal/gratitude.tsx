import React, { useState } from 'react'
import { View, Text, StyleSheet, ScrollView, Alert } from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { Button, Input, Card } from '@/components/common'
import { colors, spacing, typography } from '@/theme'
import { useRouter } from 'expo-router'

export default function GratitudeJournalScreen() {
  const [gratefulFor, setGratefulFor] = useState('')
  const [excitedAbout, setExcitedAbout] = useState('')
  const [focus, setFocus] = useState('')
  const [mood, setMood] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const handleSubmit = async () => {
    if (!gratefulFor.trim()) {
      Alert.alert('Error', 'Please fill in what you are grateful for')
      return
    }

    setLoading(true)
    try {
      // TODO: Implement GraphQL mutation to save gratitude journal entry
      console.log('Saving gratitude entry:', { gratefulFor, excitedAbout, focus, mood })
      
      Alert.alert(
        'Success',
        'Your gratitude entry has been saved!',
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
          <Text style={styles.title}>Gratitude Journal</Text>
          <Text style={styles.subtitle}>What are you grateful for today?</Text>
        </View>
        
        <View style={styles.content}>
          <Card style={styles.card}>
            <Input
              label="I am grateful for..."
              placeholder="What are you grateful for today?"
              value={gratefulFor}
              onChangeText={setGratefulFor}
              multiline
              numberOfLines={3}
              style={styles.input}
            />
            
            <Input
              label="I am excited about..."
              placeholder="What are you looking forward to?"
              value={excitedAbout}
              onChangeText={setExcitedAbout}
              multiline
              numberOfLines={3}
              style={styles.input}
            />
            
            <Input
              label="My focus for today..."
              placeholder="What will you focus on today?"
              value={focus}
              onChangeText={setFocus}
              multiline
              numberOfLines={2}
              style={styles.input}
            />
            
            <Input
              label="How are you feeling?"
              placeholder="Describe your mood"
              value={mood}
              onChangeText={setMood}
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
  },
  button: {
    marginTop: spacing.md,
  },
}) 