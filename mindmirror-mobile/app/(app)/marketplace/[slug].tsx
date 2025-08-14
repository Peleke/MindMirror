import React from 'react'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { VStack } from '@/components/ui/vstack'
import { ScrollView } from '@/components/ui/scroll-view'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { AppBar } from '@/components/common/AppBar'
import { useLocalSearchParams, useRouter } from 'expo-router'
import { useMutation, useQuery } from '@apollo/client'
import { PROGRAM_TEMPLATE_BY_SLUG, ASSIGN_PROGRAM_TO_USER, PROGRAM_STEPS } from '@/services/api/habits'
import { Button, ButtonText } from '@/components/ui/button'
import { useToast } from '@/components/ui/toast'
import { Toast, ToastDescription, ToastTitle } from '@/components/ui/toast'

export default function ProgramDetailScreen() {
  const params = useLocalSearchParams<{ slug: string; from?: string }>()
  const slug = params.slug
  const from = params.from
  const router = useRouter()
  const { data, loading, error } = useQuery(PROGRAM_TEMPLATE_BY_SLUG, { variables: { slug }, fetchPolicy: 'cache-and-network' })
  const [assignProgramToUser] = useMutation(ASSIGN_PROGRAM_TO_USER)
  const { show } = useToast()

  const program = data?.programTemplateBySlug
  const { data: stepsData } = useQuery(PROGRAM_STEPS, {
    skip: !program?.id,
    variables: { programId: program?.id },
    fetchPolicy: 'cache-and-network',
  })

  const handleEnroll = async () => {
    const today = new Date().toISOString().slice(0, 10)
    try {
      await assignProgramToUser({ variables: { programId: program.id, startDate: today } })
      show({
        placement: 'top',
        render: ({ id }) => (
          <Toast nativeID={`toast-${id}`} action="success" variant="solid">
            <VStack>
              <ToastTitle>Enrolled</ToastTitle>
              <ToastDescription>You are enrolled. Loading todays tasks…</ToastDescription>
            </VStack>
          </Toast>
        ),
      })
      router.replace({ pathname: '/journal', params: { reload: '1' } })
    } catch (e) {
      show({
        placement: 'top',
        render: ({ id }) => (
          <Toast nativeID={`toast-${id}`} action="error" variant="solid">
            <VStack>
              <ToastTitle>Enrollment failed</ToastTitle>
              <ToastDescription>Please try again.</ToastDescription>
            </VStack>
          </Toast>
        ),
      })
    }
  }

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar
          title={program?.title || 'Program'}
          showBackButton
          onBackPress={() => {
            if (from === 'marketplace') {
              router.replace('/marketplace')
            } else {
              try {
                router.back()
              } catch {
                router.replace('/journal')
              }
            }
          }}
        />
        <ScrollView showsVerticalScrollIndicator={false} className="flex-1">
          <VStack className="w-full max-w-screen-md mx-auto px-6 py-6" space="lg">
            {loading && !program ? (
              <Text className="text-typography-600 dark:text-gray-300">Loading…</Text>
            ) : error ? (
              <Text className="text-red-600 dark:text-red-400">Failed to load program</Text>
            ) : (
              <>
                <VStack space="sm">
                  <Text className="text-2xl font-bold text-typography-900 dark:text-white">{program.title}</Text>
                  {program.description ? (
                    <Text className="text-typography-600 dark:text-gray-300">{program.description}</Text>
                  ) : null}
                </VStack>

                <VStack space="sm">
                  <Text className="text-xl font-bold text-typography-900 dark:text-white">Program Steps</Text>
                  <Box className="h-px bg-border-200 dark:bg-border-700" />
                  {((stepsData?.programTemplateSteps as any[]) || []).length === 0 ? (
                    <Text className="text-typography-600 dark:text-gray-300">No steps found.</Text>
                  ) : (
                    ((stepsData?.programTemplateSteps as any[]) || []).map((s: any) => (
                      <Box key={s.id || s.sequenceIndex} className="p-3 rounded-lg border bg-background-50 dark:bg-background-100 border-border-200 dark:border-border-700">
                        <Text className="text-base font-semibold text-typography-900 dark:text-white">Step {s.sequenceIndex + 1}: {s.habit?.title || 'Habit'}</Text>
                        <Text className="text-typography-600 dark:text-gray-300">Duration: {s.durationDays} days</Text>
                        {s.habit?.shortDescription ? (
                          <Text className="text-typography-600 dark:text-gray-300">{s.habit.shortDescription}</Text>
                        ) : null}
                      </Box>
                    ))
                  )}
                </VStack>

                <Button className="bg-primary-600" onPress={handleEnroll}>
                  <ButtonText>Enroll</ButtonText>
                </Button>
              </>
            )}
          </VStack>
        </ScrollView>
      </VStack>
    </SafeAreaView>
  )
}


