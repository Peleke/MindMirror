import React from 'react'
import { View, Text, StyleSheet, ScrollView } from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { Button, Card } from '@/components/common'
import { colors, spacing, typography } from '@/theme'

export default function JournalScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <Text style={styles.title}>Journal</Text>
          <Text style={styles.subtitle}>Reflect on your day</Text>
        </View>
        
        <View style={styles.content}>
          <Card style={styles.card}>
            <Text style={styles.cardTitle}>Gratitude Journal</Text>
            <Text style={styles.cardText}>
              Write about what you're grateful for today
            </Text>
            <Button
              title="Start Writing"
              onPress={() => console.log('Open gratitude journal')}
              style={styles.button}
            />
          </Card>
          
          <Card style={styles.card}>
            <Text style={styles.cardTitle}>Reflection Journal</Text>
            <Text style={styles.cardText}>
              Reflect on your wins and areas for improvement
            </Text>
            <Button
              title="Start Writing"
              onPress={() => console.log('Open reflection journal')}
              style={styles.button}
            />
          </Card>
          
          <Card style={styles.card}>
            <Text style={styles.cardTitle}>Freeform Journal</Text>
            <Text style={styles.cardText}>
              Write freely about anything on your mind
            </Text>
            <Button
              title="Start Writing"
              onPress={() => console.log('Open freeform journal')}
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
    marginBottom: spacing.md,
  },
  cardTitle: {
    fontSize: typography.sizes.lg,
    fontWeight: typography.weights.semibold,
    color: colors.text.primary,
    marginBottom: spacing.sm,
  },
  cardText: {
    fontSize: typography.sizes.base,
    color: colors.text.secondary,
    marginBottom: spacing.md,
    lineHeight: 24,
  },
  button: {
    alignSelf: 'flex-start',
  },
}) 