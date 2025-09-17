import React, { useMemo, useRef, useState, useEffect } from 'react'
import { useLocalSearchParams, useRouter } from 'expo-router'
import { AppBar } from '@/components/common/AppBar'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { VStack } from '@/components/ui/vstack'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { Pressable } from '@/components/ui/pressable'
import { ActivityIndicator, ScrollView, Alert, Modal, View, Image, Platform } from 'react-native'
import { Input, InputField } from '@/components/ui/input'
import { useTodaysWorkouts, usePracticeInstance, useDeletePracticeInstance, useCompleteWorkout, useUpdateSetInstance, useCompleteSetInstance, useCreateSetInstance, useDeferPractice, useMyUpcomingPractices } from '@/services/api/practices'
import { QUERY_TODAYS_SCHEDULABLES } from '@/services/api/users'
import { useApolloClient } from '@apollo/client'
import dayjs from 'dayjs'
import { WebView } from 'react-native-webview'
import { Video, ResizeMode } from 'expo-av'

function YouTubeEmbed({ url }: { url: string }) {
  const vid = React.useMemo(() => {
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
    <Box className="overflow-hidden rounded-xl border border-border-200" style={{ height: 180 }}>
      <WebView source={{ uri: src }} allowsInlineMediaPlayback javaScriptEnabled />
    </Box>
  )
}

function fmtLoadBW(loadValue?: number, loadUnit?: string) {
  const unit = (loadUnit || '').toString().toLowerCase()
  if (unit === 'bodyweight') return 'BW'
  if (typeof loadValue === 'number' && !Number.isNaN(loadValue)) return `${loadValue} ${unit}`
  return '—'
}

export default function WorkoutDetailsScreen() {
  const params = useLocalSearchParams<{ id: string, enrollmentId?: string }>()
  const router = useRouter()
  const apollo = useApolloClient()
  const workoutId = params.id
  const enrollmentId = params.enrollmentId
  const onDate = dayjs().format('YYYY-MM-DD')

  const { data, loading, error } = useTodaysWorkouts(onDate)
  const fallbackQ = usePracticeInstance(workoutId || '')
  const [deletePracticeInstance] = useDeletePracticeInstance()
  const [completeWorkoutMutation] = useCompleteWorkout()
  const [updateSetInstance] = useUpdateSetInstance()
  const [completeSetInstance] = useCompleteSetInstance()
  const [createSetInstance] = useCreateSetInstance()
  const [deferPractice] = useDeferPractice()
  const upcoming = useMyUpcomingPractices()
  const [deferOpen, setDeferOpen] = useState(false)

  const serverWorkout = data?.todaysWorkouts?.find((w: any) => w.id_ === workoutId) || fallbackQ.data?.practiceInstance

  const [workout, setWorkout] = useState<any | null>(null)
  useEffect(() => { if (serverWorkout) setWorkout(JSON.parse(JSON.stringify(serverWorkout))) }, [serverWorkout])

  const [elapsed, setElapsed] = useState(0)
  const [timerActive, setTimerActive] = useState(false)
  useEffect(() => { if (!timerActive) return; const t = setInterval(() => setElapsed((e) => e + 1), 1000); return () => clearInterval(t) }, [timerActive])
  const toggleTimer = () => setTimerActive((t) => !t)
  const startTimerIfIdle = () => { if (!timerActive) setTimerActive(true) }
  const fmtMinSec = (s: number) => `${String(Math.floor(s/60)).padStart(2,'0')}:${String(s%60).padStart(2,'0')}`

  // Debug logging
  console.log('DEBUG workout screen:', {
    workoutId,
    loading,
    fallbackLoading: fallbackQ.loading,
    fallbackError: fallbackQ.error,
    fallbackData: fallbackQ.data,
    serverWorkout,
    workout
  })

  const totals = useMemo(() => {
    const prescriptions: any[] = Array.isArray(workout?.prescriptions) ? workout!.prescriptions : []
    let movements = 0, sets = 0
    prescriptions.forEach((p: any) => { const ms = Array.isArray(p?.movements) ? p.movements : []; movements += ms.length; ms.forEach((m: any) => { sets += (Array.isArray(m?.sets) ? m.sets.length : 0) }) })
    return { movements, sets }
  }, [workout])

  const handleDelete = () => {
    Alert.alert('Delete Workout?', 'This cannot be undone.', [ { text: 'Cancel', style: 'cancel' }, { text: 'Delete', style: 'destructive', onPress: async () => { try { await deletePracticeInstance({ variables: { id: workoutId } }); router.back() } catch {} } } ])
  }

  const onChangeSetField = async (pIdx: number, mIdx: number, sIdx: number, field: 'reps'|'loadValue', value: string) => {
    if (!workout) return; startTimerIfIdle()
    // local update first
    setWorkout((prev: any) => { const copy = JSON.parse(JSON.stringify(prev)); const set = copy.prescriptions?.[pIdx]?.movements?.[mIdx]?.sets?.[sIdx]; if (set) { const num = parseFloat(value); set[field] = Number.isFinite(num) ? num : undefined } return copy })
    // persist
    const setId = workout?.prescriptions?.[pIdx]?.movements?.[mIdx]?.sets?.[sIdx]?.id_
    if (setId) {
      const num = parseFloat(value)
      const input: any = { [field]: Number.isFinite(num) ? num : null }
      try { await updateSetInstance({ variables: { id: setId, input } }) } catch {}
    }
  }

  const addSetToMovement = async (pIdx: number, mIdx: number) => {
    if (!workout) return; startTimerIfIdle()
    const movement = workout?.prescriptions?.[pIdx]?.movements?.[mIdx]
    const movementInstanceId = movement?.id_
    const last = (movement?.sets || [])[movement?.sets?.length - 1] || {}
    // optimistic local
    setWorkout((prev: any) => { const copy = JSON.parse(JSON.stringify(prev)); const sets: any[] = copy.prescriptions?.[pIdx]?.movements?.[mIdx]?.sets || []; sets.push({ id_: `tmp_${Date.now()}`, reps: last.reps ?? 10, loadValue: last.loadValue ?? 0, loadUnit: last.loadUnit ?? 'kg', restDuration: last.restDuration ?? movement?.restDuration ?? 60, complete: false, movementInstanceId }); copy.prescriptions[pIdx].movements[mIdx].sets = sets; return copy })
    // persist create
    if (movementInstanceId) {
      const input = { movementInstanceId, position: (movement?.sets?.length || 0) + 1, reps: last.reps ?? 10, loadValue: last.loadValue ?? 0, loadUnit: (last.loadUnit || 'kg').toLowerCase(), restDuration: last.restDuration ?? movement?.restDuration ?? 60, complete: false }
      try {
        const res = await createSetInstance({ variables: { input } })
        const created = res.data?.createSetInstance
        if (created?.id_) {
          // replace tmp id with real
          setWorkout((prev: any) => { const copy = JSON.parse(JSON.stringify(prev)); const sets: any[] = copy.prescriptions?.[pIdx]?.movements?.[mIdx]?.sets || []; const idx = sets.findIndex((s: any) => String(s.id_).startsWith('tmp_')); if (idx >= 0) sets[idx] = { ...sets[idx], id_: created.id_ }; copy.prescriptions[pIdx].movements[mIdx].sets = sets; return copy })
        }
      } catch {}
    }
  }

  const markSetComplete = (pIdx: number, mIdx: number, sIdx: number) => {
    setWorkout((prev: any) => { const copy = JSON.parse(JSON.stringify(prev)); const set = copy.prescriptions?.[pIdx]?.movements?.[mIdx]?.sets?.[sIdx]; if (set) set.complete = true; return copy })
  }

  // Rest timer
  const [restOpen, setRestOpen] = useState(false)
  const [restSeconds, setRestSeconds] = useState(0)
  const [restCtx, setRestCtx] = useState<{ pIdx: number, mIdx: number, sIdx: number } | null>(null)
  const restTimerRef = useRef<NodeJS.Timeout | null>(null)
  const openRestTimer = (pIdx: number, mIdx: number, sIdx: number, initial: number) => {
    setRestCtx({ pIdx, mIdx, sIdx }); setRestSeconds(Math.max(0, initial || 0)); setRestOpen(true); if (restTimerRef.current) clearInterval(restTimerRef.current); restTimerRef.current = setInterval(() => setRestSeconds((s) => Math.max(0, s - 1)), 1000)
  }
  const closeRestTimer = async (complete: boolean) => {
    setRestOpen(false); if (restTimerRef.current) { clearInterval(restTimerRef.current); restTimerRef.current = null }
    if (complete && restCtx) {
      const setId = workout?.prescriptions?.[restCtx.pIdx]?.movements?.[restCtx.mIdx]?.sets?.[restCtx.sIdx]?.id_
      markSetComplete(restCtx.pIdx, restCtx.mIdx, restCtx.sIdx)
      if (setId) { try { await completeSetInstance({ variables: { id: setId } }) } catch {} }
    }
  }
  const adjustRest = (delta: number) => setRestSeconds((s) => Math.max(0, s + delta))

  const onCompleteWorkout = async () => {
    try {
      await completeWorkoutMutation({ variables: { id: workoutId } })
      // Refetch home schedulables
      const userId = '' // if you have auth context, pass real userId
      const date = onDate
      apollo.refetchQueries({ include: [QUERY_TODAYS_SCHEDULABLES] })
      router.back()
    } catch {}
  }

  if ((loading || fallbackQ.loading) && !workout) {
    return (
      <SafeAreaView>
        <VStack className="h-full w-full items-center justify-center bg-background-0">
          <ActivityIndicator />
          <Text className="mt-2 text-typography-500">Loading workout...</Text>
          {fallbackQ.error && <Text className="mt-2 text-red-500">Error: {fallbackQ.error.message}</Text>}
        </VStack>
      </SafeAreaView>
    )
  }

  // If both queries finished but no workout found
  if (!loading && !fallbackQ.loading && !workout) {
    return (
      <SafeAreaView>
        <VStack className="h-full w-full items-center justify-center bg-background-0">
          <AppBar title="Workout Not Found" showBackButton onBackPress={() => { try { router.replace('/journal') } catch { router.back() } }} />
          <Text className="text-typography-500">Workout not found</Text>
          <Text className="mt-2 text-xs text-typography-400">ID: {workoutId}</Text>
          {(error || fallbackQ.error) && (
            <Text className="mt-2 text-red-500">
              Error: {error?.message || fallbackQ.error?.message}
            </Text>
          )}
        </VStack>
      </SafeAreaView>
    )
  }

  const MovementFrozen = ({ m, pIdx, mIdx }: { m: any; pIdx: number; mIdx: number }) => (
    <Box className="rounded-xl border border-border-200 bg-white dark:bg-background-100">
      <VStack className="p-4">
        <VStack className="flex-row items-center justify-between">
          <Text className="text-base font-semibold text-typography-900 dark:text-white">{m.name}</Text>
          <Text className="text-typography-500 text-sm">{(Array.isArray(m.sets) ? m.sets.length : 0)} sets</Text>
        </VStack>
        <Box className="h-2" />
        {/* Thumbnail: prefer image (png/gif), else mp4 video, else YouTube, else placeholder */}
        {(() => {
          const imgUrl = m.imageUrl || m.gifUrl
          const vidUrl = m.shortVideoUrl || m.longVideoUrl || m.videoUrl
          if (typeof imgUrl === 'string' && /\.(png|jpg|jpeg|gif)$/i.test(imgUrl)) {
            return (
              <Box className="overflow-hidden rounded-xl border border-border-200" style={{ height: 160, alignItems: 'center', justifyContent: 'center' }}>
                <Image source={{ uri: imgUrl }} style={{ width: '100%', height: '100%', resizeMode: 'cover' }} />
              </Box>
            )
          }
          if (typeof vidUrl === 'string' && /\.mp4$/i.test(vidUrl)) {
            return (
              <Box className="overflow-hidden rounded-xl border border-border-200" style={{ height: 180, alignItems: 'center', justifyContent: 'center' }}>
                <Video
                  style={{ width: '100%', height: '100%' }}
                  source={{ uri: vidUrl }}
                  useNativeControls
                  resizeMode={ResizeMode.COVER}
                />
              </Box>
            )
          }
          if (typeof vidUrl === 'string' && (vidUrl.includes('youtube.com') || vidUrl.includes('youtu.be'))) {
            return <YouTubeEmbed url={vidUrl} />
          }
          return (
            <Box className="overflow-hidden rounded-xl border border-border-200 bg-background-100" style={{ height: 120, alignItems: 'center', justifyContent: 'center' }}>
              <Text className="text-typography-500">No preview</Text>
            </Box>
          )
        })()}
        <VStack>
          <VStack className="flex-row px-3 py-2 rounded bg-background-100 border border-border-200">
            <Box className="w-10"><Text className="text-xs font-semibold text-typography-600">#</Text></Box>
            <Box className="flex-1"><Text className="text-xs font-semibold text-typography-600">Reps</Text></Box>
            <Box className="flex-1"><Text className="text-xs font-semibold text-typography-600">Load</Text></Box>
            <Box className="flex-1"><Text className="text-xs font-semibold text-typography-600">Rest</Text></Box>
            <Box className="w-12" />
          </VStack>
          {(Array.isArray(m.sets) ? m.sets : []).map((s: any, i: number) => (
            <VStack key={i}>
              <VStack className="flex-row items-center px-3 py-2 bg-white dark:bg-background-50">
                <Box className="w-10"><Text className="text-typography-700">{i + 1}</Text></Box>
                <Box className="flex-1">
                  <Input size="sm" isDisabled={!!s.complete}>
                    <InputField
                      keyboardType="numeric"
                      defaultValue={typeof s.reps === 'number' ? String(s.reps) : ''}
                      placeholder="—"
                      onChangeText={(v) => onChangeSetField(pIdx, mIdx, i, 'reps', v)}
                      onFocus={startTimerIfIdle}
                    />
                  </Input>
                </Box>
                <Box className="flex-1">
                  <Input size="sm" isDisabled={!!s.complete}>
                    <InputField
                      keyboardType="numeric"
                      defaultValue={typeof s.loadValue === 'number' ? String(s.loadValue) : ''}
                      placeholder="—"
                      onChangeText={(v) => onChangeSetField(pIdx, mIdx, i, 'loadValue', v)}
                      onFocus={startTimerIfIdle}
                    />
                  </Input>
                </Box>
                <Box className="flex-1">
                  <Text className="text-typography-500">
                    {typeof s.restDuration === 'number' && s.restDuration > 0 ? `${s.restDuration}s` : (typeof m.restDuration === 'number' ? `${m.restDuration}s` : '—')}
                  </Text>
                </Box>
                <Box className="w-12">
                  <Pressable
                    className={`px-2 py-1 rounded border ${s.complete ? 'border-border-200 bg-background-100' : 'border-border-200 bg-background-50'}`}
                    onPress={async () => {
                      const secs = (typeof s.restDuration === 'number' && s.restDuration > 0) ? s.restDuration : (typeof m.restDuration === 'number' ? m.restDuration : 60)
                      openRestTimer(pIdx, mIdx, i, secs)
                      startTimerIfIdle()
                    }}
                  >
                    <Text className={`${s.complete ? 'text-typography-400' : 'text-typography-700'}`}>✓</Text>
                  </Pressable>
                </Box>
              </VStack>
              <Box className="h-px bg-border-200" />
            </VStack>
          ))}
        </VStack>
        <Box className="h-2" />
        <Pressable className="self-start px-3 py-1 rounded border border-border-200 bg-background-50" onPress={() => addSetToMovement(pIdx, mIdx)}>
          <Text className="text-typography-700 text-xs">+ Add Set</Text>
        </Pressable>
      </VStack>
    </Box>
  )

  const BlockFrozen = ({ p, idx }: { p: any; idx: number }) => (
    <VStack>
      <Text className="text-sm font-semibold text-typography-900 dark:text-white">
        {p?.name || String(p?.block || '').toUpperCase() || `Block ${idx + 1}`}
      </Text>
      <Box className="h-2" />
      {(Array.isArray(p.movements) ? p.movements : []).map((m: any, i: number) => (
        <VStack key={i}>
          <MovementFrozen m={m} pIdx={idx} mIdx={i} />
          <Box className="h-3" />
        </VStack>
      ))}
    </VStack>
  )

  return (
    <SafeAreaView>
      <VStack className="h-full w-full bg-background-0">
        <AppBar title="Workout" showBackButton onBackPress={() => { try { router.replace('/journal') } catch { router.back() } }} />
        <Pressable className="absolute top-0 right-0 p-2" onPress={handleDelete}>
          <Text className="text-red-600">Delete</Text>
        </Pressable>

        <ScrollView showsVerticalScrollIndicator={false} className="flex-1">
          <VStack className="w-full max-w-screen-md mx-auto">
            {/* Title + Metadata Panel */}
            <VStack className="px-6 pt-4">
              <VStack className="flex-row items-center justify-between">
                <Text className="text-2xl font-bold text-typography-900 dark:text-white">{workout?.title || 'Workout'}</Text>
                <VStack className="flex-row items-center space-x-2">
                  {enrollmentId ? (
                    <Pressable className="px-3 py-1 rounded-full border border-border-200 bg-background-50" onPress={() => setDeferOpen(true)}>
                      <Text className="text-typography-900 text-xs">Defer</Text>
                    </Pressable>
                  ) : null}
                  <Pressable className={`px-3 py-1 rounded-full border border-border-200 ${timerActive ? 'bg-green-50' : 'bg-background-50'}`} onPress={toggleTimer}>
                    <Text className="text-typography-900 text-xs">{timerActive ? 'Pause' : (elapsed > 0 ? 'Resume' : 'Start')} workout</Text>
                  </Pressable>
                </VStack>
              </VStack>
              <Box className="h-2" />
              <Box className="rounded-2xl border border-border-200 bg-white dark:bg-background-100">
                <VStack className="p-4">
                  <VStack className="flex-row">
                    <Box className="flex-1">
                      <Text className="text-xs text-typography-500">Date</Text>
                      <Text className="text-sm font-semibold text-typography-900">{dayjs(workout?.date).format('MMM DD, YYYY')}</Text>
                    </Box>
                    <Box className="flex-1">
                      <Text className="text-xs text-typography-500">Duration</Text>
                      <Text className="text-sm font-semibold text-typography-900">{fmtMinSec(elapsed)}</Text>
                    </Box>
                    <Box className="flex-1">
                      <Text className="text-xs text-typography-500">Movements</Text>
                      <Text className="text-sm font-semibold text-typography-900">{totals.movements}</Text>
                    </Box>
                    <Box className="flex-1">
                      <Text className="text-xs text-typography-500">Sets</Text>
                      <Text className="text-sm font-semibold text-typography-900">{totals.sets}</Text>
                    </Box>
                  </VStack>
                  <Box className="h-3" />
                  <Text className="text-xs text-typography-500">Notes</Text>
                  <Text className="text-sm text-typography-900">{workout?.description || '—'}</Text>
                </VStack>
              </Box>
            </VStack>

            {/* Section Header like Home */}
            <Box className="px-6 pt-6">
              <VStack className="flex-row items-center justify-between">
                <Text className="text-sm font-semibold text-typography-900">Today's Workout</Text>
                <Text className="text-xs text-typography-500">{dayjs(workout?.date).format('dddd')}</Text>
              </VStack>
            </Box>

            {/* Divider */}
            <Box className="mx-6 my-3 h-px bg-border-200" />

            {/* Workout Blocks */}
            <VStack className="px-6 pb-6">
              {(Array.isArray(workout?.prescriptions) ? workout.prescriptions : []).map((p: any, idx: number) => (
                <VStack key={idx}>
                  <BlockFrozen p={p} idx={idx} />
                  <Box className="h-4" />
                </VStack>
              ))}
            </VStack>

            {/* Complete Workout */}
            <VStack className="px-6 pb-20">
              <Pressable className="px-4 py-3 rounded-xl border border-border-200 bg-indigo-50" onPress={onCompleteWorkout}>
                <Text className="text-indigo-700 text-center font-semibold">Complete Workout</Text>
              </Pressable>
            </VStack>
          </VStack>
        </ScrollView>

        {/* Rest Timer Bottom Sheet */}
        <Modal visible={restOpen} transparent animationType="slide" onRequestClose={() => closeRestTimer(false)}>
          <VStack className="flex-1 justify-end bg-black/40">
            <Box className="rounded-t-2xl bg-white dark:bg-background-0 p-4">
              <Text className="text-center text-xl font-bold text-typography-900">Rest</Text>
              <Box className="h-2" />
              <Text className="text-center text-3xl font-bold text-typography-900">{fmtMinSec(restSeconds)}</Text>
              <Box className="h-4" />
              <VStack className="flex-row items-center justify-between">
                <Pressable className="px-4 py-2 rounded-lg border border-border-200" onPress={() => adjustRest(-15)}><Text className="text-typography-900">-15s</Text></Pressable>
                <Pressable className="px-4 py-2 rounded-lg border border-border-200" onPress={() => closeRestTimer(true)}><Text className="text-typography-900">Skip</Text></Pressable>
                <Pressable className="px-4 py-2 rounded-lg border border-border-200" onPress={() => adjustRest(15)}><Text className="text-typography-900">+15s</Text></Pressable>
              </VStack>
            </Box>
          </VStack>
        </Modal>
      </VStack>

      {/* Defer modal */}
      <Modal visible={!!deferOpen} transparent animationType="fade" onRequestClose={() => setDeferOpen(false)}>
        <Pressable onPress={() => setDeferOpen(false)} style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.4)', justifyContent: 'flex-end' }}>
          <View style={{ backgroundColor: '#fff', padding: 16, borderTopLeftRadius: 12, borderTopRightRadius: 12 }}>
            <Text className="text-typography-900" style={{ fontWeight: '700', fontSize: 16, marginBottom: 8 }}>Defer Workout</Text>
            <Pressable onPress={async () => { try { await deferPractice({ variables: { enrollmentId, mode: 'push' } }); setDeferOpen(false); upcoming.refetch && upcoming.refetch(); apollo.refetchQueries({ include: [QUERY_TODAYS_SCHEDULABLES] }) } catch {} }} style={{ paddingVertical: 12 }}>
              <Text className="text-typography-900">Push today’s workout to tomorrow</Text>
            </Pressable>
            <View style={{ height: 1, backgroundColor: '#e5e7eb' }} />
            <Pressable onPress={async () => { try { await deferPractice({ variables: { enrollmentId, mode: 'shift' } }); setDeferOpen(false); upcoming.refetch && upcoming.refetch(); apollo.refetchQueries({ include: [QUERY_TODAYS_SCHEDULABLES] }) } catch {} }} style={{ paddingVertical: 12 }}>
              <Text className="text-typography-900">Shift entire schedule forward by one day</Text>
            </Pressable>
            <View style={{ height: 1, backgroundColor: '#e5e7eb' }} />
            <Pressable onPress={() => setDeferOpen(false)} style={{ paddingVertical: 12 }}>
              <Text style={{ color: '#ef4444', fontWeight: '600' }}>Cancel</Text>
            </Pressable>
          </View>
        </Pressable>
      </Modal>

    </SafeAreaView>
  )
}
