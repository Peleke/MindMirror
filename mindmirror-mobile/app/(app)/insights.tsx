import { Box } from "@/components/ui/box"
import { Button, ButtonText } from "@/components/ui/button"
import { Heading } from "@/components/ui/heading"
import { HStack } from "@/components/ui/hstack"
import { Icon } from "@/components/ui/icon"
import { SafeAreaView } from "@/components/ui/safe-area-view"
import { ScrollView } from "@/components/ui/scroll-view"
import { Text } from "@/components/ui/text"
import { VStack } from "@/components/ui/vstack"
import { SUMMARIZE_JOURNALS_QUERY } from '../../src/services/api/queries'
import { GENERATE_REVIEW } from '../../src/services/api/mutations'
import { useQuery, useMutation, useLazyQuery } from '@apollo/client'
import { useRouter } from 'expo-router'
import { BarChart3, Lightbulb, Star, TrendingUp, Trophy } from "lucide-react-native"
import { useState } from 'react'
import { AppBar } from '@/components/common/AppBar'

interface PerformanceReview {
  keySuccess: string
  improvementArea: string
  journalPrompt: string
}



export default function InsightsScreen() {
  const [selectedTradition, setSelectedTradition] = useState('canon-default')
  const [summarizeResult, setSummarizeResult] = useState<string | null>(null)
  const [reviewResult, setReviewResult] = useState<PerformanceReview | null>(null)

  // Summarize journals query - using useLazyQuery to prevent automatic execution
  const [summarizeJournals, { data: summarizeData, loading: summarizeLoading, error: summarizeError }] = useLazyQuery(SUMMARIZE_JOURNALS_QUERY, {
    fetchPolicy: 'network-only',
    notifyOnNetworkStatusChange: true,
    onCompleted: (data) => {
      if (data?.summarizeJournals?.summary) {
        setSummarizeResult(data.summarizeJournals.summary)
        setReviewResult(null) // Clear review results when summary completes
      }
    },
    onError: (error) => {
      console.error('Summarize error:', error)
      setSummarizeResult(null)
    }
  })

  // Generate review mutation
  const [generateReview, { loading: reviewLoading, error: reviewError }] = useMutation(GENERATE_REVIEW, {
    onCompleted: (data) => {
      if (data?.generateReview) {
        setReviewResult(data.generateReview)
        setSummarizeResult(null) // Clear summary results when review completes
      }
    },
    onError: (error) => {
      console.error('Review error:', error)
      setReviewResult(null)
    }
  })

  const handleSummarizeJournals = async () => {
    setSummarizeResult(null)
    setReviewResult(null)
    summarizeJournals()
  }

  const handlePerformanceReview = async () => {
    setReviewResult(null)
    setSummarizeResult(null)
    generateReview({
      variables: {
        tradition: selectedTradition,
      },
    })
  }

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title="Insights" />
        
        <ScrollView
          showsVerticalScrollIndicator={false}
          className="flex-1"
        >
          {/* Overview Section */}
          <VStack className="px-6 py-6" space="xs">
            <Heading size="xl" className="font-roboto text-typography-900 dark:text-white">
              Generate and view insights into your journaling patterns
            </Heading>
            <Text className="text-typography-600 dark:text-gray-200 leading-6">
              Use AI-powered analysis to understand your journaling habits, identify patterns, and get personalized recommendations for your personal growth journey. Select a tradition to customize the analysis approach.
            </Text>
          </VStack>



          {/* Action Buttons */}
          <HStack className="px-6 pb-6" space="md">
            <Button
              onPress={handleSummarizeJournals}
              disabled={summarizeLoading}
              className="flex-1 py-6"
            >
              <VStack className="items-center" space="sm">
                <Icon as={BarChart3} size="md" className="text-white" />
                <ButtonText>
                  {summarizeLoading ? 'Generating...' : 'Summarize Journals'}
                </ButtonText>
              </VStack>
            </Button>

            <Button
              onPress={handlePerformanceReview}
              disabled={reviewLoading}
              className="flex-1 py-6"
            >
              <VStack className="items-center" space="sm">
                <Icon as={Trophy} size="md" className="text-white" />
                <ButtonText>
                  {reviewLoading ? 'Analyzing...' : 'Performance Review'}
                </ButtonText>
              </VStack>
            </Button>
          </HStack>

          {/* Results Section */}
          <VStack className="px-6 pb-6" space="md">
            {/* Summarize Error */}
            {summarizeError && (
              <Box className="p-6 bg-red-50 dark:bg-red-950 rounded-lg border border-red-200 dark:border-red-700">
                <HStack className="items-center mb-4" space="sm">
                  <Icon as={BarChart3} size="md" className="text-red-600 dark:text-red-400" />
                  <Text className="text-lg font-semibold text-red-700 dark:text-red-300">
                    Summary Error
                  </Text>
                </HStack>
                <Text className="text-base text-red-600 dark:text-red-400 leading-6">
                  {summarizeError.message}
                </Text>
              </Box>
            )}

            {/* Review Error */}
            {reviewError && (
              <Box className="p-6 bg-red-50 dark:bg-red-950 rounded-lg border border-red-200 dark:border-red-700">
                <HStack className="items-center mb-4" space="sm">
                  <Icon as={Trophy} size="md" className="text-red-600 dark:text-red-400" />
                  <Text className="text-lg font-semibold text-red-700 dark:text-red-300">
                    Review Error
                  </Text>
                </HStack>
                <Text className="text-base text-red-600 dark:text-red-400 leading-6">
                  {reviewError.message}
                </Text>
              </Box>
            )}

            {/* Summarize Results */}
            {summarizeResult && (
              <Box className="p-6 bg-blue-50 dark:bg-blue-950 rounded-lg border border-border-200 dark:border-border-700">
                <HStack className="items-center mb-4" space="sm">
                  <Icon as={BarChart3} size="md" className="text-blue-600 dark:text-blue-400" />
                  <Text className="text-lg font-semibold text-typography-900 dark:text-white">
                    Journal Summary
                  </Text>
                </HStack>
                <Text className="text-base text-typography-600 dark:text-gray-200 leading-6">
                  {summarizeResult}
                </Text>
              </Box>
            )}

            {/* Performance Review Results */}
            {reviewResult && (
              <VStack space="md">
                <Box className="p-6 bg-indigo-50 dark:bg-indigo-950 rounded-lg border border-border-200 dark:border-border-700">
                  <HStack className="items-center mb-4" space="sm">
                    <Icon as={Trophy} size="md" className="text-indigo-600 dark:text-indigo-400" />
                    <Text className="text-lg font-semibold text-typography-900 dark:text-white">
                      Performance Review
                    </Text>
                  </HStack>
                </Box>

                {/* Key Success */}
                <Box className="p-6 bg-indigo-50 dark:bg-indigo-950 rounded-lg border border-border-200 dark:border-border-700">
                  <HStack className="items-center mb-4" space="sm">
                    <Icon as={Star} size="md" className="text-yellow-500" />
                    <Text className="text-lg font-semibold text-typography-900 dark:text-white">
                      Key Success
                    </Text>
                  </HStack>
                  <Text className="text-base text-typography-600 dark:text-gray-200 leading-6">
                    {reviewResult.keySuccess}
                  </Text>
                </Box>

                {/* Improvement Area */}
                <Box className="p-6 bg-indigo-50 dark:bg-indigo-950 rounded-lg border border-border-200 dark:border-border-700">
                  <HStack className="items-center mb-4" space="sm">
                    <Icon as={TrendingUp} size="md" className="text-indigo-500" />
                    <Text className="text-lg font-semibold text-typography-900 dark:text-white">
                      Area for Improvement
                    </Text>
                  </HStack>
                  <Text className="text-base text-typography-600 dark:text-gray-200 leading-6">
                    {reviewResult.improvementArea}
                  </Text>
                </Box>

                {/* Journal Prompt */}
                <Box className="p-6 bg-indigo-50 dark:bg-indigo-950 rounded-lg border border-border-200 dark:border-border-700">
                  <HStack className="items-center mb-4" space="sm">
                    <Icon as={Lightbulb} size="md" className="text-indigo-500" />
                    <Text className="text-lg font-semibold text-typography-900 dark:text-white">
                      Personalized Journal Prompt
                    </Text>
                  </HStack>
                  <Text className="text-base text-typography-600 dark:text-gray-200 leading-6 italic">
                    "{reviewResult.journalPrompt}"
                  </Text>
                </Box>
              </VStack>
            )}
          </VStack>
        </ScrollView>
      </VStack>
    </SafeAreaView>
  )
} 