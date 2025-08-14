import React, { useMemo, useState } from 'react'
// Hide this route from expo-router drawer
export const href = null as any
export const unstable_settings = { initialRouteName: '(app)' } as any
export const options = { drawerItemStyle: { display: 'none' } } as any
import { useLocalSearchParams, useRouter } from 'expo-router'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { VStack } from '@/components/ui/vstack'
import { ScrollView } from '@/components/ui/scroll-view'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { HStack } from '@/components/ui/hstack'
import { Pressable } from '@/components/ui/pressable'
import { Icon } from '@/components/ui/icon'
import { Button, ButtonText } from '@/components/ui/button'
import { Textarea, TextareaInput } from '@/components/ui/textarea'
import { useMutation } from '@apollo/client'
import { RECORD_HABIT_RESPONSE, LESSONS_FOR_HABIT } from '@/services/api/habits'
import { useQuery, gql } from '@apollo/client'
import { CheckCircle, Circle } from 'lucide-react-native'
import { AppBar } from '@/components/common/AppBar'

function todayIsoDate(): string {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export default function HabitDetailScreen() {
  const params = useLocalSearchParams<{ id: string; title?: string; description?: string }>()
  const router = useRouter()
  const onDate = useMemo(() => todayIsoDate(), [])
  const [response, setResponse] = useState<'yes' | 'no' | null>(null)
  const [note, setNote] = useState('')
  const [recordHabitResponse] = useMutation(RECORD_HABIT_RESPONSE)
  const mockEnabled = (((process.env.EXPO_PUBLIC_MOCK_TASKS as string) || (require('expo-constants').expoConfig?.extra as any)?.mockTasks) || '')
    .toString()
    .toLowerCase() === 'true'

  const handleRespond = async (r: 'yes' | 'no') => {
    setResponse(r)
    if (!mockEnabled) {
      await recordHabitResponse({ variables: { habitTemplateId: params.id, onDate, response: r } })
    }
  }

  // Lessons associated with this habit (mock-first)
  const today = new Date().toISOString().slice(0, 10)
  const { data: lessonsData } = useQuery(
    gql`
      query LessonsForHabitInline($habitTemplateId: String!, $onDate: Date!) {
        lessonsForHabit(habitTemplateId: $habitTemplateId, onDate: $onDate) {
          lessonTemplateId
          title
          summary
          completed
        }
      }
    `,
    { variables: { habitTemplateId: String(params.id), onDate: today }, fetchPolicy: 'cache-and-network' }
  )

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar
          title={params.title ? String(params.title) : 'Habit'}
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
              <Text className="text-2xl font-bold text-typography-900 dark:text-white">{params.title || 'Habit'}</Text>
              {params.description ? (
                <Text className="text-typography-600 dark:text-gray-300">{params.description}</Text>
              ) : null}
            </VStack>

            {/* Response Section */}
            <VStack space="sm">
              <Text className="text-base text-typography-800 dark:text-gray-200">
                {response ? 'Your response has been recorded.' : 'Did you do your habit today?'}
              </Text>
              <HStack space="sm">
                <Button onPress={() => handleRespond('yes')} className={`flex-1 ${response === 'yes' ? 'bg-blue-500' : 'bg-blue-400'} `}>
                  <ButtonText>Yes</ButtonText>
                </Button>
                <Button onPress={() => handleRespond('no')} className={`flex-1 ${response === 'no' ? 'bg-red-500' : 'bg-red-400'} `}>
                  <ButtonText>No</ButtonText>
                </Button>
              </HStack>
            </VStack>

            {/* Journal Note Section */}
            <VStack space="sm">
              <Text className="text-base font-semibold text-typography-900 dark:text-white">Add a note (optional)</Text>
              <Box className="bg-white dark:bg-gray-800 rounded-lg border border-border-200 dark:border-border-700 p-2">
                <Textarea>
                  <TextareaInput
                    placeholder="Write about your experience..."
                    value={note}
                    onChangeText={setNote}
                    numberOfLines={12}
                    textAlignVertical="top"
                    style={{ minHeight: 280, fontSize: 16, lineHeight: 24 }}
                    multiline
                    maxLength={2000}
                  />
                </Textarea>
              </Box>
              <HStack space="sm">
                <Button className="flex-1 bg-green-500">
                  <ButtonText>Save</ButtonText>
                </Button>
                <Button className="flex-1 bg-green-600">
                  <ButtonText>Save and Chat</ButtonText>
                </Button>
              </HStack>
            </VStack>

            {/* Associated lessons */}
            <VStack space="sm">
              <Text className="text-xl font-bold text-typography-900 dark:text-white">Lessons</Text>
              <Box className="h-px bg-border-200 dark:bg-border-700" />
              {((lessonsData?.lessonsForHabit as any[]) || []).length === 0 ? (
                <Text className="text-typography-600 dark:text-gray-400">No lessons found.</Text>
              ) : ((lessonsData?.lessonsForHabit as any[]) || []).map((l: any) => (
                <Pressable
                  key={l.lessonTemplateId}
                  onPress={() => router.push(`/lesson/${l.lessonTemplateId}?title=${encodeURIComponent(l.title)}&summary=${encodeURIComponent(l.summary || '')}&from=tasks`)}
                >
                  <HStack className="py-3 items-center justify-between">
                    <HStack space="sm" className="items-center">
                      <Icon as={CheckCircle} size="sm" className={` ${l.completed ? 'text-green-600' : 'text-gray-300'}`} />
                      <VStack>
                        <Text className="text-base font-semibold text-typography-900 dark:text-white">{l.title}</Text>
                        {l.summary ? (
                          <Text className="text-typography-600 dark:text-gray-300">{l.summary}</Text>
                        ) : null}
                      </VStack>
                    </HStack>
                    <Icon as={l.completed ? CheckCircle : Circle} size="md" className={`${l.completed ? 'text-green-600' : 'text-gray-400'}`} />
                  </HStack>
                </Pressable>
              ))}
            </VStack>
          </VStack>
        </ScrollView>
      </VStack>
    </SafeAreaView>
  )
}


