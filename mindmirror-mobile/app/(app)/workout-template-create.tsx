import React, { useEffect, useMemo, useRef, useState } from 'react'
import { Modal, Platform, KeyboardAvoidingView, FlatList, Pressable as RNPressable, View, TextInput, Text as RNText } from 'react-native'
import { useRouter } from 'expo-router'
import dayjs from 'dayjs'
import { useLazySearchMovements } from '@/services/api/movements'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { VStack } from '@/components/ui/vstack'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { Input, InputField } from '@/components/ui/input'
import { Pressable } from '@/components/ui/pressable'
import { AppBar } from '@/components/common/AppBar'
import { ScrollView } from '@/components/ui/scroll-view'
import { useApolloClient } from '@apollo/client'
import { QUERY_PRACTICE_TEMPLATES, useCreatePracticeTemplate } from '@/services/api/practices'

// Reuse builder types
type SetDraft = { position: number; reps?: number; duration?: number; loadValue?: number; loadUnit?: string; restDuration?: number }
type MovementDraft = { name: string; position: number; metricUnit: 'iterative' | 'temporal' | 'breath' | 'other'; metricValue: number; description?: string; movementClass?: 'conditioning' | 'power' | 'strength' | 'mobility' | 'other'; prescribedSets?: number; restDuration?: number; videoUrl?: string; exerciseId?: string; movementId?: string; sets: SetDraft[] }
type PrescriptionDraft = { name: string; position: number; block: 'warmup' | 'workout' | 'cooldown' | 'other'; prescribedRounds: number; movements: MovementDraft[] }

export default function WorkoutTemplateCreateScreen() {
  const router = useRouter()
  const apollo = useApolloClient()
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')

  const [prescriptions, setPrescriptions] = useState<PrescriptionDraft[]>([
    { name: 'Warmup', position: 1, block: 'warmup', prescribedRounds: 1, movements: [] },
    { name: 'Workout', position: 2, block: 'workout', prescribedRounds: 1, movements: [] },
    { name: 'Cooldown', position: 3, block: 'cooldown', prescribedRounds: 1, movements: [] },
  ])

  // Movement search
  const [isPickerOpen, setPickerOpen] = useState(false)
  const [pickerForBlock, setPickerForBlock] = useState<number | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [runSearch, { data: searchData, loading: searching }] = useLazySearchMovements()

  useEffect(() => {
    if (!isPickerOpen) return
    const term = (searchTerm || '').trim()
    const h = setTimeout(() => { if (term.length > 0) runSearch({ variables: { searchTerm: term, limit: 25 } }) }, 250)
    return () => clearTimeout(h)
  }, [isPickerOpen, searchTerm, runSearch])

  const searchResults = useMemo(() => (searchData?.searchMovements || []).filter((r: any) => r?.isExternal === false), [searchData])

  const addMovementToPrescription = (pIndex: number, m: any) => {
    setPrescriptions((prev) => {
      const copy = [...prev]
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
        movementId: m.id_,
        sets: [{ position: 1, reps: 10, restDuration: 60, loadUnit: 'bodyweight' }],
      }
      p.movements = [...p.movements, newMovement]
      copy[pIndex] = p
      return copy
    })
  }

  const addSetToMovement = (pIndex: number, mIndex: number) => {
    setPrescriptions((prev) => {
      const copy = [...prev]
      const p = copy[pIndex]
      if (!p) return prev
      const mov = p.movements[mIndex]
      if (!mov) return prev
      const nextPos = mov.sets.length + 1
      const last = mov.sets[mov.sets.length - 1]
      const newSet: SetDraft = { position: nextPos }
      newSet.reps = (last?.reps ?? 10)
      if (last?.duration != null) newSet.duration = last.duration
      if (last?.loadValue != null) newSet.loadValue = last.loadValue
      newSet.loadUnit = last?.loadUnit ?? 'bodyweight'
      newSet.restDuration = (last?.restDuration ?? 60)
      mov.sets = [...mov.sets, newSet]
      p.movements[mIndex] = mov
      copy[pIndex] = p
      return copy
    })
  }

  const updateSetField = (pIndex: number, mIndex: number, sIndex: number, field: keyof SetDraft, value: string) => {
    setPrescriptions((prev) => {
      const copy = [...prev]
      const p = copy[pIndex]
      if (!p) return prev
      const mov = p.movements[mIndex]
      if (!mov) return prev
      const set = mov.sets[sIndex]
      if (!set) return prev
      let patched: any = value
      if (['reps','duration','loadValue','restDuration'].includes(field)) {
        const num = parseFloat(value)
        patched = Number.isFinite(num) ? num : undefined
      }
      mov.sets[sIndex] = { ...set, [field]: patched }
      p.movements[mIndex] = mov
      copy[pIndex] = p
      return copy
    })
  }

  const [createTemplate, { loading: saving }] = useCreatePracticeTemplate()
  const onSubmit = async () => {
    if (!title) return
    const gqlInput = {
      title,
      description: description || null,
      prescriptions: prescriptions.map((p) => ({
        name: p.name,
        position: p.position,
        block: p.block,
        description: '',
        prescribedRounds: p.prescribedRounds,
        movements: p.movements.map((m) => ({
          name: m.name,
          position: m.position,
          metricUnit: m.metricUnit.toUpperCase(),
          metricValue: m.metricValue,
          description: m.description || '',
          movementClass: (m.movementClass || 'other').toUpperCase(),
          prescribedSets: m.prescribedSets,
          restDuration: m.restDuration,
          videoUrl: m.videoUrl,
          exerciseId: m.exerciseId,
          sets: m.sets.map((s) => ({ position: s.position, reps: s.reps, duration: s.duration, restDuration: s.restDuration, loadValue: s.loadValue, loadUnit: s.loadUnit })),
        })),
      })),
    }
    try {
      const res = await createTemplate({ variables: { input: gqlInput } })
      apollo.refetchQueries({ include: [QUERY_PRACTICE_TEMPLATES] })
      const newId = res?.data?.createPracticeTemplate?.id_
      if (newId) {
        router.replace(`/program-create?addTemplateId=${newId}`)
      } else {
        router.back()
      }
    } catch {}
  }

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title="Create Workout Template" showBackButton onBackPress={() => router.back()} />
        <ScrollView className="flex-1">
          <VStack className="w-full max-w-screen-md mx-auto px-6 py-6" space="lg">
            <VStack space="sm">
              <Text className="text-2xl font-bold text-typography-900 dark:text-white">Template Details</Text>
              <Input className="bg-background-50 dark:bg-background-100"><InputField placeholder="Title" value={title} onChangeText={setTitle} /></Input>
              <Input className="bg-background-50 dark:bg-background-100"><InputField placeholder="Description (optional)" value={description} onChangeText={setDescription} /></Input>
            </VStack>

            <VStack space="md" className="mt-5">
              <Text className="text-lg font-semibold text-typography-900 dark:text-white">Blocks</Text>
              {prescriptions.map((item, index) => (
                <Box key={`${index}`} className="p-4 rounded-xl border bg-background-50 dark:bg-background-100 border-border-200 dark:border-border-700">
                  <VStack space="sm">
                    <Text className="text-base font-semibold text-typography-900 dark:text-white">{item.name}</Text>
                    <Pressable onPress={() => { setPickerForBlock(index); setPickerOpen(true); setSearchTerm('') }} className="self-start px-3 py-2 rounded-lg border border-indigo-300 dark:border-indigo-700 bg-white dark:bg-indigo-950">
                      <Text className="text-indigo-700 dark:text-indigo-200 font-semibold">＋ Add Movement</Text>
                    </Pressable>

                    {item.movements.length === 0 ? (
                      <Text className="text-typography-600 dark:text-gray-300">No movements yet</Text>
                    ) : (
                      <VStack space="sm">
                        {item.movements.map((m, mi) => (
                          <Box key={`${mi}`} className="p-3 rounded-lg border bg-white dark:bg-background-0 border-border-200 dark:border-border-700">
                            <VStack space="sm">
                              <Box className="flex-row items-center justify-between">
                                <Text className="font-semibold text-typography-900 dark:text-white">{m.name}</Text>
                                <Pressable onPress={() => {
                                  setPrescriptions(prev => {
                                    const copy = [...prev]
                                    const p = copy[index]
                                    if (!p) return prev
                                    p.movements = p.movements.filter((_, i) => i !== mi).map((mv, i) => ({ ...mv, position: i + 1 }))
                                    copy[index] = p
                                    return copy
                                  })
                                }} className="px-2 py-1 rounded-md border border-red-300">
                                  <Text className="text-red-700 font-semibold">🗑️</Text>
                                </Pressable>
                              </Box>
                              <Text className="text-typography-600 dark:text-gray-300">{m.sets.length} sets</Text>
                              <Pressable onPress={() => addSetToMovement(index, mi)} className="self-start px-3 py-1.5 rounded-md border border-border-200 dark:border-border-700">
                                <Text className="text-typography-700 dark:text-gray-200 font-semibold">Add Set</Text>
                              </Pressable>

                              {/* Set editor table */}
                              {m.sets.length > 0 && (
                                <VStack space="xs">
                                  <Box className="flex-row items-center px-2 py-1">
                                    <Box className="w-12"><Text className="text-typography-600 dark:text-gray-300">#</Text></Box>
                                    <Box className="flex-1"><Text className="text-typography-600 dark:text-gray-300">{m.metricUnit === 'temporal' ? 'Duration (s)' : 'Reps'}</Text></Box>
                                    <Box className="flex-1"><Text className="text-typography-600 dark:text-gray-300">Load</Text></Box>
                                    <Box className="w-28"><Text className="text-typography-600 dark:text-gray-300">Unit</Text></Box>
                                    <Box className="w-28"><Text className="text-typography-600 dark:text-gray-300">Rest (s)</Text></Box>
                                  </Box>
                                  {m.sets.map((s, si) => (
                                    <Box key={`${si}`} className="flex-row items-center px-2 py-1 rounded-md border border-border-200 dark:border-border-700 bg-background-50 dark:bg-background-100">
                                      <Box className="w-12"><Text className="text-typography-700 dark:text-gray-200">{si + 1}</Text></Box>
                                      <Box className="flex-1 mr-2">
                                        <TextInput keyboardType="numeric" value={m.metricUnit === 'temporal' ? (s.duration != null ? String(s.duration) : '') : (s.reps != null ? String(s.reps) : '')} onChangeText={(v) => updateSetField(index, mi, si, m.metricUnit === 'temporal' ? 'duration' : 'reps', v)} placeholder={m.metricUnit === 'temporal' ? '30' : '10'} style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, paddingHorizontal: 10, paddingVertical: 8, backgroundColor: '#fff' }} />
                                      </Box>
                                      <Box className="flex-1 mr-2">
                                        <TextInput keyboardType="numeric" value={s.loadValue != null ? String(s.loadValue) : ''} onChangeText={(v) => updateSetField(index, mi, si, 'loadValue', v)} placeholder="45" style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, paddingHorizontal: 10, paddingVertical: 8, backgroundColor: '#fff' }} />
                                      </Box>
                                      <Box className="w-28 mr-2">
                                        <Input><InputField placeholder="unit (lb/kg/bw)" defaultValue={s.loadUnit || ''} onChangeText={(v) => updateSetField(index, mi, si, 'loadUnit', v)} /></Input>
                                      </Box>
                                      <Box className="w-28 mr-2">
                                        <TextInput keyboardType="numeric" value={s.restDuration != null ? String(s.restDuration) : ''} onChangeText={(v) => updateSetField(index, mi, si, 'restDuration', v)} placeholder="60" style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, paddingHorizontal: 10, paddingVertical: 8, backgroundColor: '#fff' }} />
                                      </Box>
                                    </Box>
                                  ))}
                                </VStack>
                              )}
                            </VStack>
                          </Box>
                        ))}
                      </VStack>
                    )}
                  </VStack>
                </Box>
              ))}

              <Pressable disabled={saving || !title} onPress={onSubmit} className={`mt-2 items-center justify-center rounded-xl px-4 py-3 ${saving || !title ? 'bg-indigo-300' : 'bg-indigo-600'}`}>
                <Text className="text-white font-bold">{saving ? 'Saving…' : 'Save Template'}</Text>
              </Pressable>
            </VStack>
          </VStack>
        </ScrollView>

        {/* Movement search modal */}
        <Modal visible={isPickerOpen} transparent animationType="fade" onRequestClose={() => { setPickerOpen(false); setPickerForBlock(null); setSearchTerm('') }}>
          <View style={{ flex: 1, alignItems: 'center' }}>
            <RNPressable style={{ position: 'absolute', top: 0, bottom: 0, left: 0, right: 0, backgroundColor: 'rgba(0,0,0,0.4)' }} onPress={() => { setPickerOpen(false); setPickerForBlock(null); setSearchTerm('') }} />
            <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={{ width: '100%', alignItems: 'center', paddingTop: Platform.OS === 'ios' ? 60 : 30 }}>
              <View style={{ width: '96%', maxHeight: '70%', borderRadius: 16, backgroundColor: '#fff', padding: 16 }}>
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
                  style={{ maxHeight: '56%' }}
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