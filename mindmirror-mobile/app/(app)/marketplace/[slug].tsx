import React from 'react'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { VStack } from '@/components/ui/vstack'
import { ScrollView } from '@/components/ui/scroll-view'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { AppBar } from '@/components/common/AppBar'
import { useLocalSearchParams, useRouter } from 'expo-router'
import { useApolloClient, useMutation, useQuery } from '@apollo/client'
import { PROGRAM_TEMPLATE_BY_SLUG, ASSIGN_PROGRAM_TO_USER, PROGRAM_STEPS, PROGRAM_ASSIGNMENTS, PROGRAM_STEP_LESSONS, UNENROLL_PROGRAM } from '@/services/api/habits'
import { Icon } from '@/components/ui/icon'
import { Pressable } from '@/components/ui/pressable'
import { CheckCircle, BookOpen, Clock } from 'lucide-react-native'
import { Button, ButtonText } from '@/components/ui/button'
import { useToast } from '@/components/ui/toast'
import { Toast, ToastDescription, ToastTitle } from '@/components/ui/toast'
import { useQuery as useApolloQuery } from '@apollo/client'

export default function ProgramDetailScreen() {
  const params = useLocalSearchParams<{ slug: string; from?: string }>()
  const slug = params.slug
  const from = params.from
  const router = useRouter()
  const client = useApolloClient()
  const { data, loading, error } = useQuery(PROGRAM_TEMPLATE_BY_SLUG, { variables: { slug }, fetchPolicy: 'cache-and-network' })
  const [assignProgramToUser] = useMutation(ASSIGN_PROGRAM_TO_USER)
  const [unenrollProgram] = useMutation(UNENROLL_PROGRAM)
  const { show } = useToast()

  const program = data?.programTemplateBySlug
  const { data: stepsData } = useQuery(PROGRAM_STEPS, {
    skip: !program?.id,
    variables: { programId: program?.id },
    fetchPolicy: 'cache-and-network',
  })
  const { data: assignmentsData } = useQuery(PROGRAM_ASSIGNMENTS, { fetchPolicy: 'cache-and-network' })
  const isEnrolled = !!(assignmentsData?.programAssignments || []).find((a: any) => a.programTemplateId === program?.id && a.status === 'active')
  const StepPreview = ({ stepId }: { stepId: string }) => {
    const { data: lessons } = useApolloQuery(PROGRAM_STEP_LESSONS, { variables: { programStepId: stepId } })
    const first = (lessons?.programStepLessons || [])[0]
    if (!first) return null
    return (
      <>
        {first.subtitle ? (
          <Text className="text-emerald-800/90 dark:text-emerald-200">{first.subtitle}</Text>
        ) : null}
        <Box className="h-px bg-emerald-200/60 dark:bg-emerald-800 my-1" />
        {first.summary ? (
          <Text className="text-emerald-900/80 dark:text-emerald-100/80">{first.summary}</Text>
        ) : null}
      </>
    )
  }

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
              <ToastDescription>You are enrolled. Loading today's tasks…</ToastDescription>
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

  const handleUnenroll = async () => {
    try {
      await unenrollProgram({ variables: { programId: program.id } })
      // Refresh key queries so UI updates immediately
      await client.refetchQueries({ include: [
        'ProgramAssignments',
        'TodaysTasks',
        'ProgramTemplateSteps',
        'ListProgramTemplates'
      ] })
      show({ placement: 'top', render: ({ id }) => (
        <Toast nativeID={`toast-${id}`} action="warning" variant="solid">
          <VStack>
            <ToastTitle>Unenrolled</ToastTitle>
            <ToastDescription>You can re-enroll anytime. Progress will restart.</ToastDescription>
          </VStack>
        </Toast>
      )})
      // Navigate back; fallback to home
      if (from === 'marketplace') {
        router.replace('/marketplace')
      } else if (from === 'programs' || from === 'resources') {
        router.replace('/programs')
      } else {
        router.replace('/journal')
      }
    } catch (e) {
      show({ placement: 'top', render: ({ id }) => (
        <Toast nativeID={`toast-${id}`} action="error" variant="solid">
          <VStack>
            <ToastTitle>Unenroll failed</ToastTitle>
            <ToastDescription>Please try again.</ToastDescription>
          </VStack>
        </Toast>
      )})
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
                  {program.subtitle ? (
                    <Text className="text-typography-600 dark:text-gray-300">{program.subtitle}</Text>
                  ) : null}
                  {program.description ? (
                    <Text className="text-typography-600 dark:text-gray-300">{program.description}</Text>
                  ) : null}
                </VStack>

                <VStack space="sm">
                  <Text className="text-xl font-bold text-typography-900 dark:text-white">Habits</Text>
                  <Box className="h-px bg-border-200 dark:bg-border-700" />
                  {((stepsData?.programTemplateSteps as any[]) || []).length === 0 ? (
                    <Text className="text-typography-600 dark:text-gray-300">No steps found.</Text>
                  ) : (
                    ((stepsData?.programTemplateSteps as any[]) || []).map((s: any) => (
                      <Pressable key={s.id || s.sequenceIndex} onPress={() => router.push(`/marketplace/${slug}/step/${s.id || s.sequenceIndex}?programId=${encodeURIComponent(program.id)}&habitId=${encodeURIComponent(s.habit?.id || '')}&returnTo=${encodeURIComponent(`/marketplace/${slug}`)}`)}>
                      <Box className="p-5 rounded-2xl border bg-gradient-to-br from-emerald-50 to-emerald-100 dark:from-emerald-950 dark:to-emerald-900 border-emerald-200 dark:border-emerald-800">
                        <VStack space="xs">
                          <Text className="text-base font-semibold text-emerald-900 dark:text-emerald-100">{s.habit?.title || 'Habit'}</Text>
                          <StepPreview stepId={s.id} />
                          <VStack className="flex-row items-center" space="xs">
                            <Icon as={Clock} size="sm" className="text-emerald-700 dark:text-emerald-300" />
                            <Text className="text-emerald-800 dark:text-emerald-200 font-semibold">{s.durationDays} days</Text>
                          </VStack>
                          {typeof s.started !== 'undefined' ? (
                            <Text className="text-emerald-800/80 dark:text-emerald-200/90 mt-1">
                              {s.started ? `In progress: ${s.daysCompleted}/${s.totalDays}` : 'Not started'}
                            </Text>
                          ) : null}
                        </VStack>
                      </Box>
                      </Pressable>
                    ))
                  )}
                </VStack>

                <VStack space="sm">
                  <Button className={`bg-primary-600 ${isEnrolled ? 'opacity-60' : ''}`} onPress={isEnrolled ? undefined : handleEnroll} disabled={isEnrolled}>
                    <ButtonText>{isEnrolled ? 'Enrolled' : 'Enroll'}</ButtonText>
                  </Button>
                  {isEnrolled && (
                    <Button className="bg-red-600" onPress={handleUnenroll}>
                      <ButtonText>Unenroll</ButtonText>
                    </Button>
                  )}
                </VStack>
              </>
            )}
          </VStack>
        </ScrollView>
      </VStack>
    </SafeAreaView>
  )
}


