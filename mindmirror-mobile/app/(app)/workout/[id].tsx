import React, { useMemo, useRef, useState, useEffect } from 'react'
import { useLocalSearchParams, useRouter } from 'expo-router'
import { AppBar } from '@/components/common/AppBar'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { VStack } from '@/components/ui/vstack'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { Pressable } from '@/components/ui/pressable'
import { ActivityIndicator, Alert, Modal, View, Image, Platform } from 'react-native'
import { ScrollView } from '@/components/ui/scroll-view'
import Markdown from 'react-native-markdown-display'
import { Input, InputField } from '@/components/ui/input'
import { useTodaysWorkouts, usePracticeInstance, useDeletePracticeInstance, useCompleteWorkout, useUpdateSetInstance, useCompleteSetInstance, useCreateSetInstance, useDeferPractice, useMyUpcomingPractices } from '@/services/api/practices'
import { QUERY_TODAYS_SCHEDULABLES } from '@/services/api/users'
import { QUERY_TODAYS_WORKOUTS, QUERY_MY_UPCOMING_PRACTICES } from '@/services/api/practices'
import { useApolloClient } from '@apollo/client'
import dayjs from 'dayjs'
import { WebView } from 'react-native-webview'
import { useVideoPlayer, VideoView } from 'expo-video'
import { MovementDescription } from '@/components/workouts/MovementMedia'
import { RestTimerModal } from '@/components/workouts/RestTimerModal'

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
  const [videoOpenByKey, setVideoOpenByKey] = useState<Record<string, boolean>>({})
  const [descOpenByKey, setDescOpenByKey] = useState<Record<string, boolean>>({})
  const [notesOpen, setNotesOpen] = useState<boolean>(false)
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState<boolean>(false)
  const toggleVideoFor = (key: string) => setVideoOpenByKey(prev => ({ ...prev, [key]: !prev[key] }))
  const toggleDescFor = (key: string) => setDescOpenByKey(prev => ({ ...prev, [key]: !prev[key] }))
  const VideoPreview = ({ url }: { url: string }) => {
    const videoUrl = (url || '').trim()
    if (!videoUrl) return (
      <Box className="overflow-hidden rounded-xl border border-border-200 bg-background-100" style={{ height: 120, alignItems: 'center', justifyContent: 'center' }}>
        <Text className="text-typography-500">No preview</Text>
      </Box>
    )
    const isMp4 = /\.mp4$/i.test(videoUrl)
    if (isMp4) {
      const player = useVideoPlayer(videoUrl, (p) => { p.loop = false })
      return (
        <Box className="overflow-hidden rounded-xl border border-border-200" style={{ height: 180 }}>
          <VideoView style={{ width: '100%', height: '100%' }} player={player} allowsFullscreen allowsPictureInPicture />
        </Box>
      )
    }
    // YouTube/Vimeo embeds
    const isYouTube = /(?:youtube\.com\/watch\?v=|youtu\.be\/)/i.test(videoUrl)
    const isVimeo = /(?:vimeo\.com\/|player\.vimeo\.com\/video\/)/i.test(videoUrl)
    let embedUrl = videoUrl
    if (isYouTube) {
      try {
        const u = new URL(videoUrl)
        const vid = u.hostname.includes('youtu.be') ? u.pathname.replace('/', '') : (u.searchParams.get('v') || '')
        if (vid) embedUrl = `https://www.youtube.com/embed/${vid}`
      } catch {}
    } else if (isVimeo) {
      try {
        if (!/player\.vimeo\.com\/video\//i.test(videoUrl)) {
          const m = videoUrl.match(/vimeo\.com\/(\d+)/i)
          if (m && m[1]) embedUrl = `https://player.vimeo.com/video/${m[1]}`
        }
      } catch {}
    }
    if (Platform.OS === 'web') {
      return (
        <Box pointerEvents="none" className="overflow-hidden rounded-xl border border-border-200" style={{ height: 180 }}>
          {/* eslint-disable-next-line react/no-unknown-property */}
          <iframe src={embedUrl} style={{ width: '100%', height: '100%', border: '0' }} allow="autoplay; fullscreen; picture-in-picture" />
        </Box>
      )
    }
    return (
      <Box className="overflow-hidden rounded-xl border border-border-200" style={{ height: 180 }}>
        <WebView source={{ uri: embedUrl }} allowsInlineMediaPlayback javaScriptEnabled />
      </Box>
    )
  }


  const serverWorkout = fallbackQ.data?.practiceInstance || data?.todaysWorkouts?.find((w: any) => w.id_ === workoutId)

  const [workout, setWorkout] = useState<any | null>(null)

  // Sync local workout state with server data
  useEffect(() => {
    if (serverWorkout) {
      console.log('Syncing workout from server:', serverWorkout.id_)
      setWorkout(JSON.parse(JSON.stringify(serverWorkout)))
    }
  }, [serverWorkout])

  // Refetch workout data when component mounts to ensure fresh data
  useEffect(() => {
    if (workoutId && fallbackQ.refetch) {
      console.log('Refetching workout on mount:', workoutId)
      // Use a small delay to ensure GraphQL mutations have propagated
      const timer = setTimeout(() => {
        fallbackQ.refetch().catch((err) => {
          console.log('Refetch error (non-fatal):', err.message)
        })
      }, 100)
      return () => clearTimeout(timer)
    }
  }, [workoutId])

  const [elapsed, setElapsed] = useState(0)
  const [timerActive, setTimerActive] = useState(false)
  useEffect(() => { if (!timerActive) return; const t = setInterval(() => setElapsed((e) => e + 1), 1000); return () => clearInterval(t) }, [timerActive])
  const toggleTimer = () => setTimerActive((t) => !t)
  const startTimerIfIdle = () => { if (!timerActive) setTimerActive(true) }
  const fmtMinSec = (s: number) => `${String(Math.floor(s/60)).padStart(2,'0')}:${String(s%60).padStart(2,'0')}`

  // Pause timer on navigation away and save workout state
  useEffect(() => {
    return () => {
      // Component unmounting, pause the timer and save state
      setTimerActive(false)
      // Note: workout state is already persisted via individual set mutations
      // The elapsed time and timer state are ephemeral by design
    }
  }, [])

  // Auto-save workout duration periodically (every 10 seconds while timer active)
  useEffect(() => {
    if (!timerActive || !workoutId) return

    const saveInterval = setInterval(async () => {
      // Update workout duration in the background
      // Note: The practice instance stores duration, we could add a mutation to update it
      // For now, the duration is calculated client-side and saved on completion
      console.log('Auto-save: workout duration:', elapsed)
    }, 10000)

    return () => clearInterval(saveInterval)
  }, [timerActive, elapsed, workoutId])

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

  const openRestTimer = (pIdx: number, mIdx: number, sIdx: number, initial: number) => {
    console.log('openRestTimer called:', { pIdx, mIdx, sIdx, initial })
    setRestCtx({ pIdx, mIdx, sIdx })
    setRestSeconds(Math.max(0, initial || 60))
    setRestOpen(true)
    console.log('restOpen set to true')
  }

  const closeRestTimer = async () => {
    console.log('closeRestTimer called, restCtx:', restCtx)
    setRestOpen(false)

    if (!restCtx) {
      console.log('No restCtx, skipping set completion')
      return
    }

    const setId = workout?.prescriptions?.[restCtx.pIdx]?.movements?.[restCtx.mIdx]?.sets?.[restCtx.sIdx]?.id_
    console.log('Completing set:', setId)

    // Mark complete locally first
    markSetComplete(restCtx.pIdx, restCtx.mIdx, restCtx.sIdx)

    if (setId) {
      try {
        await completeSetInstance({ variables: { id: setId } })
        console.log('Set completed and saved:', setId)
        // Don't refetch immediately - it causes cache issues
        // The serverWorkout will sync on next render via useEffect
      } catch (e) {
        console.error('Failed to complete set:', e)
      }
    }

    // Clear rest context
    setRestCtx(null)
  }

  const onCompleteWorkout = async () => {
    try {
      await completeWorkoutMutation({ variables: { id: workoutId } })
      // Refetch home tasks and workouts, then navigate home with reload flag
      await apollo.refetchQueries({ include: [QUERY_TODAYS_SCHEDULABLES, QUERY_TODAYS_WORKOUTS, QUERY_MY_UPCOMING_PRACTICES] })
      router.replace('/journal?reload=1')
    } catch {}
  }

  if ((loading || fallbackQ.loading) && !workout) {
    return (
      <SafeAreaView className="h-full w-full">
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
      <SafeAreaView className="h-full w-full">
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

  const MovementFrozen = ({ m, pIdx, mIdx }: { m: any; pIdx: number; mIdx: number }) => {
    // Sort sets by position to maintain correct order
    const sortedSets = useMemo(() => {
      const sets = Array.isArray(m.sets) ? m.sets : []
      return [...sets].sort((a, b) => {
        const posA = typeof a?.position === 'number' ? a.position : 999
        const posB = typeof b?.position === 'number' ? b.position : 999
        return posA - posB
      })
    }, [m.sets])

    // Calculate target sets/reps for display
    const setsCount = sortedSets.length
    const firstSet = sortedSets.length > 0 ? sortedSets[0] : null
    const targetReps = firstSet?.reps || 10
    const targetDisplay = `${setsCount} sets × ${targetReps} reps`
    // Get the weight unit from the first set
    const weightUnit = firstSet?.loadUnit || 'lbs'

    return (
      <Box
        className="rounded-lg bg-white dark:bg-background-100"
        style={{
          shadowColor: '#000',
          shadowOffset: { width: 0, height: 1 },
          shadowOpacity: 0.1,
          shadowRadius: 2,
          elevation: 2,
        }}
      >
        <VStack className="p-4">
          {/* Exercise name and target sets/reps */}
          <VStack className="mb-4">
            <Text className="text-lg font-semibold text-typography-900 dark:text-white mb-1">
              {m.name}
            </Text>
            <Text className="text-sm text-typography-500 dark:text-typography-400">
              {targetDisplay}
            </Text>
          </VStack>
        {/* Collapsible video */}
        <Pressable onPress={() => toggleVideoFor(`${pIdx}-${mIdx}`)} className="flex-row items-center justify-between px-3 py-2 rounded-md border border-border-200 bg-background-0">
          <Text className="font-semibold text-typography-900 dark:text-white">Video</Text>
          <Text className="text-typography-600">{videoOpenByKey[`${pIdx}-${mIdx}`] ? '−' : '+'}</Text>
        </Pressable>
        {videoOpenByKey[`${pIdx}-${mIdx}`] ? (() => {
          // Prefer instance-level video first, else nested movement refs
          const rawUrl = (m?.videoUrl || m?.movement?.shortVideoUrl || m?.movement?.longVideoUrl || '') as string
          return <VideoPreview url={rawUrl} />
        })() : null}
        {/* Collapsible description directly under video, like in workout-create */}
        {(m.description || m?.movement?.description || m?.movement?.movement?.description) ? (
          <>
            <Box className="h-2" />
            <Pressable onPress={() => toggleDescFor(`${pIdx}-${mIdx}`)} className="flex-row items-center justify-between px-3 py-2 rounded-md border border-border-200 bg-background-0">
              <Text className="font-semibold text-typography-900 dark:text-white">Description</Text>
              <Text className="text-typography-600">{descOpenByKey[`${pIdx}-${mIdx}`] ? '−' : '+'}</Text>
            </Pressable>
            {descOpenByKey[`${pIdx}-${mIdx}`] ? (
              <MovementDescription description={(m.description || m?.movement?.description || m?.movement?.movement?.description) as string} />
            ) : null}
          </>
        ) : null}
        <VStack className="mt-2">
          {(() => {
            const usesDuration = sortedSets.some((s: any) => typeof s?.duration === 'number' && s.duration > 0)
            return (
              <VStack className="flex-row px-2 py-3 mb-2">
                <Box className="w-10"><Text className="text-xs font-bold text-typography-500 uppercase">Set</Text></Box>
                <Box className="flex-1"><Text className="text-xs font-bold text-typography-500 uppercase">{usesDuration ? 'Time' : 'Reps'}</Text></Box>
                <Box className="flex-1"><Text className="text-xs font-bold text-typography-500 uppercase">Weight ({weightUnit})</Text></Box>
                <Box className="flex-1"><Text className="text-xs font-bold text-typography-500 uppercase text-center">Rest (s)</Text></Box>
                <Box className="w-10" />
              </VStack>
            )
          })()}
          {sortedSets.map((s: any, i: number) => {
            const unit = s.loadUnit || 'lbs'
            const weightDisplay = typeof s.loadValue === 'number' ? `${s.loadValue} ${unit}` : unit
            return (
              <VStack key={i} className="mb-2">
                <VStack className="flex-row items-center px-2 py-2 bg-background-0 dark:bg-background-50 rounded-lg">
                  <Box className="w-10 items-center">
                    <Text className="text-sm font-bold text-typography-600 dark:text-typography-400">
                      {i + 1}
                    </Text>
                  </Box>
                  {(() => {
                    const usesDuration = typeof s?.duration === 'number' && s.duration > 0
                    if (usesDuration) {
                      return (
                        <Box className="flex-1 px-2">
                          <Text className="text-base font-semibold text-typography-900 dark:text-white">{`${s.duration}s`}</Text>
                        </Box>
                      )
                    }
                    return (
                      <Box className="flex-1 px-2">
                        <Input
                          size="md"
                          isDisabled={!!s.complete}
                          className="bg-white dark:bg-background-100 border-border-300"
                        >
                          <InputField
                            keyboardType="numeric"
                            defaultValue={typeof s.reps === 'number' ? String(s.reps) : ''}
                            placeholder="0"
                            onChangeText={(v) => onChangeSetField(pIdx, mIdx, i, 'reps', v)}
                            onFocus={startTimerIfIdle}
                            className="text-center font-semibold"
                          />
                        </Input>
                      </Box>
                    )
                  })()}
                  <Box className="flex-1 px-2">
                    <Input
                      size="md"
                      isDisabled={!!s.complete}
                      className="bg-white dark:bg-background-100 border-border-300"
                    >
                      <InputField
                        keyboardType="numeric"
                        defaultValue={typeof s.loadValue === 'number' ? String(s.loadValue) : ''}
                        placeholder="0"
                        onChangeText={(v) => onChangeSetField(pIdx, mIdx, i, 'loadValue', v)}
                        onFocus={startTimerIfIdle}
                        className="text-center font-semibold"
                      />
                    </Input>
                  </Box>
                  <Box className="flex-1 px-2">
                    <Input
                      size="md"
                      isDisabled={!!s.complete}
                      className="bg-white dark:bg-background-100 border-border-300"
                    >
                      <InputField
                        keyboardType="numeric"
                        defaultValue={typeof s.restDuration === 'number' ? String(s.restDuration) : (typeof m.restDuration === 'number' ? String(m.restDuration) : '')}
                        placeholder="60"
                        onChangeText={(v) => {
                          if (!workout) return
                          startTimerIfIdle()
                          // local update first
                          setWorkout((prev: any) => {
                            const copy = JSON.parse(JSON.stringify(prev))
                            const set = copy.prescriptions?.[pIdx]?.movements?.[mIdx]?.sets?.[i]
                            if (set) {
                              const num = parseFloat(v)
                              set.restDuration = Number.isFinite(num) ? num : undefined
                            }
                            return copy
                          })
                          // persist
                          const setId = workout?.prescriptions?.[pIdx]?.movements?.[mIdx]?.sets?.[i]?.id_
                          if (setId) {
                            const num = parseFloat(v)
                            const input: any = { restDuration: Number.isFinite(num) ? num : null }
                            try { updateSetInstance({ variables: { id: setId, input } }) } catch {}
                          }
                        }}
                        onFocus={startTimerIfIdle}
                        className="text-center font-semibold"
                      />
                    </Input>
                  </Box>
                  <Box className="w-10 items-center">
                    <Pressable
                      className={`w-10 h-10 rounded items-center justify-center ${
                        s.complete
                          ? 'bg-green-100 dark:bg-green-900/30'
                          : 'bg-background-100 dark:bg-background-200'
                      }`}
                      onPress={async () => {
                        const secs = (typeof s.restDuration === 'number' && s.restDuration > 0) ? s.restDuration : (typeof m.restDuration === 'number' ? m.restDuration : 60)
                        openRestTimer(pIdx, mIdx, i, secs)
                        startTimerIfIdle()
                      }}
                    >
                      <Text className={`text-xl ${s.complete ? 'text-green-600 dark:text-green-400' : 'text-typography-400 dark:text-typography-500'}`}>
                        ✓
                      </Text>
                    </Pressable>
                  </Box>
                </VStack>
              </VStack>
            )
          })}
        </VStack>
        {/* Removed duplicate always-on description block to keep only collapsible */}
        <Box className="h-2" />
        <Pressable className="self-start px-4 py-2 rounded-lg bg-green-600" onPress={() => addSetToMovement(pIdx, mIdx)}>
          <Text className="text-white text-sm font-semibold">+ Add Set</Text>
        </Pressable>
      </VStack>
      </Box>
    )
  }

  const BlockFrozen = ({ p, idx }: { p: any; idx: number }) => {
    // Sort movements by position to maintain correct order
    const sortedMovements = useMemo(() => {
      const movements = Array.isArray(p.movements) ? p.movements : []
      return [...movements].sort((a, b) => {
        const posA = typeof a?.position === 'number' ? a.position : 999
        const posB = typeof b?.position === 'number' ? b.position : 999
        return posA - posB
      })
    }, [p.movements])

    return (
      <VStack>
        <Text className="text-xl font-bold text-typography-900 dark:text-white uppercase mb-4">
          {p?.name || String(p?.block || '').toUpperCase() || `Block ${idx + 1}`}
        </Text>
        {sortedMovements.map((m: any, i: number) => (
          <VStack key={m.id_ || i}>
            <MovementFrozen m={m} pIdx={idx} mIdx={i} />
            <Box className="h-6" />
          </VStack>
        ))}
      </VStack>
    )
  }

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title="Workout" showBackButton onBackPress={() => { try { router.replace('/journal') } catch { router.back() } }} />
        {/* Delete moved to bottom with confirm modal */}

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
                  {workout?.description ? (
                    <>
                      <Box className="h-1" />
                      <Pressable onPress={() => setNotesOpen((o) => !o)} className="flex-row items-center justify-between px-3 py-2 rounded-md border border-border-200 bg-background-0">
                        <Text className="font-semibold text-typography-900 dark:text-white">Description</Text>
                        <Text className="text-typography-600">{notesOpen ? '−' : '+'}</Text>
                      </Pressable>
                      {notesOpen ? (
                        <Box className="mt-2 p-3 rounded border border-border-200 bg-background-50">
                          <Markdown>{workout.description}</Markdown>
                        </Box>
                      ) : null}
                    </>
                  ) : (
                    <Text className="text-sm text-typography-900">—</Text>
                  )}
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
              {(() => {
                const prescriptions = Array.isArray(workout?.prescriptions) ? workout.prescriptions : []
                // Sort prescriptions by position to maintain correct block order
                const sortedPrescriptions = [...prescriptions].sort((a, b) => {
                  const posA = typeof a?.position === 'number' ? a.position : 999
                  const posB = typeof b?.position === 'number' ? b.position : 999
                  return posA - posB
                })
                return sortedPrescriptions.map((p: any, idx: number) => (
                  <VStack key={p.id_ || idx}>
                    <BlockFrozen p={p} idx={idx} />
                    <Box className="h-4" />
                  </VStack>
                ))
              })()}
            </VStack>

            {/* Complete / Delete */}
            <VStack className="px-6 pb-20">
              <Pressable className="px-4 py-3 rounded-xl border border-border-200 bg-indigo-50" onPress={onCompleteWorkout}>
                <Text className="text-indigo-700 text-center font-semibold">Complete Workout</Text>
              </Pressable>
              {!enrollmentId ? (
                <>
                  <Box className="h-3" />
                  <Pressable className="px-4 py-3 rounded-xl border border-red-200 bg-red-50" onPress={() => setDeleteConfirmOpen(true)}>
                    <Text className="text-red-700 text-center font-semibold">Delete Workout</Text>
                  </Pressable>
                </>
              ) : null}
            </VStack>
          </VStack>
        </ScrollView>

        {/* Rest Timer Modal */}
        <RestTimerModal
          visible={restOpen}
          initialSeconds={restSeconds}
          onComplete={closeRestTimer}
          onSkip={closeRestTimer}
        />
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

      {/* Confirm Delete modal */}
      <Modal visible={!!deleteConfirmOpen} transparent animationType="fade" onRequestClose={() => setDeleteConfirmOpen(false)}>
        <Pressable onPress={() => setDeleteConfirmOpen(false)} style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.4)', justifyContent: 'flex-end' }}>
          <View style={{ backgroundColor: '#fff', padding: 16, borderTopLeftRadius: 12, borderTopRightRadius: 12 }}>
            <Text className="text-typography-900" style={{ fontWeight: '700', fontSize: 16, marginBottom: 8 }}>Delete Workout</Text>
            <Text className="text-typography-700" style={{ marginBottom: 12 }}>Are you sure you want to delete this workout?</Text>
            <VStack className="flex-row items-center justify-end" style={{ gap: 12 }}>
              <Pressable onPress={() => setDeleteConfirmOpen(false)} className="px-4 py-2 rounded-lg border border-border-200 bg-background-50">
                <Text className="text-typography-900">Cancel</Text>
              </Pressable>
              <Pressable onPress={async () => { try { await deletePracticeInstance({ variables: { id: workoutId } }); setDeleteConfirmOpen(false); await apollo.refetchQueries({ include: [QUERY_TODAYS_SCHEDULABLES, QUERY_TODAYS_WORKOUTS, QUERY_MY_UPCOMING_PRACTICES] }); router.replace('/journal?reload=1') } catch {} }} className="px-4 py-2 rounded-lg border border-red-200 bg-red-50">
                <Text className="text-red-700 font-semibold">Delete</Text>
              </Pressable>
            </VStack>
          </View>
        </Pressable>
      </Modal>

    </SafeAreaView>
  )
}
