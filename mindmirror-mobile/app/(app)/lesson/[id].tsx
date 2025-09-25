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
import { useMutation, useQuery, gql } from '@apollo/client'
import { MARK_LESSON_COMPLETED, LESSON_TEMPLATE_BY_ID } from '@/services/api/habits'
import Markdown from 'react-native-markdown-display'

function convertGfmTablesToLists(md: string): string {
  const lines = (md || '').split('\n')
  const out: string[] = []
  let i = 0
  while (i < lines.length) {
    const line = lines[i] || ''
    // Detect start of GFM table: header row starting/ending with | and separator row next
    if (/^\|.*\|\s*$/.test(line) && i + 1 < lines.length && /^\|\s*[:\-\s\|]+\|\s*$/.test((lines[i + 1] || ''))) {
      // Parse headers
      const headers = (line || '')
        .trim()
        .slice(1, -1)
        .split('|')
        .map((h) => h.trim())
      i += 2 // skip header and separator
      // Collect rows
      const rows: string[][] = []
      while (i < lines.length && /^\|.*\|\s*$/.test(lines[i] || '')) {
        const cells = (lines[i] || '')
          .trim()
          .slice(1, -1)
          .split('|')
          .map((c) => c.trim())
        rows.push(cells)
        i += 1
      }
      // Emit as bullet list
      for (const r of rows) {
        const pairs: string[] = []
        for (let k = 0; k < Math.min(headers.length, r.length); k++) {
          const head = headers[k] || ''
          const cell = r[k] || ''
          if (head && cell) pairs.push(`${head}: ${cell}`)
        }
        if (pairs.length) out.push(`- ${pairs.join('  •  ')}`)
      }
      continue
    }
    out.push(line)
    i += 1
  }
  return out.join('\n')
}

export default function LessonDetailScreen() {
  const params = useLocalSearchParams<{ id: string; title?: string; summary?: string; subtitle?: string; from?: string; onDate?: string }>()
  const router = useRouter()
  const [markLessonCompleted] = useMutation(MARK_LESSON_COMPLETED)
  const mockEnabled = (((process.env.EXPO_PUBLIC_MOCK_TASKS as string) || (require('expo-constants').expoConfig?.extra as any)?.mockTasks) || '')
    .toString()
    .toLowerCase() === 'true'

  const today = new Date().toISOString().slice(0, 10)
  const onDate = (params.onDate as string) || today
  const [useLegacy, setUseLegacy] = React.useState(false)
  const { data: lessonDetailNew } = useQuery(LESSON_TEMPLATE_BY_ID, {
    variables: { id: String((params.id as string) || ''), onDate: String((onDate as string) || today) },
    fetchPolicy: 'cache-and-network',
    skip: useLegacy,
    onError: (err) => {
      const msg = (err?.graphQLErrors?.[0]?.message || '') as string
      if (msg.includes('Unknown argument') && msg.includes('onDate')) setUseLegacy(true)
    },
  })
  const LEGACY_QUERY = gql`
    query LessonTemplateByIdLegacy($id: String!) {
      lessonTemplateById(id: $id) { id slug title summary markdownContent subtitle __typename }
    }
  `
  const { data: lessonDetailLegacy } = useQuery(LEGACY_QUERY, {
    variables: { id: String((params.id as string) || '') },
    fetchPolicy: 'cache-and-network',
    skip: !useLegacy,
  })
  const lessonDetail = useLegacy ? lessonDetailLegacy : lessonDetailNew

  const content = (lessonDetail?.lessonTemplateById?.markdownContent as string) || ''
  const processedContent = React.useMemo(() => convertGfmTablesToLists(content), [content])

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar
          title={params.title ? String(params.title) : 'Lesson'}
          showBackButton
          onBackPress={() => {
            try {
              // Respect origin screen when provided
              const from = (params.from as string) || ''
              if (from === 'programs') {
                router.replace('/programs')
                return
              }
              if (from === 'tasks' || from === 'journal') {
                const backDate = (params.onDate as string) || new Date().toISOString().slice(0, 10)
                router.replace({ pathname: '/journal', params: { date: backDate } })
                return
              }
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
              ) : null}
            </VStack>

            <Box className="p-4 rounded-lg border border-border-200 dark:border-border-700 bg-background-50 dark:bg-background-100">
              <Markdown>
                {processedContent}
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


