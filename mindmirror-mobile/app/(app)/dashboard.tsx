import React from 'react'
import { View, Text, StyleSheet, ScrollView } from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { Card } from '@/components/common'
import { colors, spacing, typography } from '@/theme'

export default function DashboardScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <Text style={styles.title}>Dashboard</Text>
          <Text style={styles.subtitle}>Your mindful journey starts here</Text>
        </View>
        
        <View style={styles.content}>
          <Card style={styles.card}>
            <Text style={styles.cardTitle}>Today's Affirmation</Text>
            <Text style={styles.cardText}>
              "Every moment is a new beginning. Embrace the journey of self-discovery."
            </Text>
          </Card>
          
          <Card style={styles.card}>
            <Text style={styles.cardTitle}>Journal Streak</Text>
            <Text style={styles.cardText}>7 days in a row! Keep up the great work.</Text>
          </Card>
          
          <Card style={styles.card}>
            <Text style={styles.cardTitle}>Recent Insights</Text>
            <Text style={styles.cardText}>
              Your gratitude practice is showing positive patterns. Consider exploring deeper reflections.
            </Text>
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
    lineHeight: 24,
  },
}) 