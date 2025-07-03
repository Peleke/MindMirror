import { useState } from 'react'
import { View, Text, StyleSheet, ScrollView, Alert, TouchableOpacity } from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { Button, Input, Card } from '@/components/common'
import { colors, spacing, typography } from '@/theme'
import { useRouter } from 'expo-router'
import { Ionicons } from '@expo/vector-icons'

export default function ReflectionJournalScreen() {
  const [wins, setWins] = useState('')
  const [improvements, setImprovements] = useState('')
  const [mood, setMood] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const handleSubmit = async () => {
    if (!wins.trim()) {
      Alert.alert('Error', 'Please fill in your wins for today')
      return
    }

    setLoading(true)
    try {
      // TODO: Implement GraphQL mutation to save reflection journal entry
      console.log('Saving reflection entry:', { wins, improvements, mood })
      
      Alert.alert(
        'Success',
        'Your reflection entry has been saved!',
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
      {/* App Bar */}
      <View style={styles.appBar}>
        <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={24} color={colors.text.primary} />
        </TouchableOpacity>
        
        <Text style={styles.appBarTitle}>Daily Reflection</Text>
        
        <View style={styles.appBarRight} />
      </View>

      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <Text style={styles.title}>Look back on your day</Text>
          <Text style={styles.subtitle}>Reflect on your experiences and insights</Text>
        </View>
        
        <View style={styles.content}>
          <Card style={styles.card}>
            <Input
              label="Today's Wins"
              placeholder="What went well today?"
              value={wins}
              onChangeText={setWins}
              multiline
              numberOfLines={4}
              style={styles.input}
            />
            
            <Input
              label="Areas for Improvement"
              placeholder="What could you improve on?"
              value={improvements}
              onChangeText={setImprovements}
              multiline
              numberOfLines={4}
              style={styles.input}
            />
            
            <Input
              label="How are you feeling?"
              placeholder="Describe your mood and energy"
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
  appBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border.light,
    backgroundColor: colors.background.primary,
  },
  backButton: {
    padding: spacing.sm,
  },
  appBarTitle: {
    fontSize: typography.sizes.xl,
    fontWeight: typography.weights.bold,
    color: colors.text.primary,
  },
  appBarRight: {
    width: 44, // Same width as backButton for balance
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