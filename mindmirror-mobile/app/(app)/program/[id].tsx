import React from 'react'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { AppBar } from '@/components/common/AppBar'
import { VStack } from '@/components/ui/vstack'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { Pressable } from '@/components/ui/pressable'
import { ScrollView } from '@/components/ui/scroll-view'
import { useLocalSearchParams, useRouter } from 'expo-router'
import { useProgram, useDeleteProgram, useEnrollInProgram, useMyEnrollments, useUpdateEnrollmentStatus } from '@/services/api/practices'
import GlobalFab from '@/components/common/GlobalFab'
import { useAuth } from '@/features/auth/context/AuthContext'
import { Button, ButtonText } from '@/components/ui/button'
import { HStack } from '@/components/ui/hstack'
import { View } from 'react-native'
import { useToast } from '@/components/ui/toast'
import { Toast, ToastTitle, ToastDescription } from '@/components/ui/toast'

export default function ProgramDetailsScreen() {
  const { id } = useLocalSearchParams<{ id: string }>()
  const router = useRouter()
  const { data, loading } = useProgram(id || '')
  const [deleteProgram] = useDeleteProgram()
  const [enrollProgram] = useEnrollInProgram()
  const [updateEnrollmentStatus] = useUpdateEnrollmentStatus()
  const { session } = useAuth()
  const enrollmentsQ = useMyEnrollments(session?.user?.id)
  const [showConfirmUnenroll, setShowConfirmUnenroll] = React.useState(false)
  const { show, close } = useToast()
  const p = data?.program

  const isEnrolled = React.useMemo(() => {
    const rows = enrollmentsQ.data?.enrollments || []
    return !!rows.find((e: any) => e.program_id === p?.id_ && (e.status || '').toLowerCase() === 'active')
  }, [enrollmentsQ.data?.enrollments, p?.id_])

  const onDelete = async () => {
    try {
      await deleteProgram({ variables: { id }, refetchQueries: ['Programs'], awaitRefetchQueries: true })
      show({ placement: 'top', render: ({ id }) => (
        <Toast nativeID={`toast-${id}`} action="success" variant="solid">
          <VStack>
            <ToastTitle>Program deleted</ToastTitle>
            <ToastDescription>Refreshing list…</ToastDescription>
          </VStack>
        </Toast>
      )})
      try {
        router.back()
      } catch {
      router.replace('/programs?reload=1')
      }
    } catch {}
  }

  const onEnroll = async () => {
    try {
      await enrollProgram({ variables: { programId: p?.id_ }, refetchQueries: ['Programs', 'Enrollments', 'MyUpcomingPractices', 'TodaysWorkouts', 'TodaysSchedulables'], awaitRefetchQueries: true })
      show({ placement: 'top', render: ({ id }) => (
        <Toast nativeID={`toast-${id}`} action="success" variant="solid">
          <VStack>
            <ToastTitle>Enrolled</ToastTitle>
            <ToastDescription>Scheduled today’s workout. Updating your home…</ToastDescription>
          </VStack>
        </Toast>
      )})
      setTimeout(() => { router.replace('/programs?reload=1') }, 500)
    } catch {}
  }

  const onUnenroll = async () => {
    try {
      const rows = enrollmentsQ.data?.enrollments || []
      const en = rows.find((e: any) => e.program_id === p?.id_ && (e.status || '').toLowerCase() === 'active')
      if (en?.id_) {
        await updateEnrollmentStatus({ variables: { enrollmentId: en.id_, status: 'CANCELLED' },
          refetchQueries: ['Enrollments', 'Programs', 'Program', 'MyUpcomingPractices', 'Workouts', 'TodaysWorkouts'], awaitRefetchQueries: true })
      }
      setShowConfirmUnenroll(false)
      router.replace('/programs?reload=1')
    } catch {}
  }

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title={p?.name || 'Program'} showBackButton onBackPress={() => { try { router.back() } catch { router.replace('/programs?reload=1') } }} />
        <ScrollView className="flex-1">
          <VStack className="w-full max-w-screen-md mx-auto px-6 py-6" space="lg">
            {loading ? (
              <Text className="text-typography-600">Loading…</Text>
            ) : !p ? (
              <Text className="text-typography-600">Not found</Text>
            ) : (
              <>
                <VStack space="xs">
                  <Text className="text-2xl font-bold text-typography-900 dark:text-white">{p.name}</Text>
                  {p.description ? <Text className="text-typography-600 dark:text-gray-300">{p.description}</Text> : null}
                </VStack>

                <VStack space="sm">
                  <Text className="text-lg font-semibold text-typography-900 dark:text-white">Sequence</Text>
                  {(p.practiceLinks || []).length === 0 ? (
                    <Text className="text-typography-600 dark:text-gray-300">No workouts added</Text>
                  ) : (
                    (p.practiceLinks || []).map((l: any, i: number) => (
                      <Pressable key={i} onPress={() => router.push(`/(app)/template/${l.practiceTemplate?.id_}?returnTo=${encodeURIComponent(`/(app)/program/${p.id_}`)}`)}>
                        <Box className="p-4 rounded-xl border border-border-200 bg-background-50 dark:bg-background-100">
                          <VStack>
                            <Text className="font-semibold text-typography-900 dark:text-white">{i + 1}. {l.practiceTemplate?.title || 'Workout'}</Text>
                            <Text className="text-typography-600 dark:text-gray-300">Rest days after: {l.intervalDaysAfter}</Text>
                          </VStack>
                        </Box>
                      </Pressable>
                    ))
                  )}
                </VStack>

                {/* Bottom actions */}
                <VStack space="sm">
                  {isEnrolled ? (
                    <Button className="w-full bg-transparent border border-red-300" onPress={() => setShowConfirmUnenroll(true)}>
                      <ButtonText className="text-red-700">Unenroll</ButtonText>
                    </Button>
                  ) : (
                    <Button className="bg-primary-600 w-full" onPress={onEnroll}>
                      <ButtonText>Enroll</ButtonText>
                    </Button>
                  )}
                  <Button className="bg-red-600 w-full" onPress={onDelete}>
                    <ButtonText>Delete Program</ButtonText>
                  </Button>
                </VStack>
              </>
            )}
          </VStack>
        </ScrollView>
      </VStack>
      <GlobalFab onPress={() => router.push('/(app)/workout-create')} />
      {showConfirmUnenroll ? (
        <View style={{ position: 'absolute', left: 0, right: 0, top: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.45)', justifyContent: 'center', alignItems: 'center', padding: 24 }}>
          <Box className="w-full max-w-md p-5 rounded-2xl bg-background-0 border border-border-200 dark:border-border-700">
            <VStack space="md">
              <Text className="text-xl font-bold text-typography-900 dark:text-white">Unenroll from this program?</Text>
              <Text className="text-typography-700 dark:text-gray-300">You’ll lose today’s schedule for this program. You can re‑enroll anytime and progress will restart.</Text>
              <HStack className="justify-end space-x-3">
                <Button className="bg-gray-600" onPress={() => setShowConfirmUnenroll(false)}>
                  <ButtonText>Cancel</ButtonText>
                </Button>
                <Button className="bg-red-600" onPress={onUnenroll}>
                  <ButtonText>Confirm</ButtonText>
                </Button>
              </HStack>
            </VStack>
          </Box>
        </View>
      ) : null}
    </SafeAreaView>
  )
} 