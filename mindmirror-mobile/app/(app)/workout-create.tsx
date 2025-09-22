import React, { useEffect, useMemo, useRef, useState } from 'react'
import { Modal, Platform, KeyboardAvoidingView, FlatList, Pressable as RNPressable, View, TextInput, Text as RNText, Dimensions, Image, ScrollView, Keyboard } from 'react-native'
import DateTimePicker from '@react-native-community/datetimepicker'
import { useRouter } from 'expo-router'
import dayjs from 'dayjs'
import { useCreateAdHocWorkout } from '@/services/api/practices'
import { useLazySearchMovements } from '@/services/api/movements'
import { useCreateMovement, useImportExternalMovement } from '@/services/api/movements'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { VStack } from '@/components/ui/vstack'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { Input, InputField } from '@/components/ui/input'
import { Pressable } from '@/components/ui/pressable'
import { AppBar } from '@/components/common/AppBar'
import { useApolloClient } from '@apollo/client'
import { QUERY_TODAYS_SCHEDULABLES } from '@/services/api/users'
import { Select, SelectBackdrop, SelectContent, SelectDragIndicator, SelectDragIndicatorWrapper, SelectInput, SelectItem, SelectPortal, SelectTrigger } from '@/components/ui/select'
import { useCreatePracticeTemplate, QUERY_PRACTICE_TEMPLATES } from '@/services/api/practices'
import GlobalFab from '@/components/common/GlobalFab'
import { useThemeVariant } from '@/theme/ThemeContext'
import { useFocusEffect } from '@react-navigation/native'
import Markdown from 'react-native-markdown-display'
import { MovementThumb } from '@/components/workouts/MovementMedia'

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
  imageUrl?: string
  shortVideoUrl?: string
  longVideoUrl?: string
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
  const apollo = useApolloClient()
  const [title, setTitle] = useState('')
  const [dt, setDt] = useState<Date>(new Date())
  const [dateText, setDateText] = useState(dayjs(new Date()).format('YYYY-MM-DD'))
  const [showDatePicker, setShowDatePicker] = useState(false)
  const [createWorkout, { loading }] = useCreateAdHocWorkout()
  const [createTemplate, { loading: savingTemplate }] = useCreatePracticeTemplate()
  const [asTemplate, setAsTemplate] = useState(false)
  const [templateDescription, setTemplateDescription] = useState('')
  const [toast, setToast] = useState<{ msg: string; type: 'error' | 'success' } | null>(null)
  const showToast = (msg: string, type: 'error' | 'success' = 'error') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 2500)
  }

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
  const [importExternal] = useImportExternalMovement()
  const [createMovementMutation] = useCreateMovement()
  const [showCreateExercise, setShowCreateExercise] = useState(false)
  const [newExerciseName, setNewExerciseName] = useState('')
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [advDifficulty, setAdvDifficulty] = useState('')
  const [advBodyRegion, setAdvBodyRegion] = useState('')
  const [advEquipmentCsv, setAdvEquipmentCsv] = useState('')
  const [advPrimaryMusclesCsv, setAdvPrimaryMusclesCsv] = useState('')
  const [advSecondaryMusclesCsv, setAdvSecondaryMusclesCsv] = useState('')
  const [advPatternsCsv, setAdvPatternsCsv] = useState('')
  const [advPlanesCsv, setAdvPlanesCsv] = useState('')
  const [advTagsCsv, setAdvTagsCsv] = useState('')
  const [advShortVideoUrl, setAdvShortVideoUrl] = useState('')
  const [advLongVideoUrl, setAdvLongVideoUrl] = useState('')
  const [advDescription, setAdvDescription] = useState('')
  const [videoOpenByKey, setVideoOpenByKey] = useState<Record<string, boolean>>({})
  const [descOpenByKey, setDescOpenByKey] = useState<Record<string, boolean>>({})
  const toggleVideoFor = (key: string) => setVideoOpenByKey(prev => ({ ...prev, [key]: !prev[key] }))
  const toggleDescFor = (key: string) => setDescOpenByKey(prev => ({ ...prev, [key]: !prev[key] }))

  // Optional draggable list (fallback to static list if not installed)
  // Prefer react-native-draglist for stable drag without input conflicts
  let DragList: any = null
  try { DragList = require('react-native-draglist').default } catch {}

  // Input refs for keyboard navigation
  const inputRefs = useRef<Record<string, TextInput | null>>({})
  const setInputRef = (key: string) => (el: TextInput | null) => {
    inputRefs.current[key] = el
  }
  const focusKey = (key: string) => {
    const ref = inputRefs.current[key]
    if (ref && typeof ref.focus === 'function') ref.focus()
  }
  const focusNextField = (pIndex: number, mIndex: number, sIndex: number, field: 'reps' | 'duration' | 'loadValue' | 'restDuration', metricUnit: string) => {
    const order: Array<'reps' | 'duration' | 'loadValue' | 'restDuration'> = metricUnit === 'temporal' ? ['duration', 'loadValue', 'restDuration'] : ['reps', 'loadValue', 'restDuration']
    const curIdx = order.indexOf(field)
    if (curIdx >= 0 && curIdx < order.length - 1) {
      const nextField = order[curIdx + 1]
      focusKey(`${pIndex}-${mIndex}-${sIndex}-${nextField}`)
      return
    }
    // Move to next row's first field if exists
    const nextRow = sIndex + 1
    const firstField = order[0]
    const key = `${pIndex}-${mIndex}-${nextRow}-${firstField}`
    if (inputRefs.current[key]) {
      focusKey(key)
      return
    }
    // Optionally add a new set and focus it
    addSetToMovement(pIndex, mIndex)
    setTimeout(() => focusKey(`${pIndex}-${mIndex}-${nextRow}-${firstField}`), 50)
  }

  // Debounced search (DB-only results)
  useEffect(() => {
    if (!isPickerOpen) return
    const term = (searchTerm || '').trim()
    const h = setTimeout(() => {
      if (term.length === 0) return
      runSearch({ variables: { searchTerm: term, limit: 15 } })
    }, 250)
    return () => clearTimeout(h)
  }, [isPickerOpen, searchTerm, runSearch])

  const searchResults = useMemo(() => {
    const list = searchData?.searchMovements ?? []
    // Show both sources; external items labeled in UI
    return list
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
        description: m.description ?? undefined,
        movementClass: 'other',
        prescribedSets: 3,
        restDuration: 60,
        videoUrl: m.shortVideoUrl ?? undefined,
        sets: [
          { position: 1, reps: 10, restDuration: 60, loadUnit: 'bodyweight' } as SetDraft,
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
      const last = mov.sets[mov.sets.length - 1]
      const newSet = {
        position: nextPos,
        reps: last?.reps ?? 10,
        duration: (last?.duration ?? undefined) as number | undefined,
        loadValue: (last?.loadValue ?? undefined) as number | undefined,
        loadUnit: last?.loadUnit ?? 'bodyweight',
        restDuration: last?.restDuration ?? 60,
      } as SetDraft
      mov.sets = [...mov.sets, newSet]
      p.movements = p.movements.map((mm, i) => (i === mIndex ? mov : mm))
      copy[pIndex] = p
      return copy
    })
  }

  const updateSetField = (
    pIndex: number,
    mIndex: number,
    sIndex: number,
    field: keyof SetDraft,
    value: string
  ) => {
    setPrescriptions((prev) => {
      const copy: PrescriptionDraft[] = [...prev]
      const p = copy[pIndex]
      if (!p) return prev
      const mov = p.movements[mIndex]
      if (!mov) return prev
      const set = mov.sets[sIndex]
      if (!set) return prev
      let patched: any = value
      if (field === 'reps' || field === 'duration' || field === 'loadValue' || field === 'restDuration') {
        const num = parseFloat(value)
        patched = Number.isFinite(num) ? num : undefined
      }
      const newSet: SetDraft = { ...set, [field]: patched }
      const newSets = mov.sets.map((s, i) => (i === sIndex ? newSet : s))
      const newMov: MovementDraft = { ...mov, sets: newSets }
      p.movements = p.movements.map((mm, i) => (i === mIndex ? newMov : mm))
      copy[pIndex] = p
      return copy
    })
  }

  const removeSet = (pIndex: number, mIndex: number, sIndex: number) => {
    setPrescriptions((prev) => {
      const copy: PrescriptionDraft[] = [...prev]
      const p = copy[pIndex]
      if (!p) return prev
      const mov = p.movements[mIndex]
      if (!mov) return prev
      const newSets = mov.sets.filter((_, i) => i !== sIndex).map((s, i) => ({ ...s, position: i + 1 }))
      const newMov: MovementDraft = { ...mov, sets: newSets }
      p.movements = p.movements.map((mm, i) => (i === mIndex ? newMov : mm))
      copy[pIndex] = p
      return copy
    })
  }

  const onSubmit = async () => {
    if (!title) {
      showToast('Please enter a workout title', 'error')
      return
    }

    const gqlPrescriptions = prescriptions.map((p) => ({
      name: p.name,
      position: p.position,
      block: p.block,
      prescribedRounds: p.prescribedRounds,
      description: '',
      movements: p.movements.map((m) => ({
        name: m.name,
        position: m.position,
        metricUnit: (m.metricUnit || 'iterative').toUpperCase(),
        metricValue: m.metricValue,
        description: m.description ?? '',
        movementClass: (m.movementClass || 'other').toUpperCase(),
        prescribedSets: m.prescribedSets,
        restDuration: m.restDuration,
        videoUrl: m.videoUrl,
        exerciseId: m.exerciseId,
        sets: m.sets.map((s) => ({
          position: s.position,
          reps: s.reps,
          duration: s.duration,
          loadValue: s.loadValue,
          loadUnit: s.loadUnit,
          restDuration: s.restDuration,
        })),
      })),
    }))

    try {
      const variables = { input: { title, date: dateText, prescriptions: gqlPrescriptions } }
      console.log('[CreateWorkout] Submitting variables:', variables)
      await createWorkout({ variables })
      showToast('Workout created', 'success')
      await new Promise((r) => setTimeout(r, 600))
      router.back()
    } catch (e: any) {
      console.error('[CreateWorkout] Error:', e)
      showToast(e?.message || 'Failed to create workout', 'error')
    }
  }

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title="Create Workout" showBackButton onBackPress={() => router.back()} />
        <VStack className="flex-1 w-full max-w-screen-md mx-auto px-6 py-6" space="lg">
          <VStack space="sm">
            <VStack className="flex-row items-center justify-between">
              <Text className="text-2xl font-bold text-typography-900 dark:text-white">Workout Details</Text>
              <Pressable onPress={() => setAsTemplate(v => !v)} className={`px-3 py-1 rounded-full border ${asTemplate ? 'border-indigo-300 bg-indigo-50' : 'border-border-200 bg-background-50'}`}>
                <Text className="text-xs font-semibold">{asTemplate ? 'Template' : 'Instance'}</Text>
              </Pressable>
            </VStack>
            <Text className="text-typography-600 dark:text-gray-300">Set a title and date, then add movements to each block.</Text>
          </VStack>

          <VStack space="sm" style={{ flexShrink: 0 }}>
            <Text className="text-typography-900 font-semibold dark:text-white">Title</Text>
            <Input className="bg-background-50 dark:bg-background-100">
              <InputField placeholder="e.g. Push Day" value={title} onChangeText={setTitle} />
            </Input>
            {asTemplate ? (
              <>
                <Text className="text-typography-900 font-semibold dark:text-white">Template Description</Text>
                <TextInput
                  placeholder="Optional description for this template"
                  value={templateDescription}
                  onChangeText={setTemplateDescription}
                  multiline
                  numberOfLines={3}
                  className="bg-background-50 dark:bg-background-100 text-typography-600 dark:text-gray-300"
                  style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10, minHeight: 48, textAlignVertical: 'top' }}
                />
                {templateDescription.trim().length > 0 ? (
                  <Box className="mt-2 mb-3 p-3 rounded-lg border border-border-200 bg-background-50 dark:bg-background-100" style={{ height: 140, zIndex: 10 }}>
                    <ScrollView
                      nestedScrollEnabled
                      keyboardShouldPersistTaps="handled"
                      showsVerticalScrollIndicator
                      style={{ flex: 1 }}
                      contentContainerStyle={{ paddingBottom: 8 }}
                    >
                      <Markdown>{templateDescription}</Markdown>
                    </ScrollView>
                  </Box>
                ) : null}
              </>
            ) : null}
            {!asTemplate && (
              <>
                <Text className="text-typography-600 dark:text-gray-300">Date (YYYY-MM-DD)</Text>
                <Input className="bg-background-50 dark:bg-background-100">
                  <InputField placeholder="YYYY-MM-DD" value={dateText} onChangeText={setDateText} autoCapitalize="none" autoCorrect={false} />
                </Input>
              </>
            )}
          </VStack>

          {/* Divider with extra bottom margin to ensure description preview doesn't get overlapped */}
          <Box className="h-px bg-border-200 dark:bg-border-700 mt-4 mb-6" />
          <VStack space="md" className="mt-4" style={{ minHeight: 0, flexGrow: 1 }}>
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
                        {DragList ? (
                          <DragList
                            style={{ flexGrow: 1, minHeight: 0 }}
                            data={item.movements}
                            keyExtractor={(m: any, mi: number) => `${m.movementId || m.name || mi}`}
                            onReordered={(arg1: any, arg2?: any) => {
                              // accept either (from,to) or {from,to}
                              let from = -1
                              let to = -1
                              if (typeof arg1 === 'number') { from = arg1 as number; to = (arg2 as number) ?? -1 }
                              else if (arg1 && typeof arg1 === 'object') { from = (arg1.from ?? -1); to = (arg1.to ?? -1) }
                              if (from < 0 || to < 0) return
                              setPrescriptions(prev => {
                                const cp = [...prev]
                                const pb = cp[index]
                                if (!pb) return prev
                                const arr: MovementDraft[] = [...pb.movements]
                                if (from < 0 || from >= arr.length) return prev
                                const movedArr = arr.splice(from, 1)
                                if (movedArr.length === 0) return prev
                                const moved = movedArr[0] as MovementDraft
                                if (to < 0 || to > arr.length) return prev
                                arr.splice(to, 0, moved)
                                pb.movements = arr.map((mm, i) => ({ ...mm, position: i + 1 }))
                                cp[index] = { ...pb }
                                return cp
                              })
                            }}
                            renderItem={({ item: m, index: mi, drag }: any) => (
                              <Box key={`${m.movementId || m.name || mi}`} className="p-3 rounded-lg border bg-white dark:bg-background-0 border-border-200 dark:border-border-700">
                                <VStack space="sm">
                                  <Box className="flex-row items-center justify-between">
                                    <Box className="flex-row items-center">
                                      <Pressable onLongPress={() => { Keyboard.dismiss(); drag() }} delayLongPress={120} className="mr-2 px-2 py-1 rounded-md border border-border-200 dark:border-border-700 bg-background-50">
                                        <Text className="text-typography-600">≡</Text>
                                      </Pressable>
                                      <Text className="font-semibold text-typography-900 dark:text-white">{m.name}</Text>
                                    </Box>
                                    <Pressable onPress={() => {
                                      setPrescriptions(prev => {
                                        const cp = [...prev]
                                        const pb = cp[index]
                                        if (!pb) return prev
                                        pb.movements = pb.movements.filter((_, i) => i !== mi).map((mm, i) => ({ ...mm, position: i + 1 }))
                                        cp[index] = { ...pb }
                                        return cp
                                      })
                                    }} className="px-2 py-1 rounded-md border border-red-300 bg-white dark:bg-background-0">
                                      <Text className="text-red-700 dark:text-red-300">Remove</Text>
                                    </Pressable>
                                  </Box>
                                  <MovementThumb imageUrl={m.imageUrl} videoUrl={(m.shortVideoUrl || m.longVideoUrl || m.videoUrl) as string | undefined} />
                                  <Text className="text-typography-600 dark:text-gray-300">{m.sets.length} sets</Text>
                                  <Pressable onPress={() => addSetToMovement(index, mi)} className="self-start px-3 py-1.5 rounded-md border border-border-200 dark:border-border-700">
                                    <Text className="text-typography-700 dark:text-gray-200 font-semibold">Add Set</Text>
                                  </Pressable>

                                  {m.sets.length > 0 && (
                                    <VStack space="xs">
                                      <Box className="flex-row items-center px-2 py-1">
                                        <Box className="w-12"><Text className="text-typography-600 dark:text-gray-300">#</Text></Box>
                                        <Box className="flex-1"><Text className="text-typography-600 dark:text-gray-300">{m.metricUnit === 'temporal' ? 'Duration (s)' : 'Reps'}</Text></Box>
                                        <Box className="flex-1"><Text className="text-typography-600 dark:text-gray-300">Load</Text></Box>
                                        <Box className="w-28"><Text className="text-typography-600 dark:text-gray-300">Unit</Text></Box>
                                        <Box className="w-28"><Text className="text-typography-600 dark:text-gray-300">Rest (s)</Text></Box>
                                        <Box className="w-14" />
                                      </Box>
                                      {m.sets.map((s: any, si: number) => (
                                        <Box key={`${si}`} className="flex-row items-center px-2 py-1 rounded-md border border-border-200 dark:border-border-700 bg-background-50 dark:bg-background-100">
                                          <Box className="w-12"><Text className="text-typography-700 dark:text-gray-200">{si + 1}</Text></Box>
                                          <Box className="flex-1 mr-2">
                                            <TextInput
                                              ref={setInputRef(`${index}-${mi}-${si}-${m.metricUnit === 'temporal' ? 'duration' : 'reps'}`)}
                                              keyboardType="numeric"
                                              value={m.metricUnit === 'temporal' ? (s.duration != null ? String(s.duration) : '') : (s.reps != null ? String(s.reps) : '')}
                                              onChangeText={(v) => updateSetField(index, mi, si, m.metricUnit === 'temporal' ? 'duration' : 'reps', v)}
                                              returnKeyType="next"
                                              blurOnSubmit={false}
                                              onSubmitEditing={() => focusNextField(index, mi, si, m.metricUnit === 'temporal' ? 'duration' : 'reps', m.metricUnit)}
                                              placeholder={m.metricUnit === 'temporal' ? '30' : '10'}
                                              style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, paddingHorizontal: 10, paddingVertical: 8, backgroundColor: '#fff' }}
                                            />
                                          </Box>
                                          <Box className="flex-1 mr-2">
                                            <TextInput
                                              ref={setInputRef(`${index}-${mi}-${si}-loadValue`)}
                                              keyboardType="numeric"
                                              value={s.loadValue != null ? String(s.loadValue) : ''}
                                              onChangeText={(v) => updateSetField(index, mi, si, 'loadValue', v)}
                                              returnKeyType="next"
                                              blurOnSubmit={false}
                                              onSubmitEditing={() => focusNextField(index, mi, si, 'loadValue', m.metricUnit)}
                                              placeholder="45"
                                              style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, paddingHorizontal: 10, paddingVertical: 8, backgroundColor: '#fff' }}
                                            />
                                          </Box>
                                          <Box className="w-28 mr-2">
                                            <Input>
                                              <InputField placeholder="unit (lb/kg/bw)" value={s.loadUnit ?? ''} onChangeText={(v) => updateSetField(index, mi, si, 'loadUnit', v)} />
                                            </Input>
                                          </Box>
                                          <Box className="w-28 mr-2">
                                            <TextInput
                                              ref={setInputRef(`${index}-${mi}-${si}-restDuration`)}
                                              keyboardType="numeric"
                                              value={s.restDuration != null ? String(s.restDuration) : ''}
                                              onChangeText={(v) => updateSetField(index, mi, si, 'restDuration', v)}
                                              returnKeyType="next"
                                              blurOnSubmit={false}
                                              placeholder="60"
                                              style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, paddingHorizontal: 10, paddingVertical: 8, backgroundColor: '#fff' }}
                                            />
                                          </Box>
                                          <Box className="w-14" />
                                        </Box>
                                      ))}
                                    </VStack>
                                  )}
                                </VStack>
                              </Box>
                            )}
                          />
                        ) : (
                          item.movements.map((m, mi) => (
                          <Box key={`${m.movementId || m.name || mi}`} className="p-3 rounded-lg border bg-white dark:bg-background-0 border-border-200 dark:border-border-700">
                            <VStack space="sm">
                              <Box className="flex-row items-center justify-between">
                                  <Text className="font-semibold text-typography-900 dark:text-white">{m.name}</Text>
                                <Pressable onPress={() => {
                                  setPrescriptions(prev => {
                                    const cp = [...prev]
                                    const pb = cp[index]
                                    if (!pb) return prev
                                    pb.movements = pb.movements.filter((_, i) => i !== mi).map((mm, i) => ({ ...mm, position: i + 1 }))
                                    cp[index] = { ...pb }
                                    return cp
                                  })
                                }} className="px-2 py-1 rounded-md border border-red-300 bg-white dark:bg-background-0">
                                  <Text className="text-red-700 dark:text-red-300">Remove</Text>
                                </Pressable>
                              </Box>
                              {/* Collapsible video */}
                              <Pressable onPress={() => toggleVideoFor(`${index}-${mi}`)} className="flex-row items-center justify-between px-3 py-2 rounded-md border border-border-200 bg-background-0">
                                <Text className="font-semibold text-typography-900 dark:text-white">Video</Text>
                                <Text className="text-typography-600 dark:text-gray-300">{videoOpenByKey[`${index}-${mi}`] ? '−' : '+'}</Text>
                              </Pressable>
                              {videoOpenByKey[`${index}-${mi}`] ? (
                                <MovementThumb imageUrl={m.imageUrl as string | undefined} videoUrl={(m.shortVideoUrl || m.longVideoUrl) as string | undefined} />
                              ) : null}
                              {/* Collapsible description (if any) */}
                              {m.description ? (
                                <>
                                  <Pressable onPress={() => toggleDescFor(`${index}-${mi}`)} className="flex-row items-center justify-between px-3 py-2 rounded-md border border-border-200 bg-background-0">
                                    <Text className="font-semibold text-typography-900 dark:text-white">Description</Text>
                                    <Text className="text-typography-600 dark:text-gray-300">{descOpenByKey[`${index}-${mi}`] ? '−' : '+'}</Text>
                                  </Pressable>
                                  {descOpenByKey[`${index}-${mi}`] ? (
                                    <Box className="p-2 rounded border border-border-200 bg-background-50 dark:bg-background-100">
                                      <Markdown>{m.description}</Markdown>
                                    </Box>
                                  ) : null}
                                </>
                              ) : null}

                              <Text className="text-typography-600 dark:text-gray-300">{m.sets.length} sets</Text>
                              <Pressable onPress={() => addSetToMovement(index, mi)} className="self-start px-3 py-1.5 rounded-md border border-border-200 dark:border-border-700">
                                <Text className="text-typography-700 dark:text-gray-200 font-semibold">Add Set</Text>
                              </Pressable>

                              {/* Set editor table */}
                              {m.sets.length > 0 && (
                                <VStack space="xs">
                                  {/* Header row */}
                                  <Box className="flex-row items-center px-2 py-1">
                                    <Box className="w-12"><Text className="text-typography-600 dark:text-gray-300">#</Text></Box>
                                    <Box className="flex-1"><Text className="text-typography-600 dark:text-gray-300">{m.metricUnit === 'temporal' ? 'Duration (s)' : 'Reps'}</Text></Box>
                                    <Box className="flex-1"><Text className="text-typography-600 dark:text-gray-300">Load</Text></Box>
                                    <Box className="w-28"><Text className="text-typography-600 dark:text-gray-300">Unit</Text></Box>
                                    <Box className="w-28"><Text className="text-typography-600 dark:text-gray-300">Rest (s)</Text></Box>
                                    <Box className="w-14" />
                                  </Box>
                                  {m.sets.map((s, si) => (
                                    <Box key={`${si}`} className="flex-row items-center px-2 py-1 rounded-md border border-border-200 dark:border-border-700 bg-background-50 dark:bg-background-100">
                                      <Box className="w-12"><Text className="text-typography-700 dark:text-gray-200">{si + 1}</Text></Box>
                                      <Box className="flex-1 mr-2">
                                        <TextInput
                                          ref={setInputRef(`${index}-${mi}-${si}-${m.metricUnit === 'temporal' ? 'duration' : 'reps'}`)}
                                          keyboardType="numeric"
                                          value={m.metricUnit === 'temporal' ? (s.duration != null ? String(s.duration) : '') : (s.reps != null ? String(s.reps) : '')}
                                          onChangeText={(v) => updateSetField(index, mi, si, m.metricUnit === 'temporal' ? 'duration' : 'reps', v)}
                                          returnKeyType="next"
                                          blurOnSubmit={false}
                                          onSubmitEditing={() => focusNextField(index, mi, si, m.metricUnit === 'temporal' ? 'duration' : 'reps', m.metricUnit)}
                                          placeholder={m.metricUnit === 'temporal' ? '30' : '10'}
                                          style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, paddingHorizontal: 10, paddingVertical: 8, backgroundColor: '#fff' }}
                                        />
                                      </Box>
                                      <Box className="flex-1 mr-2">
                                        <TextInput
                                          ref={setInputRef(`${index}-${mi}-${si}-loadValue`)}
                                          keyboardType="numeric"
                                          value={s.loadValue != null ? String(s.loadValue) : ''}
                                          onChangeText={(v) => updateSetField(index, mi, si, 'loadValue', v)}
                                          returnKeyType="next"
                                          blurOnSubmit={false}
                                          onSubmitEditing={() => focusNextField(index, mi, si, 'loadValue', m.metricUnit)}
                                          placeholder="45"
                                          style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, paddingHorizontal: 10, paddingVertical: 8, backgroundColor: '#fff' }}
                                        />
                                      </Box>
                                      <Box className="w-28 mr-2">
                                        <Select selectedValue={s.loadUnit ?? ''} onValueChange={(v: any) => updateSetField(index, mi, si, 'loadUnit', v)}>
                                          <SelectTrigger variant="outline">
                                            <SelectInput placeholder="unit" />
                                          </SelectTrigger>
                                          <SelectPortal>
                                            <SelectBackdrop />
                                            <SelectContent>
                                              <SelectDragIndicatorWrapper>
                                                <SelectDragIndicator />
                                              </SelectDragIndicatorWrapper>
                                              <SelectItem label="lb" value="pounds" />
                                              <SelectItem label="kg" value="kilograms" />
                                              <SelectItem label="bw" value="bodyweight" />
                                              <SelectItem label="other" value="other" />
                                            </SelectContent>
                                          </SelectPortal>
                                        </Select>
                                      </Box>
                                      <Box className="w-28 mr-2">
                                        <TextInput
                                          ref={setInputRef(`${index}-${mi}-${si}-restDuration`)}
                                          keyboardType="numeric"
                                          value={s.restDuration != null ? String(s.restDuration) : ''}
                                          onChangeText={(v) => updateSetField(index, mi, si, 'restDuration', v)}
                                          returnKeyType="next"
                                          blurOnSubmit={false}
                                          placeholder="60"
                                          style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, paddingHorizontal: 10, paddingVertical: 8, backgroundColor: '#fff' }}
                                        />
                                      </Box>
                                        <Box className="w-14" />
                                    </Box>
                                  ))}
                                </VStack>
                              )}
                            </VStack>
                          </Box>
                          ))
                        )}
                      </VStack>
                    )}
                  </VStack>
                </Box>
              )}
            />
          </VStack>

          <Pressable disabled={loading || savingTemplate} onPress={async () => {
            if (!title) { showToast('Please enter a workout title', 'error'); return }
            if (asTemplate) {
              // Build PracticeTemplateCreateInput
              const gqlPrescriptions = prescriptions.map((p) => ({
                name: p.name,
                position: p.position,
                block: p.block,
                description: '',
                prescribedRounds: p.prescribedRounds,
                movements: p.movements.map((m) => ({
                  name: m.name,
                  position: m.position,
                  metricUnit: (m.metricUnit || 'iterative').toUpperCase(),
                  metricValue: m.metricValue,
                  description: m.description ?? '',
                  movementClass: (m.movementClass || 'other').toUpperCase(),
                  prescribedSets: m.prescribedSets,
                  restDuration: m.restDuration,
                  // Persist videoUrl from short/long URLs so instances can read it
                  videoUrl: (m.shortVideoUrl || m.longVideoUrl || m.videoUrl || undefined) as string | undefined,
                  exerciseId: m.exerciseId,
                  sets: m.sets.map((s) => ({ position: s.position, reps: s.reps, duration: s.duration, restDuration: s.restDuration, loadValue: s.loadValue, loadUnit: s.loadUnit })),
                })),
              }))
              try {
                await createTemplate({ variables: { input: { title, description: templateDescription || '', prescriptions: gqlPrescriptions } } })
                apollo.refetchQueries({ include: [QUERY_PRACTICE_TEMPLATES] })
                showToast('Template created', 'success')
                await new Promise((r) => setTimeout(r, 400))
                router.back()
              } catch (e: any) {
                showToast(e?.message || 'Failed to create template', 'error')
              }
            } else {
              await onSubmit()
            }
          }} className="mt-2 items-center justify-center rounded-xl bg-indigo-600 px-4 py-3 disabled:bg-indigo-300">
            <Text className="text-white font-bold">{(loading || savingTemplate) ? 'Creating…' : (asTemplate ? 'Create Template' : 'Create Workout')}</Text>
          </Pressable>
        </VStack>

        {toast && (
          <View style={{ position: 'absolute', left: 16, right: 16, bottom: 24, paddingVertical: 12, paddingHorizontal: 16, borderRadius: 10, backgroundColor: toast.type === 'success' ? '#16a34a' : '#dc2626' }}>
            <RNText style={{ color: '#fff', fontWeight: '600' }}>{toast.msg}</RNText>
          </View>
        )}

        {/* Movement search modal (patterned after Add Food) */}
        <Modal visible={isPickerOpen} transparent animationType="fade" onRequestClose={() => { setPickerOpen(false); setPickerForBlock(null); setSearchTerm('') }}>
          <View style={{ flex: 1, alignItems: 'center' }}>
            <RNPressable style={{ position: 'absolute', top: 0, bottom: 0, left: 0, right: 0, backgroundColor: 'rgba(0,0,0,0.4)' }} onPress={() => { setPickerOpen(false); setPickerForBlock(null); setSearchTerm('') }} />
            <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={{ width: '100%', alignItems: 'center', paddingTop: Platform.OS === 'ios' ? 60 : 30 }}>
              <View style={{ width: '96%', maxWidth: 560, maxHeight: 520, borderRadius: 16, backgroundColor: '#fff', padding: 16, flexDirection: 'column', alignSelf: 'center', borderWidth: 1, borderColor: '#e5e7eb' }}>
                <RNText style={{ fontSize: 18, fontWeight: '600', marginBottom: 8 }}>Add Movement</RNText>
                <View style={{ marginBottom: 12 }}>
                  <TextInput placeholder="Search movements…" value={searchTerm} onChangeText={setSearchTerm} autoFocus style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10 }} />
                </View>
                <View style={{ flex: 1, minHeight: 240, overflow: 'hidden' }}>
                <FlatList
                  keyboardDismissMode="on-drag"
                  keyboardShouldPersistTaps="handled"
                  data={searchResults}
                    keyExtractor={(item: any, i) => item.id_ ?? item.externalId ?? `${i}`}
                  renderItem={({ item }) => (
                      <RNPressable onPress={() => {
                        if (item.isExternal && item.externalId) {
                          (async () => {
                            try {
                              const res = await importExternal({ variables: { externalId: item.externalId } })
                              const local = res.data?.importExternalMovement
                              if (local && pickerForBlock != null) {
                                addMovementToPrescription(pickerForBlock, { ...local, id_: local.id_ })
                              }
                            } catch {}
                            setPickerOpen(false); setPickerForBlock(null)
                          })()
                        } else {
                          if (pickerForBlock != null) addMovementToPrescription(pickerForBlock, item)
                          setPickerOpen(false); setPickerForBlock(null)
                        }
                      }} style={{ paddingVertical: 10, borderTopWidth: 1, borderTopColor: '#e5e7eb' }}>
                        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                          <View style={{ flex: 1, paddingRight: 8 }}>
                        <RNText style={{ fontWeight: '600' }}>{item.name}</RNText>
                        <RNText style={{ color: '#6b7280' }}>{item.bodyRegion}{Array.isArray(item.equipment) && item.equipment.length ? ` • ${item.equipment.join(', ')}` : ''}</RNText>
                          </View>
                          {item.isExternal ? (
                            <View style={{ paddingVertical: 4, paddingHorizontal: 8, borderRadius: 999, backgroundColor: '#eff6ff', borderWidth: 1, borderColor: '#dbeafe' }}>
                              <RNText style={{ color: '#1d4ed8', fontWeight: '700' }}>ExerciseDB</RNText>
                            </View>
                          ) : (
                            <View style={{ paddingVertical: 4, paddingHorizontal: 8, borderRadius: 999, backgroundColor: '#f0fdf4', borderWidth: 1, borderColor: '#dcfce7' }}>
                              <RNText style={{ color: '#16a34a', fontWeight: '700' }}>Local</RNText>
                            </View>
                          )}
                      </View>
                    </RNPressable>
                  )}
                  ListEmptyComponent={!searching ? (
                    <View style={{ paddingVertical: 16, alignItems: 'center' }}>
                      <RNText style={{ color: '#6b7280' }}>{(searchTerm||'').trim().length === 0 ? 'Type to search movements' : 'No matches found'}</RNText>
                    </View>
                  ) : null}
                  style={{ flex: 1 }}
                    contentContainerStyle={{ paddingBottom: 8 }}
                  />
                </View>
                <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: 8 }}>
                  <RNPressable onPress={() => { setShowCreateExercise(true) }} style={{ alignSelf: 'flex-start', paddingVertical: 8, paddingHorizontal: 12, borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8 }}>
                    <RNText style={{ color: '#111827', fontWeight: '700' }}>＋ Create Exercise</RNText>
                  </RNPressable>
                  <RNPressable onPress={() => { setPickerOpen(false); setPickerForBlock(null); setSearchTerm('') }} style={{ alignSelf: 'flex-end', paddingVertical: 8, paddingHorizontal: 12, borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8 }}>
                  <RNText style={{ color: '#374151', fontWeight: '600' }}>Close</RNText>
                </RNPressable>
                </View>
              </View>
            </KeyboardAvoidingView>
          </View>
        </Modal>

        {/* Create Exercise Modal */}
        <Modal visible={showCreateExercise} transparent animationType="fade" onRequestClose={() => setShowCreateExercise(false)}>
          <View style={{ flex: 1, alignItems: 'center' }}>
            <RNPressable style={{ position: 'absolute', top: 0, bottom: 0, left: 0, right: 0, backgroundColor: 'rgba(0,0,0,0.4)' }} onPress={() => setShowCreateExercise(false)} />
            <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={{ width: '100%', alignItems: 'center', paddingTop: Platform.OS === 'ios' ? 60 : 30 }}>
              <View style={{ width: '96%', maxWidth: 560, maxHeight: 560, borderRadius: 16, backgroundColor: '#fff', padding: 16, borderWidth: 1, borderColor: '#e5e7eb' }}>
                <RNText style={{ fontSize: 18, fontWeight: '600', marginBottom: 8 }}>Create Exercise</RNText>
                <View style={{ flex: 1 }}>
                  <View style={{ marginBottom: 12 }}>
                    <TextInput placeholder="Exercise name" value={newExerciseName} onChangeText={setNewExerciseName} autoFocus style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10 }} />
                  </View>
                  <RNPressable onPress={() => setShowAdvanced(v => !v)} style={{ alignSelf: 'flex-start', marginBottom: 8 }}>
                    <RNText style={{ color: '#1f2937', fontWeight: '700' }}>{showAdvanced ? '▾' : '▸'} Additional info</RNText>
                  </RNPressable>
                  {showAdvanced && (
                    <View style={{ flex: 1 }}>
                      <FlatList
                        data={[{ k: 'd' }, { k: 'br' }, { k: 'eq' }, { k: 'pm' }, { k: 'sm' }, { k: 'mp' }, { k: 'pl' }, { k: 'tg' }, { k: 'desc' }, { k: 'sv' }, { k: 'lv' }]}
                        keyExtractor={(it) => it.k}
                        renderItem={({ item }) => {
                          if (item.k === 'd') return <TextInput placeholder="Difficulty (e.g., Beginner)" value={advDifficulty} onChangeText={setAdvDifficulty} style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10, marginBottom: 8 }} />
                          if (item.k === 'br') return <TextInput placeholder="Body Region (e.g., Upper Body)" value={advBodyRegion} onChangeText={setAdvBodyRegion} style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10, marginBottom: 8 }} />
                          if (item.k === 'eq') return <TextInput placeholder="Equipment (comma-separated)" value={advEquipmentCsv} onChangeText={setAdvEquipmentCsv} style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10, marginBottom: 8 }} />
                          if (item.k === 'pm') return <TextInput placeholder="Primary Muscles (comma-separated)" value={advPrimaryMusclesCsv} onChangeText={setAdvPrimaryMusclesCsv} style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10, marginBottom: 8 }} />
                          if (item.k === 'sm') return <TextInput placeholder="Secondary Muscles (comma-separated)" value={advSecondaryMusclesCsv} onChangeText={setAdvSecondaryMusclesCsv} style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10, marginBottom: 8 }} />
                          if (item.k === 'mp') return <TextInput placeholder="Movement Patterns (comma-separated)" value={advPatternsCsv} onChangeText={setAdvPatternsCsv} style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10, marginBottom: 8 }} />
                          if (item.k === 'pl') return <TextInput placeholder="Planes of Motion (comma-separated)" value={advPlanesCsv} onChangeText={setAdvPlanesCsv} style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10, marginBottom: 8 }} />
                          if (item.k === 'tg') return <TextInput placeholder="Tags (comma-separated)" value={advTagsCsv} onChangeText={setAdvTagsCsv} style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10, marginBottom: 8 }} />
                          if (item.k === 'desc') return (
                            <>
                              <TextInput placeholder="Description (markdown supported)" value={advDescription} onChangeText={setAdvDescription} multiline numberOfLines={3} style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10, marginBottom: 8, minHeight: 84, textAlignVertical: 'top' }} />
                              {advDescription.trim().length > 0 ? (
                                <Box className="mb-2 p-2 rounded border border-border-200 bg-background-50">
                                  <Markdown>{advDescription}</Markdown>
                                </Box>
                              ) : null}
                            </>
                          )
                          if (item.k === 'sv') return <TextInput placeholder="Short Video URL" value={advShortVideoUrl} onChangeText={setAdvShortVideoUrl} style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10, marginBottom: 8 }} />
                          if (item.k === 'lv') return <TextInput placeholder="Long Video URL" value={advLongVideoUrl} onChangeText={setAdvLongVideoUrl} style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10, marginBottom: 8 }} />
                          return null
                        }}
                      />
                    </View>
                  )}
                </View>
                <View style={{ flexDirection: 'row', justifyContent: 'flex-end', marginTop: 12 }}>
                  <RNPressable onPress={() => setShowCreateExercise(false)} style={{ paddingVertical: 8, paddingHorizontal: 12, borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, marginRight: 8 }}>
                    <RNText style={{ color: '#374151', fontWeight: '600' }}>Cancel</RNText>
                  </RNPressable>
                  <RNPressable onPress={async () => {
                    const name = (newExerciseName || '').trim()
                    if (!name) return
                    try {
                      const parseCsv = (s: string) => (s || '').split(',').map(t => t.trim()).filter(Boolean)
                      const input: any = {
                        name,
                      }
                      if (advDifficulty.trim()) input.difficulty = advDifficulty.trim()
                      if (advBodyRegion.trim()) input.bodyRegion = advBodyRegion.trim()
                      const eq = parseCsv(advEquipmentCsv)
                      if (eq.length) input.equipment = eq
                      const pm = parseCsv(advPrimaryMusclesCsv)
                      if (pm.length) input.primaryMuscles = pm
                      const sm = parseCsv(advSecondaryMusclesCsv)
                      if (sm.length) input.secondaryMuscles = sm
                      const mp = parseCsv(advPatternsCsv)
                      if (mp.length) input.movementPatterns = mp
                      const pl = parseCsv(advPlanesCsv)
                      if (pl.length) input.planesOfMotion = pl
                      const tg = parseCsv(advTagsCsv)
                      if (tg.length) input.tags = tg
                      if (advDescription.trim()) input.description = advDescription.trim()
                      if (advShortVideoUrl.trim()) input.shortVideoUrl = advShortVideoUrl.trim()
                      if (advLongVideoUrl.trim()) input.longVideoUrl = advLongVideoUrl.trim()

                      const res = await createMovementMutation({ variables: { input } })
                      const local = res.data?.createMovement
                      if (local && pickerForBlock != null) {
                        addMovementToPrescription(pickerForBlock, { ...local, id_: local.id_ })
                      }
                      setShowCreateExercise(false)
                      setNewExerciseName('')
                      setShowAdvanced(false)
                      setAdvDifficulty('')
                      setAdvBodyRegion('')
                      setAdvEquipmentCsv('')
                      setAdvPrimaryMusclesCsv('')
                      setAdvSecondaryMusclesCsv('')
                      setAdvPatternsCsv('')
                      setAdvPlanesCsv('')
                      setAdvTagsCsv('')
                      setAdvShortVideoUrl('')
                      setAdvLongVideoUrl('')
                      setAdvDescription('')
                    } catch {}
                  }} style={{ paddingVertical: 8, paddingHorizontal: 12, borderRadius: 8, backgroundColor: '#111827' }}>
                    <RNText style={{ color: '#fff', fontWeight: '700' }}>Save</RNText>
                  </RNPressable>
                </View>
              </View>
            </KeyboardAvoidingView>
          </View>
        </Modal>
      </VStack>
    </SafeAreaView>
  )
}