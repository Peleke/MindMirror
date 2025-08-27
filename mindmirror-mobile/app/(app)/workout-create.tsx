import React, { useEffect, useMemo, useState } from 'react'
import { Modal, Platform, KeyboardAvoidingView, FlatList, Pressable as RNPressable, View, TextInput, Text as RNText } from 'react-native'
import { useRouter } from 'expo-router'
import dayjs from 'dayjs'
import { useCreateAdHocWorkout } from '@/services/api/practices'
import { useLazySearchMovements } from '@/services/api/movements'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { VStack } from '@/components/ui/vstack'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { Input, InputField } from '@/components/ui/input'
import { Pressable } from '@/components/ui/pressable'
import { AppBar } from '@/components/common/AppBar'

// Minimal enums to map to server values
const BLOCKS = ['warmup', 'workout', 'cooldown', 'other'] as const

// Local types for builder state
type SetDraft = {
  position: number
  reps?: number
  duration?: number
  loadValue?: number
  loadUnit?: string
  restDuration?: number
}

type MovementDraft = {
  name: string
  position: number
  metricUnit: 'iterative' | 'temporal' | 'breath' | 'other'
  metricValue: number
  description?: string
  movementClass?: 'conditioning' | 'power' | 'strength' | 'mobility' | 'other'
  prescribedSets?: number
  restDuration?: number
  videoUrl?: string
  exerciseId?: string
  movementId?: string
  sets: SetDraft[]
}

type PrescriptionDraft = {
  name: string
  position: number
  block: typeof BLOCKS[number]
  prescribedRounds: number
  movements: MovementDraft[]
}

export default function WorkoutCreateScreen() {
  const router = useRouter()
  const [title, setTitle] = useState('')
  const [date, setDate] = useState(dayjs().format('YYYY-MM-DD'))
  const [createWorkout, { loading }] = useCreateAdHocWorkout()

  // Pre-create Warmup, Workout, Cooldown blocks
  const [prescriptions, setPrescriptions] = useState<PrescriptionDraft[]>([
    { name: 'Warmup', position: 1, block: 'warmup', prescribedRounds: 1, movements: [] },
    { name: 'Workout', position: 2, block: 'workout', prescribedRounds: 1, movements: [] },
    { name: 'Cooldown', position: 3, block: 'cooldown', prescribedRounds: 1, movements: [] },
  ])

  // Movement picker modal
  const [isPickerOpen, setPickerOpen] = useState(false)
  const [pickerForBlock, setPickerForBlock] = useState<number | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [runSearch, { data: searchData, loading: searching }] = useLazySearchMovements()

  // Debounced search (DB-only results)
  useEffect(() => {
    if (!isPickerOpen) return
    const term = (searchTerm || '').trim()
    const h = setTimeout(() => {
      if (term.length === 0) return
      runSearch({ variables: { searchTerm: term, limit: 25 } })
    }, 250)
    return () => clearTimeout(h)
  }, [isPickerOpen, searchTerm, runSearch])

  const searchResults = useMemo(() => {
    const list = searchData?.searchMovements ?? []
    // DB-only
    return list.filter((r: any) => r?.isExternal === false)
  }, [searchData])

  const addMovementToPrescription = (pIndex: number, m: any) => {
    setPrescriptions((prev) => {
      const copy: PrescriptionDraft[] = [...prev]
      const p = copy[pIndex]
      if (!p) return prev
      const nextPos = p.movements.length + 1
      const newMovement: MovementDraft = {
        name: m.name,
        position: nextPos,
        metricUnit: 'iterative',
        metricValue: 1,
        movementClass: 'other',
        prescribedSets: 3,
        restDuration: 60,
        videoUrl: m.shortVideoUrl ?? undefined,
        sets: [
          { position: 1, reps: 10, restDuration: 60, loadUnit: 'bodyweight' },
        ],
      }
      if (m.id_) newMovement.movementId = m.id_
      p.movements = [...p.movements, newMovement]
      copy[pIndex] = p
      return copy
    })
  }

  const addSetToMovement = (pIndex: number, mIndex: number) => {
    setPrescriptions((prev) => {
      const copy: PrescriptionDraft[] = [...prev]
      const p = copy[pIndex]
      if (!p) return prev
      const mov = p.movements[mIndex]
      if (!mov) return prev
      const nextPos = mov.sets.length + 1
      const newSet: SetDraft = { position: nextPos, reps: 10, restDuration: 60, loadUnit: 'bodyweight' }
      mov.sets = [...mov.sets, newSet]
      p.movements = p.movements.map((mm, i) => (i === mIndex ? mov : mm))
      copy[pIndex] = p
      return copy
    })
  }

  const onSubmit = async () => {
    if (!title) {
      alert('Please enter a workout title')
      return
    }

    const gqlPrescriptions = prescriptions.map((p) => ({
      name: p.name,
      position: p.position,
      block: p.block,
      prescribed_rounds: p.prescribedRounds,
      description: '',
      movements: p.movements.map((m) => ({
        name: m.name,
        position: m.position,
        metric_unit: m.metricUnit,
        metric_value: m.metricValue,
        description: m.description ?? '',
        movement_class: m.movementClass,
        prescribed_sets: m.prescribedSets,
        rest_duration: m.restDuration,
        video_url: m.videoUrl,
        exercise_id: m.exerciseId,
        sets: m.sets.map((s) => ({
          position: s.position,
          reps: s.reps,
          duration: s.duration,
          load_value: s.loadValue,
          load_unit: s.loadUnit,
          rest_duration: s.restDuration,
        })),
      })),
    }))

    try {
      await createWorkout({ variables: { input: { title, date, prescriptions: gqlPrescriptions } } })
      router.back()
    } catch (e: any) {
      alert(e?.message || 'Failed to create workout')
    }
  }

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title="Create Workout" showBackButton onBackPress={() => router.back()} />
        <VStack className="flex-1 w-full max-w-screen-md mx-auto px-6 py-6" space="lg">
          <VStack space="sm">
            <Text className="text-2xl font-bold text-typography-900 dark:text-white">Workout Details</Text>
            <Text className="text-typography-600 dark:text-gray-300">Set a title and date, then add movements to each block.</Text>
          </VStack>

          <VStack space="sm">
            <Text className="text-typography-600 dark:text-gray-300">Title</Text>
            <Input className="bg-background-50 dark:bg-background-100">
              <InputField placeholder="e.g. Push Day" value={title} onChangeText={setTitle} />
            </Input>
            <Text className="text-typography-600 dark:text-gray-300">Date (YYYY-MM-DD)</Text>
            <Input className="bg-background-50 dark:bg-background-100">
              <InputField placeholder="YYYY-MM-DD" value={date} onChangeText={setDate} />
            </Input>
          </VStack>

          <VStack space="md">
            <Text className="text-lg font-semibold text-typography-900 dark:text-white">Blocks</Text>
            <FlatList
              data={prescriptions}
              keyExtractor={(item) => `${item.position}`}
              renderItem={({ item, index }) => (
                <Box className="p-4 rounded-xl border bg-background-50 dark:bg-background-100 border-border-200 dark:border-border-700">
                  <VStack space="sm">
                    <VStack space="xs">
                      <Text className="text-base font-semibold text-typography-900 dark:text-white">{item.name}</Text>
                    </VStack>
                    <Pressable onPress={() => { setPickerForBlock(index); setPickerOpen(true); setSearchTerm('') }} className="self-start px-3 py-2 rounded-lg border border-indigo-300 dark:border-indigo-700 bg-white dark:bg-indigo-950">
                      <Text className="text-indigo-700 dark:text-indigo-200 font-semibold">＋ Add Movement</Text>
                    </Pressable>

                    {item.movements.length === 0 ? (
                      <Text className="text-typography-600 dark:text-gray-300">No movements yet</Text>
                    ) : (
                      <VStack space="sm">
                        {item.movements.map((m, mi) => (
                          <Box key={`${mi}`} className="p-3 rounded-lg border bg-white dark:bg-background-0 border-border-200 dark:border-border-700">
                            <VStack space="xs">
                              <Text className="font-semibold text-typography-900 dark:text-white">{mi + 1}. {m.name}</Text>
                              <Text className="text-typography-600 dark:text-gray-300">{m.prescribedSets ?? 0} sets · rest {m.restDuration ?? 0}s</Text>
                              <Pressable onPress={() => addSetToMovement(index, mi)} className="self-start px-3 py-1.5 rounded-md border border-border-200 dark:border-border-700">
                                <Text className="text-typography-700 dark:text-gray-200 font-semibold">Add Set</Text>
                              </Pressable>
                              {m.sets.map((s, si) => (
                                <Text key={`${si}`} className="text-typography-700 dark:text-gray-200 ml-1">
                                  {`Set ${si + 1}: ${s.reps ?? '-'} reps${s.loadValue ? ` @ ${s.loadValue} ${s.loadUnit ?? ''}` : ''}`}
                                </Text>
                              ))}
                            </VStack>
                          </Box>
                        ))}
                      </VStack>
                    )}
                  </VStack>
                </Box>
              )}
            />
          </VStack>

          <Pressable disabled={loading} onPress={onSubmit} className="mt-2 items-center justify-center rounded-xl bg-indigo-600 px-4 py-3 disabled:bg-indigo-300">
            <Text className="text-white font-bold">{loading ? 'Creating…' : 'Create Workout'}</Text>
          </Pressable>
        </VStack>

        {/* Movement search modal (patterned after Add Food) */}
        <Modal visible={isPickerOpen} transparent animationType="fade" onRequestClose={() => { setPickerOpen(false); setPickerForBlock(null); setSearchTerm('') }}>
          <View style={{ flex: 1, alignItems: 'center' }}>
            <RNPressable style={{ position: 'absolute', top: 0, bottom: 0, left: 0, right: 0, backgroundColor: 'rgba(0,0,0,0.4)' }} onPress={() => { setPickerOpen(false); setPickerForBlock(null); setSearchTerm('') }} />
            <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={{ width: '100%', alignItems: 'center', paddingTop: Platform.OS === 'ios' ? 60 : 30 }}>
              <View style={{ width: '96%', height: '70%', maxHeight: '70%', borderRadius: 16, backgroundColor: '#fff', padding: 16 }}>
                <RNText style={{ fontSize: 18, fontWeight: '600', marginBottom: 8 }}>Add Movement</RNText>
                <View style={{ marginBottom: 12 }}>
                  <TextInput placeholder="Search movements…" value={searchTerm} onChangeText={setSearchTerm} autoFocus style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10 }} />
                </View>
                <FlatList
                  keyboardDismissMode="on-drag"
                  keyboardShouldPersistTaps="handled"
                  data={searchResults}
                  keyExtractor={(item: any, i) => item.id_ ?? `${i}`}
                  renderItem={({ item }) => (
                    <RNPressable onPress={() => { if (pickerForBlock != null) addMovementToPrescription(pickerForBlock, item); setPickerOpen(false); setPickerForBlock(null); }} style={{ paddingVertical: 10, borderTopWidth: 1, borderTopColor: '#e5e7eb' }}>
                      <View>
                        <RNText style={{ fontWeight: '600' }}>{item.name}</RNText>
                        <RNText style={{ color: '#6b7280' }}>{item.bodyRegion}{Array.isArray(item.equipment) && item.equipment.length ? ` • ${item.equipment.join(', ')}` : ''}</RNText>
                      </View>
                    </RNPressable>
                  )}
                  ListEmptyComponent={!searching ? (
                    <View style={{ paddingVertical: 16, alignItems: 'center' }}>
                      <RNText style={{ color: '#6b7280' }}>{(searchTerm||'').trim().length === 0 ? 'Type to search movements' : 'No matches found'}</RNText>
                    </View>
                  ) : null}
                  style={{ flex: 1 }}
                  contentContainerStyle={{ paddingBottom: 12 }}
                />
                <RNPressable onPress={() => { setPickerOpen(false); setPickerForBlock(null); setSearchTerm('') }} style={{ alignSelf: 'flex-end', marginTop: 12, paddingVertical: 8, paddingHorizontal: 12, borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8 }}>
                  <RNText style={{ color: '#374151', fontWeight: '600' }}>Close</RNText>
                </RNPressable>
              </View>
            </KeyboardAvoidingView>
          </View>
        </Modal>
      </VStack>
    </SafeAreaView>
  )
}