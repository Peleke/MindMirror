import {
  Avatar,
  AvatarBadge,
  AvatarFallbackText,
  AvatarImage,
} from "@/components/ui/avatar"
import { Box } from "@/components/ui/box"
import { Button, ButtonText } from "@/components/ui/button"
import { Heading } from "@/components/ui/heading"
import { HStack } from "@/components/ui/hstack"
import { Icon, MenuIcon } from "@/components/ui/icon"
import { Pressable } from "@/components/ui/pressable"
import { SafeAreaView } from "@/components/ui/safe-area-view"
import { ScrollView } from "@/components/ui/scroll-view"
import { Text } from "@/components/ui/text"
import { VStack } from "@/components/ui/vstack"
import { useNavigation } from '@react-navigation/native'
import { useRouter } from 'expo-router'
import { BarChart3, Lightbulb, Star, TrendingUp, Trophy } from "lucide-react-native"
import { useState } from 'react'

interface PerformanceReview {
  keySuccess: string
  improvementArea: string
  journalPrompt: string
}

function AppBar() {
  const router = useRouter()
  const navigation = useNavigation()

  const handleMenuPress = () => {
    (navigation as any).openDrawer()
  }

  const handleProfilePress = () => {
    router.push('/(app)/profile')
  }

  return (
    <HStack
      className="py-6 px-4 border-b border-border-300 bg-background-0 items-center justify-between"
      space="md"
    >
      <HStack className="items-center" space="sm">
        <Pressable onPress={handleMenuPress}>
          <Icon as={MenuIcon} />
        </Pressable>
        <Text className="text-xl">Insights</Text>
      </HStack>
      
      <Pressable onPress={handleProfilePress}>
        <Avatar className="h-9 w-9">
          <AvatarFallbackText>U</AvatarFallbackText>
          <AvatarImage source={{ uri: "https://i.pravatar.cc/300" }} />
          <AvatarBadge />
        </Avatar>
      </Pressable>
    </HStack>
  )
}

export default function InsightsScreen() {
  const [summarizeLoading, setSummarizeLoading] = useState(false)
  const [reviewLoading, setReviewLoading] = useState(false)
  const [summarizeResult, setSummarizeResult] = useState<string | null>(null)
  const [reviewResult, setReviewResult] = useState<PerformanceReview | null>(null)

  const handleSummarizeJournals = async () => {
    setSummarizeLoading(true)
    setSummarizeResult(null)
    setReviewResult(null) // Clear review results when starting summary
    
    // Mock API call
    setTimeout(() => {
      setSummarizeResult("Based on your recent journal entries, I notice a positive trend in your gratitude practice. You've been consistently reflecting on meaningful relationships and personal growth. Your entries show increasing self-awareness and a balanced perspective on challenges. The frequency of your journaling has been steady, which is excellent for building this habit.")
      setSummarizeLoading(false)
    }, 2000)
  }

  const handlePerformanceReview = async () => {
    setReviewLoading(true)
    setReviewResult(null)
    setSummarizeResult(null) // Clear summary results when starting review
    
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
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar />
        
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
              Use AI-powered analysis to understand your journaling habits, identify patterns, and get personalized recommendations for your personal growth journey.
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
            {/* Summarize Results */}
            {summarizeResult && (
              <Box className="p-6 bg-background-50 dark:bg-background-100 rounded-lg border border-border-200 dark:border-border-700">
                <HStack className="items-center mb-4" space="sm">
                  <Icon as={BarChart3} size="md" className="text-primary-600 dark:text-primary-400" />
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
                <Box className="p-6 bg-background-50 dark:bg-background-100 rounded-lg border border-border-200 dark:border-border-700">
                  <HStack className="items-center mb-4" space="sm">
                    <Icon as={Trophy} size="md" className="text-primary-600 dark:text-primary-400" />
                    <Text className="text-lg font-semibold text-typography-900 dark:text-white">
                      Performance Review
                    </Text>
                  </HStack>
                </Box>

                {/* Key Success */}
                <Box className="p-6 bg-background-50 dark:bg-background-100 rounded-lg border border-border-200 dark:border-border-700">
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
                <Box className="p-6 bg-background-50 dark:bg-background-100 rounded-lg border border-border-200 dark:border-border-700">
                  <HStack className="items-center mb-4" space="sm">
                    <Icon as={TrendingUp} size="md" className="text-primary-500" />
                    <Text className="text-lg font-semibold text-typography-900 dark:text-white">
                      Area for Improvement
                    </Text>
                  </HStack>
                  <Text className="text-base text-typography-600 dark:text-gray-200 leading-6">
                    {reviewResult.improvementArea}
                  </Text>
                </Box>

                {/* Journal Prompt */}
                <Box className="p-6 bg-background-50 dark:bg-background-100 rounded-lg border border-border-200 dark:border-border-700">
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