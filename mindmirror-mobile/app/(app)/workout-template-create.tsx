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
import { QUERY_PRACTICE_TEMPLATES, useCreatePracticeTemplate, useMovementTemplate } from '@/services/api/practices'
import { Button, ButtonText } from '@/components/ui/button'
import { HStack } from '@/components/ui/hstack'
import { WebView } from 'react-native-webview'

// Import Phase 1 components
import {
  MovementCard,
  SummaryStatsHeader,
} from '@/components/workout'

// Flat builder types - no nested prescriptions
type BlockType = 'warmup' | 'workout' | 'cooldown'
type SetDraft = { position: number; reps?: number; duration?: number; loadValue?: number; loadUnit?: string; restDuration?: number }
type MovementDraft = {
  id: string // local React key
  name: string
  position: number
  block: BlockType
  metricUnit: 'iterative' | 'temporal'
  sets: SetDraft[]
  shortVideoUrl?: string
  movementId?: string
}

function YouTubeEmbed({ url }: { url: string }) {
  const vid = useMemo(() => {
    try {
      const u = new URL(url)
      if (u.hostname.includes('youtube.com')) {
        const v = u.searchParams.get('v')
        if (v) return v
        const parts = u.pathname.split('/')
        const idx = parts.findIndex((p) => p === 'embed' || p === 'shorts' || p === 'watch')
        if (idx >= 0 && parts[idx + 1]) return parts[idx + 1]
      }
      if (u.hostname.includes('youtu.be')) {
        return u.pathname.replace('/', '')
      }
    } catch {}
    return null
  }, [url])
  if (!vid) return null
  const src = `https://www.youtube.com/embed/${vid}?playsinline=1`
  return (
    <Box className="overflow-hidden rounded-xl border border-border-200" style={{ height: 200 }}>
      <WebView source={{ uri: src }} allowsInlineMediaPlayback javaScriptEnabled />
    </Box>
  )
}

function formatUnit(unit?: string | null) {
  if (!unit) return ''
  const s = String(unit).toLowerCase()
  if (s === 'bodyweight') return 'BW'
  return s.charAt(0).toUpperCase() + s.slice(1)
}

function formatLoad(loadValue?: number | null, loadUnit?: string | null) {
  const unit = (loadUnit || '').toString().toLowerCase()
  if (unit === 'bodyweight') return 'BW'
  if (typeof loadValue === 'number' && !Number.isNaN(loadValue)) {
    const prettyUnit = formatUnit(loadUnit as any)
    return `${loadValue} ${prettyUnit}`.trim()
  }
  return '—'
}

function DetailsTable({ movement }: { movement?: any }) {
  if (!movement) return null
  const rows: Array<{ label: string; value: string | null }> = [
    { label: 'Difficulty', value: movement.difficulty || null },
    { label: 'Body Region', value: movement.bodyRegion || null },
    { label: 'Equipment', value: Array.isArray(movement.equipment) && movement.equipment.length ? movement.equipment.join(', ') : null },
    { label: 'Primary Muscles', value: Array.isArray(movement.primaryMuscles) && movement.primaryMuscles.length ? movement.primaryMuscles.join(', ') : null },
    { label: 'Secondary Muscles', value: Array.isArray(movement.secondaryMuscles) && movement.secondaryMuscles.length ? movement.secondaryMuscles.join(', ') : null },
    { label: 'Movement Patterns', value: Array.isArray(movement.movementPatterns) && movement.movementPatterns.length ? movement.movementPatterns.join(', ') : null },
    { label: 'Planes of Motion', value: Array.isArray(movement.planesOfMotion) && movement.planesOfMotion.length ? movement.planesOfMotion.join(', ') : null },
  ].filter((r) => r.value)
  if (rows.length === 0) return null
  return (
    <VStack className="rounded-xl border border-border-200 divide-y divide-border-200 bg-background-0">
      {rows.map((r, i) => (
        <VStack key={`${r.label}-${i}`} className="flex-row items-start p-3">
          <Box className="w-40"><Text className="text-typography-700 text-sm font-semibold">{r.label}</Text></Box>
          <Box className="flex-1"><Text className="text-typography-900 text-sm dark:text-white">{r.value}</Text></Box>
        </VStack>
      ))}
    </VStack>
  )
}

export default function WorkoutTemplateCreateScreen() {
  const router = useRouter()
  const apollo = useApolloClient()
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')

  const [movements, setMovements] = useState<MovementDraft[]>([])

  // Movement search
  const [isPickerOpen, setPickerOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [runSearch, { data: searchData, loading: searching }] = useLazySearchMovements()

  useEffect(() => {
    if (!isPickerOpen) return
    const term = (searchTerm || '').trim()
    const h = setTimeout(() => { if (term.length > 0) runSearch({ variables: { searchTerm: term, limit: 25 } }) }, 250)
    return () => clearTimeout(h)
  }, [isPickerOpen, searchTerm, runSearch])

  const searchResults = useMemo(() => (searchData?.searchMovements || []).filter((r: any) => r?.isExternal === false), [searchData])

  const addMovement = (m: any) => {
    const newMovement: MovementDraft = {
      id: `${Date.now()}-${Math.random()}`,
      name: m.name,
      position: movements.length + 1,
      block: 'workout', // default
      metricUnit: 'iterative',
      sets: [{ position: 1, reps: 10, loadUnit: 'bodyweight', restDuration: 60 }],
      shortVideoUrl: m.shortVideoUrl,
      movementId: m.id_,
    }
    setMovements([...movements, newMovement])
  }

  const updateMovementBlock = (movementId: string, block: BlockType) => {
    setMovements(movements.map(m => m.id === movementId ? { ...m, block } : m))
  }

  const removeMovement = (movementId: string) => {
    setMovements(movements.filter(m => m.id !== movementId))
  }

  const addSet = (movementId: string) => {
    setMovements(movements.map(m => {
      if (m.id !== movementId) return m
      const lastSet = m.sets[m.sets.length - 1]
      const newSet: SetDraft = {
        position: m.sets.length + 1,
        reps: lastSet?.reps ?? 10,
        duration: lastSet?.duration,
        loadValue: lastSet?.loadValue,
        loadUnit: lastSet?.loadUnit ?? 'bodyweight',
        restDuration: lastSet?.restDuration ?? 60,
      }
      return { ...m, sets: [...m.sets, newSet] }
    }))
  }

  const removeSet = (movementId: string, setIndex: number) => {
    setMovements(movements.map(m => {
      if (m.id !== movementId) return m
      return {
        ...m,
        sets: m.sets.filter((_, i) => i !== setIndex).map((s, i) => ({ ...s, position: i + 1 }))
      }
    }))
  }

  // Set editing modal
  const [editingSet, setEditingSet] = useState<{ movementId: string; setIndex: number } | null>(null)
  const [editReps, setEditReps] = useState('')
  const [editDuration, setEditDuration] = useState('')
  const [editLoad, setEditLoad] = useState('')
  const [editRest, setEditRest] = useState('')

  const openSetEditor = (movementId: string, setIndex: number) => {
    const movement = movements.find(m => m.id === movementId)
    if (!movement) return
    const set = movement.sets[setIndex]
    if (!set) return

    setEditReps(String(set.reps ?? ''))
    setEditDuration(String(set.duration ?? ''))
    setEditLoad(String(set.loadValue ?? ''))
    setEditRest(String(set.restDuration ?? ''))
    setEditingSet({ movementId, setIndex })
  }

  const saveSetEdit = () => {
    if (!editingSet) return
    const { movementId, setIndex } = editingSet

    setMovements(movements.map(m => {
      if (m.id !== movementId) return m
      const updatedSet: SetDraft = {
        ...m.sets[setIndex],
        reps: editReps ? parseFloat(editReps) : undefined,
        duration: editDuration ? parseFloat(editDuration) : undefined,
        loadValue: editLoad ? parseFloat(editLoad) : undefined,
        restDuration: editRest ? parseFloat(editRest) : undefined,
      }
      const newSets = [...m.sets]
      newSets[setIndex] = updatedSet
      return { ...m, sets: newSets }
    }))

    setEditingSet(null)
  }

  const [createTemplate, { loading: saving }] = useCreatePracticeTemplate()
  const onSubmit = async () => {
    if (!title) return

    // Group movements by block for server
    const warmupMovements = movements.filter(m => m.block === 'warmup')
    const workoutMovements = movements.filter(m => m.block === 'workout')
    const cooldownMovements = movements.filter(m => m.block === 'cooldown')

    const gqlInput = {
      title,
      description: description || null,
      prescriptions: [
        {
          name: 'Warmup',
          position: 1,
          block: 'warmup',
          description: '',
          prescribedRounds: 1,
          movements: warmupMovements.map((m, i) => ({
            name: m.name,
            position: i + 1,
            metricUnit: m.metricUnit.toUpperCase(),
            metricValue: 1,
            description: '',
            movementClass: 'OTHER',
            prescribedSets: m.sets.length,
            restDuration: m.sets[0]?.restDuration ?? 60,
            videoUrl: m.shortVideoUrl,
            movementId: m.movementId,
            sets: m.sets.map(s => ({
              position: s.position,
              reps: s.reps,
              duration: s.duration,
              loadValue: s.loadValue,
              loadUnit: s.loadUnit,
              restDuration: s.restDuration,
            })),
          })),
        },
        {
          name: 'Workout',
          position: 2,
          block: 'workout',
          description: '',
          prescribedRounds: 1,
          movements: workoutMovements.map((m, i) => ({
            name: m.name,
            position: i + 1,
            metricUnit: m.metricUnit.toUpperCase(),
            metricValue: 1,
            description: '',
            movementClass: 'OTHER',
            prescribedSets: m.sets.length,
            restDuration: m.sets[0]?.restDuration ?? 60,
            videoUrl: m.shortVideoUrl,
            movementId: m.movementId,
            sets: m.sets.map(s => ({
              position: s.position,
              reps: s.reps,
              duration: s.duration,
              loadValue: s.loadValue,
              loadUnit: s.loadUnit,
              restDuration: s.restDuration,
            })),
          })),
        },
        {
          name: 'Cooldown',
          position: 3,
          block: 'cooldown',
          description: '',
          prescribedRounds: 1,
          movements: cooldownMovements.map((m, i) => ({
            name: m.name,
            position: i + 1,
            metricUnit: m.metricUnit.toUpperCase(),
            metricValue: 1,
            description: '',
            movementClass: 'OTHER',
            prescribedSets: m.sets.length,
            restDuration: m.sets[0]?.restDuration ?? 60,
            videoUrl: m.shortVideoUrl,
            movementId: m.movementId,
            sets: m.sets.map(s => ({
              position: s.position,
              reps: s.reps,
              duration: s.duration,
              loadValue: s.loadValue,
              loadUnit: s.loadUnit,
              restDuration: s.restDuration,
            })),
          })),
        },
      ],
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
    } catch (e) {
      console.error('Failed to create template:', e)
    }
  }

  const [previewMovementId, setPreviewMovementId] = useState<string | null>(null)
  const [previewDraft, setPreviewDraft] = useState<MovementDraft | null>(null)
  const movementQ = useMovementTemplate(previewMovementId || '')
  const mt = movementQ.data?.movementTemplate

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title="Create Workout Template" showBackButton onBackPress={() => router.back()} />
        <ScrollView className="flex-1">
          <VStack className="w-full max-w-screen-md mx-auto px-6 py-6" space="lg">
            <VStack space="sm">
              <Text className="text-2xl font-bold text-typography-900 dark:text-white">Template Details</Text>
              <Input className="bg-background-50 dark:bg-background-100"><InputField placeholder="Title" value={title} onChangeText={setTitle} /></Input>
              <Input className="bg-background-50 dark:bg-background-100"><InputField placeholder="Description (optional, markdown)" value={description} onChangeText={setDescription} /></Input>
            </VStack>

            {/* Summary Stats - shows workout overview */}
            <SummaryStatsHeader
              totalDuration={movements.reduce((sum, m) =>
                sum + m.sets.reduce((sSum, s) =>
                  sSum + (s.restDuration || 0) + (s.duration || 0), 0), 0)}
              totalExercises={movements.length}
              totalSets={movements.reduce((sum, m) => sum + m.sets.length, 0)}
            />

            <Box className="h-px bg-border-200 dark:bg-border-700 my-4" />

            {/* Add Movement Button */}
            <Pressable
              onPress={() => setPickerOpen(true)}
              className="px-4 py-3 rounded-xl border-2 border-dashed border-indigo-300 bg-indigo-50 dark:bg-indigo-900"
            >
              <Text className="text-center text-indigo-700 dark:text-indigo-200 font-semibold">+ Add Movement</Text>
            </Pressable>

            {/* Movements List */}
            <VStack space="md" className="mt-4">
              {movements.map(movement => (
                <MovementCard
                  key={movement.id}
                  movementName={movement.name}
                  block={movement.block}
                  sets={movement.sets}
                  shortVideoUrl={movement.shortVideoUrl}
                  metricUnit={movement.metricUnit}
                  onBlockChange={(block) => updateMovementBlock(movement.id, block)}
                  onRemove={() => removeMovement(movement.id)}
                  onAddSet={() => addSet(movement.id)}
                  onEditSet={(setIndex) => openSetEditor(movement.id, setIndex)}
                  onRemoveSet={(setIndex) => removeSet(movement.id, setIndex)}
                  onViewDetails={() => {
                    setPreviewMovementId(movement.movementId || '');
                    setPreviewDraft(movement);
                  }}
                />
              ))}
            </VStack>

            {/* Save Button */}
            <Pressable disabled={saving || !title} onPress={onSubmit} className={`mt-4 items-center justify-center rounded-xl px-4 py-3 ${saving || !title ? 'bg-indigo-300' : 'bg-indigo-600'}`}>
              <Text className="text-white font-bold">{saving ? 'Saving…' : 'Save Template'}</Text>
            </Pressable>
          </VStack>
        </ScrollView>

        {/* Movement search modal */}
        <Modal visible={isPickerOpen} transparent animationType="fade" onRequestClose={() => { setPickerOpen(false); setSearchTerm('') }}>
          <View style={{ flex: 1, alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.5)' }}>
            <RNPressable style={{ position: 'absolute', top: 0, bottom: 0, left: 0, right: 0 }} onPress={() => { setPickerOpen(false); setSearchTerm('') }} />
            <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={{ width: '100%', alignItems: 'center', paddingTop: Platform.OS === 'ios' ? 60 : 30 }}>
              <View style={{ width: '96%', maxWidth: 560, maxHeight: '70%', borderRadius: 16, backgroundColor: '#fff', padding: 16 }}>
                <RNText style={{ fontSize: 18, fontWeight: '600', marginBottom: 8 }}>Add Movement</RNText>
                <View style={{ marginBottom: 12 }}>
                  <TextInput
                    placeholder="Search movements…"
                    value={searchTerm}
                    onChangeText={setSearchTerm}
                    autoFocus
                    style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10 }}
                  />
                </View>
                {searching ? (
                  <View style={{ paddingVertical: 32, alignItems: 'center' }}>
                    <RNText style={{ color: '#6b7280' }}>Searching...</RNText>
                  </View>
                ) : (
                  <FlatList
                    keyboardDismissMode="on-drag"
                    keyboardShouldPersistTaps="handled"
                    data={searchResults}
                    keyExtractor={(item: any, i) => item.id_ ?? `${i}`}
                    renderItem={({ item }) => (
                      <RNPressable
                        onPress={() => {
                          addMovement(item);
                          setPickerOpen(false);
                          setSearchTerm('');
                        }}
                        style={{ paddingVertical: 10, borderTopWidth: 1, borderTopColor: '#e5e7eb' }}
                      >
                        <View>
                          <RNText style={{ fontWeight: '600' }}>{item.name}</RNText>
                          <RNText style={{ color: '#6b7280' }}>{item.bodyRegion}{Array.isArray(item.equipment) && item.equipment.length ? ` • ${item.equipment.join(', ')}` : ''}</RNText>
                        </View>
                      </RNPressable>
                    )}
                    ListEmptyComponent={(
                      <View style={{ paddingVertical: 16, alignItems: 'center' }}>
                        <RNText style={{ color: '#6b7280' }}>{(searchTerm||'').trim().length === 0 ? 'Type to search movements' : 'No matches found'}</RNText>
                      </View>
                    )}
                    style={{ maxHeight: '56%' }}
                    contentContainerStyle={{ paddingBottom: 12 }}
                  />
                )}
                <RNPressable onPress={() => { setPickerOpen(false); setSearchTerm('') }} style={{ alignSelf: 'flex-end', marginTop: 12, paddingVertical: 8, paddingHorizontal: 12, borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8 }}>
                  <RNText style={{ color: '#374151', fontWeight: '600' }}>Close</RNText>
                </RNPressable>
              </View>
            </KeyboardAvoidingView>
          </View>
        </Modal>

        {/* Set Edit Modal */}
        <Modal visible={editingSet !== null} transparent animationType="fade" onRequestClose={() => setEditingSet(null)}>
          <View style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'center', alignItems: 'center' }}>
            <RNPressable style={{ position: 'absolute', top: 0, bottom: 0, left: 0, right: 0 }} onPress={() => setEditingSet(null)} />
            <Box className="w-11/12 max-w-sm bg-white dark:bg-background-100 rounded-xl p-4">
              <Text className="text-lg font-bold mb-3">Edit Set</Text>
              <VStack space="sm">
                <Input className="bg-background-50">
                  <InputField placeholder="Reps" keyboardType="numeric" value={editReps} onChangeText={setEditReps} />
                </Input>
                <Input className="bg-background-50">
                  <InputField placeholder="Duration (s)" keyboardType="numeric" value={editDuration} onChangeText={setEditDuration} />
                </Input>
                <Input className="bg-background-50">
                  <InputField placeholder="Load Value" keyboardType="numeric" value={editLoad} onChangeText={setEditLoad} />
                </Input>
                <Input className="bg-background-50">
                  <InputField placeholder="Rest Duration (s)" keyboardType="numeric" value={editRest} onChangeText={setEditRest} />
                </Input>
                <Pressable onPress={saveSetEdit} className="mt-2 px-4 py-2 bg-indigo-600 rounded-lg">
                  <Text className="text-center text-white font-bold">Save</Text>
                </Pressable>
                <Pressable onPress={() => setEditingSet(null)} className="px-4 py-2 border border-border-200 rounded-lg">
                  <Text className="text-center font-semibold">Cancel</Text>
                </Pressable>
              </VStack>
            </Box>
          </View>
        </Modal>

      {/* Movement preview modal */}
      {previewMovementId ? (
        <View style={{ position: 'absolute', left: 0, right: 0, top: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.45)', justifyContent: 'center', alignItems: 'center', padding: 24 }}>
          <Box className="w-full max-w-md p-5 rounded-2xl bg-background-0 border border-border-200 dark:border-border-700">
            <VStack space="md">
              <Text className="text-xl font-bold text-typography-900 dark:text-white">{mt?.name || 'Exercise'}</Text>
              {mt?.movement?.shortVideoUrl ? (
                <Box className="overflow-hidden rounded-xl border border-border-200" style={{ height: 200 }}>
                  <WebView source={{ uri: `https://www.youtube.com/embed/${new URL(mt.movement.shortVideoUrl).searchParams.get('v')}` }} allowsInlineMediaPlayback javaScriptEnabled />
                </Box>
              ) : (
                <Box className="overflow-hidden rounded-xl border border-border-200 bg-background-50" style={{ height: 200, alignItems: 'center', justifyContent: 'center' }}>
                  <Text className="text-typography-600">🎥 Video placeholder</Text>
                </Box>
              )}
              {mt?.description ? <Text className="text-typography-700 dark:text-gray-300">{mt.description}</Text> : null}

              {(Array.isArray(mt?.sets) && mt!.sets.length > 0) ? (
                <VStack>
                  <VStack className="flex-row px-3 py-2 rounded bg-background-100 border border-border-200">
                    <Box className="w-10"><Text className="text-xs font-semibold text-typography-600">#</Text></Box>
                    <Box className="flex-1"><Text className="text-xs font-semibold text-typography-600">Reps/Dur</Text></Box>
                    <Box className="flex-1"><Text className="text-xs font-semibold text-typography-600">Load</Text></Box>
                    <Box className="flex-1"><Text className="text-xs font-semibold text-typography-600">Rest</Text></Box>
                  </VStack>
                  {mt!.sets.map((s: any, i: number) => (
                    <VStack key={s.id_ || i}>
                      <VStack className="flex-row items-center px-3 py-2 bg-white dark:bg-background-50">
                        <Box className="w-10"><Text className="text-typography-700">{i + 1}</Text></Box>
                        <Box className="flex-1"><Text className="text-typography-900">{s.reps ?? s.duration ?? '—'}</Text></Box>
                        <Box className="flex-1"><Text className="text-typography-900">{formatLoad(s.load_value, s.load_unit)}</Text></Box>
                        <Box className="flex-1"><Text className="text-typography-900">{s.rest_duration ? `${s.rest_duration}s` : '—'}</Text></Box>
                      </VStack>
                      <Box className="h-px bg-border-200" />
                    </VStack>
                  ))}
                </VStack>
              ) : null}

              <DetailsTable movement={mt?.movement} />

              <HStack className="justify-end space-x-3">
                <Button className="bg-gray-600" onPress={() => setPreviewMovementId(null)}>
                  <ButtonText>Dismiss</ButtonText>
                </Button>
                <Button className="bg-primary-600" onPress={() => { 
                  const id = previewMovementId;
                  const prefetch = previewDraft ? encodeURIComponent(JSON.stringify({
                    name: previewDraft.name,
                    description: previewDraft.description,
                    movement: undefined,
                    sets: (previewDraft.sets || []).map((s) => ({
                      reps: s.reps,
                      duration: s.duration,
                      rest_duration: s.restDuration,
                      load_value: s.loadValue,
                      load_unit: s.loadUnit,
                    })),
                    metric_value: previewDraft.metricValue,
                    metric_unit: previewDraft.metricUnit,
                    prescribed_sets: previewDraft.prescribedSets,
                    rest_duration: previewDraft.restDuration,
                    video_url: previewDraft.videoUrl,
                  })) : ''
                  setPreviewMovementId(null); setPreviewDraft(null);
                  router.push(`/(app)/exercise/${id}?${prefetch ? `prefetch=${prefetch}&` : ''}returnTo=${encodeURIComponent('/workout-template-create')}`)
                }}>
                  <ButtonText>More info</ButtonText>
                </Button>
              </HStack>
            </VStack>
          </Box>
        </View>
      ) : null}
      </VStack>
    </SafeAreaView>
  )
} 