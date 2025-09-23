import React, { useState, useMemo } from 'react'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { VStack } from '@/components/ui/vstack'
import { HStack } from '@/components/ui/hstack'
import { ScrollView } from '@/components/ui/scroll-view'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { AppBar } from '@/components/common/AppBar'
import Markdown from 'react-native-markdown-display'
import { useLocalSearchParams, useRouter } from 'expo-router'
import { useUserById, useTerminateCoachingForClient } from '@/services/api/users'
import { useWorkoutsForUser, usePrograms as useWorkoutPrograms, useMyEnrollments, useEnrollUserInProgram, useUpdateEnrollmentStatus } from '@/services/api/practices'
import GlobalFab from '@/components/common/GlobalFab'
import { Alert, AlertIcon, AlertText } from '@/components/ui/alert'
import { AlertCircleIcon } from 'lucide-react-native'
import { Avatar, AvatarFallbackText, AvatarImage, AvatarBadge } from '@/components/ui/avatar'
import { Badge, BadgeText } from '@/components/ui/badge'
import { Button, ButtonText } from '@/components/ui/button'
import { Pressable } from '@/components/ui/pressable'
import { gql, useQuery } from '@apollo/client'
import { Input, InputField } from '@/components/ui/input'
import { Modal, Platform, KeyboardAvoidingView, FlatList, Pressable as RNPressable, View, TextInput, Text as RNText } from 'react-native'

export default function ClientProfileScreen() {
  const { id } = useLocalSearchParams<{ id: string }>()
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<'workouts' | 'meals'>('workouts')
  const [removing, setRemoving] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [assigningProgramId, setAssigningProgramId] = useState<string | null>(null)
  const [unassigningEnrollmentId, setUnassigningEnrollmentId] = useState<string | null>(null)
  const [repeatCounts, setRepeatCounts] = useState<{[programId: string]: string}>({})
  
  // Program search modal state
  const [isProgramPickerOpen, setProgramPickerOpen] = useState(false)
  const [programSearchTerm, setProgramSearchTerm] = useState('')
  const [selectedProgram, setSelectedProgram] = useState<any>(null)

  const { data: clientData, loading: clientLoading, error: clientError, refetch: refetchClient } = useUserById(id || '')
  const { data: workoutsData, loading: workoutsLoading, error: workoutsError } = useWorkoutsForUser(
    id || '', 
    undefined, // dateFrom
    undefined, // dateTo
    'completed'  // status
  )

  // Workouts programs and client enrollments
  const programsQ = useWorkoutPrograms()
  const enrollmentsQ = useMyEnrollments(id || '')
  const [enrollUserInProgram] = useEnrollUserInProgram()
  const [updateEnrollmentStatus] = useUpdateEnrollmentStatus()

  const client = clientData?.userById
  const workouts = workoutsData?.workoutsForUser || []
  const programs = programsQ.data?.programs || [] // Workout programs only
  const enrollments = enrollmentsQ.data?.enrollments || []
  const activeEnrollments = useMemo(() => (enrollments || []).filter((e: any) => (e.status || '').toLowerCase() === 'active'), [enrollments])

  const activeProgramIds = useMemo(() => new Set<string>(activeEnrollments.map((e: any) => e.program_id)), [activeEnrollments])
  const programIdToProgram = useMemo(() => {
    const map = new Map<string, any>()
    for (const p of programs) map.set(p.id_, p)
    return map
  }, [programs])

  // Filter programs based on search term
  const filteredPrograms = useMemo(() => {
    if (!programSearchTerm.trim()) return programs
    const term = programSearchTerm.toLowerCase()
    return programs.filter((p: any) => 
      p.name?.toLowerCase().includes(term) || 
      p.description?.toLowerCase().includes(term)
    )
  }, [programs, programSearchTerm])

  const handleAssignProgram = async (programId: string) => {
    if (!id) return
    try {
      setAssigningProgramId(programId)
      const input = {
        programId,
        userId: id,
        repeatCount: parseInt(repeatCounts[programId] || '1') || 1
      }
      await enrollUserInProgram({ variables: { input } })
      await enrollmentsQ.refetch()
      
      // Reset modal state
      setProgramPickerOpen(false)
      setSelectedProgram(null)
      setProgramSearchTerm('')
    } finally {
      setAssigningProgramId(null)
    }
  }

  const handleUnassignEnrollment = async (enrollmentId: string) => {
    try {
      setUnassigningEnrollmentId(enrollmentId)
      await updateEnrollmentStatus({ variables: { enrollmentId, status: 'CANCELLED' } })
      await enrollmentsQ.refetch()
    } finally {
      setUnassigningEnrollmentId(null)
    }
  }

  // Get last 7 days for recent workouts
  const sevenDaysAgo = new Date()
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)
  const recentWorkouts = workouts.filter((workout: any) => 
    new Date(workout.date) >= sevenDaysAgo
  )

  // Meals: recent (last 7 days)
  const toUtcDateStr = (d: Date) => {
    const yy = d.getUTCFullYear()
    const mm = String(d.getUTCMonth() + 1).padStart(2, '0')
    const dd = String(d.getUTCDate()).padStart(2, '0')
    return `${yy}-${mm}-${dd}`
  }
  const mealsStart = useMemo(() => toUtcDateStr(sevenDaysAgo), [])
  const mealsEnd = useMemo(() => {
    const next = new Date()
    next.setDate(next.getDate() + 1)
    return toUtcDateStr(next)
  }, [])

  const LIST_MEALS = gql`
    query MealsByUser($userId: String!, $start: String!, $end: String!, $limit: Int) {
      mealsByUserAndDateRange(userId: $userId, startDate: $start, endDate: $end, limit: $limit) {
        id_
        name
        type
        date
        notes
        mealFoods {
          id_
          quantity
          servingUnit
          foodItem { id_ name calories protein carbohydrates fat }
        }
      }
    }
  `
  const mealsQ = useQuery(LIST_MEALS, { skip: !id, variables: { userId: id, start: mealsStart, end: mealsEnd, limit: 50 }, fetchPolicy: 'cache-and-network' })
  const meals = mealsQ.data?.mealsByUserAndDateRange || []

  const [terminateCoaching] = useTerminateCoachingForClient()
  const handleRemoveClient = async () => {
    if (!id || removing === 'loading') return
    setRemoving('loading')
    try {
      await terminateCoaching({ variables: { clientId: id } })
      setRemoving('success')
      await refetchClient()
    } catch (e) {
      setRemoving('error')
    }
  }

  if (clientLoading) {
    return (
      <SafeAreaView className="h-full w-full">
        <VStack className="h-full w-full bg-background-0">
          <AppBar title="Client Profile" showBackButton />
          <VStack className="flex-1 justify-center items-center">
            <Text className="text-typography-600 dark:text-gray-300">Loading client...</Text>
          </VStack>
        </VStack>
      </SafeAreaView>
    )
  }

  if (clientError || !client) {
    return (
      <SafeAreaView className="h-full w-full">
        <VStack className="h-full w-full bg-background-0">
          <AppBar title="Client Profile" showBackButton />
          <VStack className="flex-1 justify-center items-center px-6">
            <Alert action="error" variant="solid">
              <AlertIcon as={AlertCircleIcon} />
              <AlertText>Failed to load client profile</AlertText>
            </Alert>
          </VStack>
        </VStack>
      </SafeAreaView>
    )
  }

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title="Client Profile" showBackButton />
        <ScrollView showsVerticalScrollIndicator={false} className="flex-1">
          <VStack className="w-full max-w-screen-md mx-auto px-6 py-6" space="lg">
            {/* Client Header */}
            <VStack space="md" className="items-center">
              <Avatar size="xl">
                <AvatarFallbackText>
                  {(client.firstName?.[0] || client.email?.[0] || client.supabaseId.substring(0, 2)).toUpperCase()}
                </AvatarFallbackText>
                <AvatarBadge />
              </Avatar>
              <VStack space="xs" className="items-center">
                <Text className="text-xl font-bold text-typography-900 dark:text-white">
                  {client.firstName && client.lastName ? `${client.firstName} ${client.lastName}` : (client.email || `Client ${client.supabaseId.substring(0, 8)}...`)}
                </Text>
                <Text className="text-typography-600 dark:text-gray-300 text-sm">
                  Member since {new Date(client.createdAt).toLocaleDateString()}
                </Text>
                <Badge variant="solid" className="bg-green-100 border-green-200">
                  <BadgeText className="text-green-800">Active Client</BadgeText>
                </Badge>
              </VStack>
            </VStack>

            {/* Quick Stats */}
            <HStack space="md" className="justify-around">
              <VStack className="items-center">
                <Text className="text-2xl font-bold text-typography-900 dark:text-white">
                  {recentWorkouts.length}
                </Text>
                <Text className="text-typography-600 dark:text-gray-300 text-sm text-center">
                  Workouts (7d)
                </Text>
              </VStack>
              <VStack className="items-center">
                <Text className="text-2xl font-bold text-typography-900 dark:text-white">
                  {workouts.length}
                </Text>
                <Text className="text-typography-600 dark:text-gray-300 text-sm text-center">
                  Total Workouts
                </Text>
              </VStack>
              <VStack className="items-center">
                <Text className="text-2xl font-bold text-typography-900 dark:text-white">
                  {meals.length}
                </Text>
                <Text className="text-typography-600 dark:text-gray-300 text-sm text-center">
                  Meals (7d)
                </Text>
              </VStack>
            </HStack>

            {/* Tab Navigation */}
            <HStack space="sm" className="bg-background-50 dark:bg-background-100 rounded-lg p-1">
              <Button
                variant={activeTab === 'workouts' ? 'solid' : 'outline'}
                className={`flex-1 ${activeTab === 'workouts' ? 'bg-primary-600' : 'bg-transparent border-0'}`}
                onPress={() => setActiveTab('workouts')}
              >
                <ButtonText className={activeTab === 'workouts' ? 'text-white' : 'text-typography-600'}>
                  Workouts
                </ButtonText>
              </Button>
              <Button
                variant={activeTab === 'meals' ? 'solid' : 'outline'}
                className={`flex-1 ${activeTab === 'meals' ? 'bg-primary-600' : 'bg-transparent border-0'}`}
                onPress={() => setActiveTab('meals')}
              >
                <ButtonText className={activeTab === 'meals' ? 'text-white' : 'text-typography-600'}>
                  Meals
                </ButtonText>
              </Button>
            </HStack>

            {/* Tab Content */}
            {activeTab === 'workouts' ? (
              <VStack space="md">
                <Text className="text-lg font-semibold text-typography-900 dark:text-white">
                  Completed Workouts
                </Text>
                {workoutsLoading ? (
                  <Text className="text-typography-600 dark:text-gray-300">Loading workouts...</Text>
                ) : workoutsError ? (
                  <Alert action="error" variant="solid">
                    <AlertIcon as={AlertCircleIcon} />
                    <AlertText>Failed to load workouts</AlertText>
                  </Alert>
                ) : workouts.length === 0 ? (
                  <VStack space="md" className="items-center py-8">
                    <Text className="text-typography-600 dark:text-gray-300 text-center">
                      No completed workouts yet.
                    </Text>
                  </VStack>
                ) : (
                  <VStack space="md">
                    {workouts.slice(0, 10).map((workout: any) => (
                      <Pressable key={workout.id_} onPress={() => router.push(`/(app)/workout/${workout.id_}`)}>
                        <Box 
                          className="p-4 rounded-xl border bg-background-50 dark:bg-background-100 border-border-200 dark:border-border-700"
                        >
                          <VStack space="xs">
                            <HStack className="items-center justify-between">
                              <Text className="text-base font-semibold text-typography-900 dark:text-white">
                                {workout.title || 'Workout'}
                              </Text>
                              <Text className="text-typography-500 dark:text-gray-400 text-sm">
                                {new Date(workout.date).toLocaleDateString()}
                              </Text>
                            </HStack>
                            {workout.description && (
                              <Box className="rounded border border-border-200 bg-white/60 dark:bg-background-50 p-2">
                                <Markdown>{workout.description}</Markdown>
                              </Box>
                            )}
                            <HStack className="items-center justify-between">
                              <Badge variant="solid" className="bg-green-100 border-green-200">
                                <BadgeText className="text-green-800">Completed</BadgeText>
                              </Badge>
                              {workout.completedAt && (
                                <Text className="text-typography-500 dark:text-gray-400 text-xs">
                                  Completed {new Date(workout.completedAt).toLocaleString()}
                                </Text>
                              )}
                            </HStack>
                          </VStack>
                        </Box>
                      </Pressable>
                    ))}
                    {workouts.length > 10 && (
                      <Text className="text-typography-500 dark:text-gray-400 text-sm text-center">
                        Showing 10 of {workouts.length} workouts
                      </Text>
                    )}
                  </VStack>
                )}

                {/* Assign Workout Program */}
                <VStack space="sm" className="mt-6">
                  <Text className="text-lg font-semibold text-typography-900 dark:text-white">Assign Program</Text>
                  
                  {programsQ.loading ? (
                    <Text className="text-typography-600 dark:text-gray-300">Loading programs…</Text>
                  ) : programsQ.error ? (
                    <Text className="text-red-600 dark:text-red-400">Failed to load programs</Text>
                  ) : programs.length === 0 ? (
                    <Text className="text-typography-600 dark:text-gray-300">No workout programs available.</Text>
                  ) : (
                    <VStack space="sm">
                      {/* Search button */}
                      <Pressable 
                        onPress={() => setProgramPickerOpen(true)} 
                        className="p-3 rounded-lg border border-indigo-300 dark:border-indigo-700 bg-white dark:bg-indigo-950"
                      >
                        <Text className="text-indigo-700 dark:text-indigo-200 font-semibold text-center">
                          Search Programs
                        </Text>
                      </Pressable>

                      {/* Selected program display */}
                      {selectedProgram && (
                        <VStack space="sm" className="p-3 rounded-lg border bg-background-50 dark:bg-background-100 border-border-200 dark:border-border-700">
                          <HStack className="items-center justify-between">
                            <VStack className="flex-1">
                              <Text className="text-typography-900 dark:text-white font-medium">{selectedProgram.name}</Text>
                              {selectedProgram.description ? (
                                <Box className="mt-2">
                                  <Markdown>{selectedProgram.description}</Markdown>
                                </Box>
                              ) : null}
                            </VStack>
                            <Button
                              size="sm"
                              variant={activeProgramIds.has(selectedProgram.id_) ? 'outline' : 'solid'}
                              disabled={assigningProgramId === selectedProgram.id_ || activeProgramIds.has(selectedProgram.id_)}
                              onPress={() => handleAssignProgram(selectedProgram.id_)}
                            >
                              <ButtonText>
                                {activeProgramIds.has(selectedProgram.id_) ? 'Assigned' : (assigningProgramId === selectedProgram.id_ ? 'Assigning…' : 'Assign')}
                              </ButtonText>
                            </Button>
                          </HStack>
                          {!activeProgramIds.has(selectedProgram.id_) && (
                            <VStack space="xs">
                              <Text className="text-typography-700 dark:text-white text-sm font-medium">Repeat Count</Text>
                              <Input className="bg-background-0 dark:bg-background-50" size="sm">
                                <InputField 
                                  placeholder="1" 
                                  value={repeatCounts[selectedProgram.id_] || '1'} 
                                  onChangeText={(value) => setRepeatCounts(prev => ({...prev, [selectedProgram.id_]: value}))}
                                  keyboardType="numeric"
                                />
                              </Input>
                            </VStack>
                          )}
                        </VStack>
                      )}
                    </VStack>
                  )}
                </VStack>

                {/* Current Assignments */}
                <VStack space="sm" className="mt-4">
                  <Text className="text-lg font-semibold text-typography-900 dark:text-white">Current Assignments</Text>
                  {enrollmentsQ.loading ? (
                    <Text className="text-typography-600 dark:text-gray-300">Loading assignments…</Text>
                  ) : activeEnrollments.length === 0 ? (
                    <Text className="text-typography-600 dark:text-gray-300">No active assignments.</Text>
                  ) : (
                    <VStack space="sm">
                      {activeEnrollments.map((e: any) => {
                        const program = programIdToProgram.get(e.program_id)
                        return (
                          <HStack key={e.id_} className="items-center justify-between p-3 rounded-lg border bg-background-50 dark:bg-background-100 border-border-200 dark:border-border-700">
                            <VStack>
                              <Text className="text-typography-900 dark:text-white font-medium">{program?.name || 'Program'}</Text>
                              <Text className="text-typography-600 dark:text-gray-300 text-sm">Status: {e.status}</Text>
                            </VStack>
                            <Button
                              size="sm"
                              variant="outline"
                              disabled={unassigningEnrollmentId === e.id_}
                              onPress={() => handleUnassignEnrollment(e.id_)}
                            >
                              <ButtonText>{unassigningEnrollmentId === e.id_ ? 'Unassigning…' : 'Unassign'}</ButtonText>
                            </Button>
                          </HStack>
                        )
                      })}
                    </VStack>
                  )}
                </VStack>

                {/* Danger zone */}
                <VStack className="mt-8" space="xs">
                  <Text className="text-typography-700">Danger zone</Text>
                  <Button
                    variant="outline"
                    className="border-red-300"
                    onPress={handleRemoveClient}
                    disabled={removing === 'loading' || removing === 'success'}
                  >
                    <ButtonText className="text-red-700">
                      {removing === 'loading' ? 'Removing…' : removing === 'success' ? 'Removed' : 'Remove Client'}
                    </ButtonText>
                  </Button>
                </VStack>
              </VStack>
            ) : (
              <VStack space="md">
                <Text className="text-lg font-semibold text-typography-900 dark:text-white">
                  Recent Meals (7d)
                </Text>
                {mealsQ.loading ? (
                  <Text className="text-typography-600 dark:text-gray-300">Loading meals...</Text>
                ) : mealsQ.error ? (
                  <Alert action="error" variant="solid">
                    <AlertIcon as={AlertCircleIcon} />
                    <AlertText>Failed to load meals</AlertText>
                  </Alert>
                ) : meals.length === 0 ? (
                  <VStack space="md" className="items-center py-8">
                    <Text className="text-typography-600 dark:text-gray-300 text-center">
                      No meals logged in the last 7 days.
                    </Text>
                  </VStack>
                ) : (
                  <VStack space="sm">
                    {meals.map((m: any) => {
                      const kcal = Math.round((m.mealFoods || []).reduce((acc: number, mf: any) => acc + (mf.foodItem?.calories || 0), 0))
                      return (
                        <Box key={m.id_} className="p-4 rounded-xl border bg-background-50 dark:bg-background-100 border-border-200 dark:border-border-700">
                          <HStack className="items-center justify-between">
                            <VStack>
                              <Text className="text-base font-semibold text-typography-900 dark:text-white">{m.name}</Text>
                              <Text className="text-typography-500 dark:text-gray-400 text-sm">{m.type} • {new Date(m.date).toLocaleDateString()}</Text>
                            </VStack>
                            <Text className="text-indigo-700 font-semibold">{kcal} cal</Text>
                          </HStack>
                        </Box>
                      )
                    })}
                  </VStack>
                )}
              </VStack>
            )}
          </VStack>
        </ScrollView>
      </VStack>
      <GlobalFab />

      {/* Program search modal */}
      <Modal visible={isProgramPickerOpen} transparent animationType="fade" onRequestClose={() => { setProgramPickerOpen(false); setProgramSearchTerm('') }}>
        <View style={{ flex: 1, alignItems: 'center' }}>
          <RNPressable style={{ position: 'absolute', top: 0, bottom: 0, left: 0, right: 0, backgroundColor: 'rgba(0,0,0,0.4)' }} onPress={() => { setProgramPickerOpen(false); setProgramSearchTerm('') }} />
          <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={{ width: '100%', alignItems: 'center', paddingTop: Platform.OS === 'ios' ? 60 : 30 }}>
            <View style={{ width: '96%', maxWidth: 560, maxHeight: 520, borderRadius: 16, backgroundColor: '#fff', padding: 16, flexDirection: 'column', alignSelf: 'center', borderWidth: 1, borderColor: '#e5e7eb' }}>
              <RNText style={{ fontSize: 18, fontWeight: '600', marginBottom: 8 }}>Select Program</RNText>
              <View style={{ marginBottom: 12 }}>
                <TextInput 
                  placeholder="Search programs…" 
                  value={programSearchTerm} 
                  onChangeText={setProgramSearchTerm} 
                  autoFocus 
                  style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10 }} 
                />
              </View>
              <View style={{ flex: 1, minHeight: 240, overflow: 'hidden' }}>
                <FlatList
                  keyboardDismissMode="on-drag"
                  keyboardShouldPersistTaps="handled"
                  data={filteredPrograms}
                  keyExtractor={(item: any) => item.id_}
                  renderItem={({ item }) => (
                    <RNPressable onPress={() => {
                      setSelectedProgram(item)
                      setProgramPickerOpen(false)
                      setProgramSearchTerm('')
                    }} style={{ paddingVertical: 10, borderTopWidth: 1, borderTopColor: '#e5e7eb' }}>
                      <View style={{ flexDirection: 'column' }}>
                        <RNText style={{ fontWeight: '600', marginBottom: 4 }}>{item.name}</RNText>
                        {item.description ? (
                          <View style={{ backgroundColor: '#f9fafb', padding: 8, borderRadius: 6, borderWidth: 1, borderColor: '#e5e7eb' }}>
                            <Markdown>{item.description}</Markdown>
                          </View>
                        ) : null}
                        {activeProgramIds.has(item.id_) && (
                          <View style={{ marginTop: 4, paddingVertical: 2, paddingHorizontal: 8, borderRadius: 999, backgroundColor: '#dcfce7', borderWidth: 1, borderColor: '#bbf7d0', alignSelf: 'flex-start' }}>
                            <RNText style={{ color: '#16a34a', fontWeight: '700', fontSize: 12 }}>Already Assigned</RNText>
                          </View>
                        )}
                      </View>
                    </RNPressable>
                  )}
                  ListEmptyComponent={
                    <View style={{ paddingVertical: 16, alignItems: 'center' }}>
                      <RNText style={{ color: '#6b7280' }}>
                        {programSearchTerm.trim().length === 0 ? 'Type to search programs' : 'No programs found'}
                      </RNText>
                    </View>
                  }
                  style={{ flex: 1 }}
                  contentContainerStyle={{ paddingBottom: 8 }}
                />
              </View>
              <View style={{ flexDirection: 'row', justifyContent: 'flex-end', marginTop: 8 }}>
                <RNPressable onPress={() => { setProgramPickerOpen(false); setProgramSearchTerm('') }} style={{ paddingVertical: 8, paddingHorizontal: 12, borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8 }}>
                  <RNText style={{ color: '#374151', fontWeight: '600' }}>Close</RNText>
                </RNPressable>
              </View>
            </View>
          </KeyboardAvoidingView>
        </View>
      </Modal>
    </SafeAreaView>
  )
} 