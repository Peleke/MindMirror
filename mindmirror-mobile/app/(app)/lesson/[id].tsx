import React from 'react'
// Hide this route from expo-router drawer
export const href = null as any
export const unstable_settings = { initialRouteName: '(app)' } as any
import { useLocalSearchParams, useRouter } from 'expo-router'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { VStack } from '@/components/ui/vstack'
import { ScrollView } from '@/components/ui/scroll-view'
import { Text } from '@/components/ui/text'
import { Box } from '@/components/ui/box'
import { AppBar } from '@/components/common/AppBar'
import { Button, ButtonText } from '@/components/ui/button'
import { useMutation, useQuery } from '@apollo/client'
import { MARK_LESSON_COMPLETED, LESSON_TEMPLATE_BY_ID } from '@/services/api/habits'
import Markdown from 'react-native-markdown-display'

export default function LessonDetailScreen() {
  const params = useLocalSearchParams<{ id: string; title?: string; summary?: string; subtitle?: string }>()
  const router = useRouter()
  const [markLessonCompleted] = useMutation(MARK_LESSON_COMPLETED)
  const mockEnabled = (((process.env.EXPO_PUBLIC_MOCK_TASKS as string) || (require('expo-constants').expoConfig?.extra as any)?.mockTasks) || '')
    .toString()
    .toLowerCase() === 'true'

  const { data: lessonDetail } = useQuery(LESSON_TEMPLATE_BY_ID, {
    variables: { id: String(params.id) },
    fetchPolicy: 'cache-and-network',
  })

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar
          title={params.title ? String(params.title) : 'Lesson'}
          showBackButton
          onBackPress={() => {
            try {
              router.back()
            } catch {
              router.replace('/journal')
            }
          }}
        />
        <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
          <VStack className="px-6 py-6 w-full max-w-screen-md mx-auto" space="lg">
            <VStack space="sm">
              <Text className="text-2xl font-bold text-typography-900 dark:text-white">{params.title || 'Lesson'}</Text>
              {lessonDetail?.lessonTemplateById?.subtitle ? (
                <Text className="text-typography-600 dark:text-gray-300">{lessonDetail?.lessonTemplateById?.subtitle}</Text>
              ) : params.subtitle ? (
                <Text className="text-typography-600 dark:text-gray-300">{params.subtitle}</Text>
              ) : params.summary ? (
                <Text className="text-typography-600 dark:text-gray-300">{params.summary}</Text>
              ) : null}
            </VStack>

            <Box className="p-4 rounded-lg border border-border-200 dark:border-border-700 bg-background-50 dark:bg-background-100">
              <Markdown>
                {lessonDetail?.lessonTemplateById?.markdownContent || (params.summary as string) || ''}
              </Markdown>
            </Box>

            <Button
              className="bg-blue-500"
              onPress={async () => {
                if (!mockEnabled) {
                  const today = new Date().toISOString().slice(0, 10)
                  await markLessonCompleted({ variables: { lessonTemplateId: String(params.id), onDate: today } })
                }
                router.replace({ pathname: '/journal', params: { reload: '1' } })
              }}
            >
              <ButtonText>Complete Lesson</ButtonText>
            </Button>
          </VStack>
        </ScrollView>
      </VStack>
    </SafeAreaView>
  )
}


