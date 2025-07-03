import { useState } from 'react'
import { View, Text, StyleSheet, ScrollView, Alert, TouchableOpacity } from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { Button, Input, Card } from '@/components/common'
import { colors, spacing, typography } from '@/theme'
import { useRouter } from 'expo-router'
import { Ionicons } from '@expo/vector-icons'

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
      {/* App Bar */}
      <View style={styles.appBar}>
        <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={24} color={colors.text.primary} />
        </TouchableOpacity>
        
        <Text style={styles.appBarTitle}>Freeform Writing</Text>
        
        <View style={styles.appBarRight} />
      </View>

      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <Text style={styles.title}>Express your thoughts freely</Text>
          <Text style={styles.subtitle}>Write whatever comes to mind</Text>
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
    minHeight: 200,
  },
  button: {
    marginTop: spacing.md,
  },
}) 