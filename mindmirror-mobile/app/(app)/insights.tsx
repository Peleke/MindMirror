import { useState } from 'react'
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { Card } from '@/components/common'
import { colors, spacing, typography } from '@/theme'
import { useRouter } from 'expo-router'
import { useNavigation } from '@react-navigation/native'
import { Ionicons } from '@expo/vector-icons'

interface PerformanceReview {
  keySuccess: string
  improvementArea: string
  journalPrompt: string
}

export default function InsightsScreen() {
  const [summarizeLoading, setSummarizeLoading] = useState(false)
  const [reviewLoading, setReviewLoading] = useState(false)
  const [summarizeResult, setSummarizeResult] = useState<string | null>(null)
  const [reviewResult, setReviewResult] = useState<PerformanceReview | null>(null)
  const router = useRouter()
  const navigation = useNavigation()

  const handleMenuPress = () => {
    ;(navigation as any).openDrawer()
  }

  const handleSummarizeJournals = async () => {
    setSummarizeLoading(true)
    setSummarizeResult(null)
    
    // Mock API call
    setTimeout(() => {
      setSummarizeResult("Based on your recent journal entries, I notice a positive trend in your gratitude practice. You've been consistently reflecting on meaningful relationships and personal growth. Your entries show increasing self-awareness and a balanced perspective on challenges. The frequency of your journaling has been steady, which is excellent for building this habit.")
      setSummarizeLoading(false)
    }, 2000)
  }

  const handlePerformanceReview = async () => {
    setReviewLoading(true)
    setReviewResult(null)
    
    // Mock API call
    setTimeout(() => {
      setReviewResult({
        keySuccess: "You've shown remarkable consistency in your journaling practice over the past two weeks. Your ability to find gratitude in daily moments has improved significantly, and you're developing deeper self-reflection skills.",
        improvementArea: "Consider exploring more specific goals and action plans in your entries. While reflection is strong, actionable next steps could enhance your personal growth journey.",
        journalPrompt: "Reflect on a recent challenge you faced and write about how you can apply the lessons learned to create a specific action plan for future similar situations."
      })
      setReviewLoading(false)
    }, 3000)
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* App Bar */}
      <View style={styles.appBar}>
        <TouchableOpacity style={styles.menuButton} onPress={handleMenuPress}>
          <Ionicons name="menu" size={24} color={colors.text.primary} />
        </TouchableOpacity>
        
        <Text style={styles.appBarTitle}>Insights</Text>
        
        <TouchableOpacity 
          style={styles.profileButton}
          onPress={() => router.push('/(app)/profile')}
        >
          <Ionicons name="person-circle" size={28} color={colors.text.primary} />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.scrollView}>
        {/* Overview Section */}
        <View style={styles.overviewSection}>
          <Text style={styles.overviewTitle}>Generate and view insights into your journaling patterns</Text>
          <Text style={styles.overviewSubtitle}>
            Use AI-powered analysis to understand your journaling habits, identify patterns, and get personalized recommendations for your personal growth journey.
          </Text>
        </View>

        {/* Action Buttons */}
        <View style={styles.buttonRow}>
          <TouchableOpacity
            style={[styles.actionButton, summarizeLoading && styles.actionButtonDisabled]}
            onPress={handleSummarizeJournals}
            disabled={summarizeLoading}
          >
            <Ionicons name="analytics" size={24} color={summarizeLoading ? colors.text.tertiary : colors.text.inverse} />
            <Text style={[styles.actionButtonText, summarizeLoading && styles.actionButtonTextDisabled]}>
              {summarizeLoading ? 'Generating...' : 'Summarize Journals'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionButton, reviewLoading && styles.actionButtonDisabled]}
            onPress={handlePerformanceReview}
            disabled={reviewLoading}
          >
            <Ionicons name="trophy" size={24} color={reviewLoading ? colors.text.tertiary : colors.text.inverse} />
            <Text style={[styles.actionButtonText, reviewLoading && styles.actionButtonTextDisabled]}>
              {reviewLoading ? 'Analyzing...' : 'Performance Review'}
            </Text>
          </TouchableOpacity>
        </View>

        {/* Results Section */}
        <View style={styles.resultsSection}>
          {/* Summarize Results */}
          {summarizeResult && (
            <Card style={styles.resultCard}>
              <View style={styles.resultHeader}>
                <Ionicons name="analytics" size={20} color={colors.primary[600]} />
                <Text style={styles.resultTitle}>Journal Summary</Text>
              </View>
              <Text style={styles.resultText}>{summarizeResult}</Text>
            </Card>
          )}

          {/* Performance Review Results */}
          {reviewResult && (
            <View style={styles.reviewResults}>
              <Card style={styles.resultCard}>
                <View style={styles.resultHeader}>
                  <Ionicons name="trophy" size={20} color={colors.primary[600]} />
                  <Text style={styles.resultTitle}>Performance Review</Text>
                </View>
              </Card>

              {/* Key Success */}
              <Card style={styles.resultCard}>
                <View style={styles.resultHeader}>
                  <Ionicons name="star" size={20} color={colors.warning[500]} />
                  <Text style={styles.resultTitle}>Key Success</Text>
                </View>
                <Text style={styles.resultText}>{reviewResult.keySuccess}</Text>
              </Card>

              {/* Improvement Area */}
              <Card style={styles.resultCard}>
                <View style={styles.resultHeader}>
                  <Ionicons name="trending-up" size={20} color={colors.primary[500]} />
                  <Text style={styles.resultTitle}>Area for Improvement</Text>
                </View>
                <Text style={styles.resultText}>{reviewResult.improvementArea}</Text>
              </Card>

              {/* Journal Prompt */}
              <Card style={styles.resultCard}>
                <View style={styles.resultHeader}>
                  <Ionicons name="bulb" size={20} color={colors.secondary[500]} />
                  <Text style={styles.resultTitle}>Personalized Journal Prompt</Text>
                </View>
                <Text style={[styles.resultText, styles.promptText]}>"{reviewResult.journalPrompt}"</Text>
              </Card>
            </View>
          )}
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
  menuButton: {
    padding: spacing.sm,
  },
  appBarTitle: {
    fontSize: typography.sizes.xl,
    fontWeight: typography.weights.bold,
    color: colors.text.primary,
  },
  profileButton: {
    padding: spacing.sm,
  },
  scrollView: {
    flex: 1,
  },
  overviewSection: {
    padding: spacing.lg,
    paddingBottom: spacing.md,
  },
  overviewTitle: {
    fontSize: typography.sizes.xl,
    fontWeight: typography.weights.bold,
    color: colors.text.primary,
    marginBottom: spacing.sm,
  },
  overviewSubtitle: {
    fontSize: typography.sizes.base,
    color: colors.text.secondary,
    lineHeight: 22,
  },
  buttonRow: {
    flexDirection: 'row',
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.lg,
    gap: spacing.md,
  },
  actionButton: {
    flex: 1,
    backgroundColor: colors.primary[600],
    paddingVertical: spacing.lg,
    paddingHorizontal: spacing.md,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
    elevation: 2,
    shadowColor: colors.primary[600],
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
  },
  actionButtonDisabled: {
    backgroundColor: colors.gray[300],
  },
  actionButtonText: {
    fontSize: typography.sizes.base,
    fontWeight: typography.weights.semibold,
    color: colors.text.inverse,
  },
  actionButtonTextDisabled: {
    color: colors.text.tertiary,
  },
  resultsSection: {
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.lg,
  },
  resultCard: {
    marginBottom: spacing.md,
    padding: spacing.lg,
  },
  resultHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
    gap: spacing.sm,
  },
  resultTitle: {
    fontSize: typography.sizes.lg,
    fontWeight: typography.weights.semibold,
    color: colors.text.primary,
  },
  resultText: {
    fontSize: typography.sizes.base,
    color: colors.text.secondary,
    lineHeight: 22,
  },
  promptText: {
    fontStyle: 'italic',
  },
  reviewResults: {
    gap: spacing.md,
  },
}) 