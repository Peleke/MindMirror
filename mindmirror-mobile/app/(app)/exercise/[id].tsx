import React from 'react'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { AppBar } from '@/components/common/AppBar'
import { VStack } from '@/components/ui/vstack'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { ScrollView } from '@/components/ui/scroll-view'
import { useLocalSearchParams, useRouter } from 'expo-router'
import { useMovementTemplate, useSearchMovements } from '@/services/api/practices'
import { WebView } from 'react-native-webview'

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
    <Box className="overflow-hidden rounded-xl border border-border-200" style={{ height: 240 }}>
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
    { label: 'Tags', value: Array.isArray(movement.tags) && movement.tags.length ? movement.tags.join(', ') : null },
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

function DetailsSection({ movement, videoUrl, summary }: { movement?: any; videoUrl?: string | null; summary?: string }) {
  const url = videoUrl || movement?.shortVideoUrl || null
  return (
    <VStack space="sm">
      <Text className="text-lg font-semibold text-typography-900 dark:text-white">Details</Text>
      <Box className="overflow-hidden rounded-xl border border-border-200 bg-background-50" style={{ height: 200, alignItems: 'center', justifyContent: 'center' }}>
        {url ? <YouTubeEmbed url={url} /> : <Text className="text-typography-600">🎥 Video placeholder</Text>}
      </Box>
      {summary ? <Text className="text-typography-700 dark:text-gray-300">{summary}</Text> : null}
      <DetailsTable movement={movement} />
    </VStack>
  )
}

function computeRepsRange(sets?: any[] | null): { min?: number; max?: number } {
  if (!Array.isArray(sets) || sets.length === 0) return {}
  const reps = sets.map((s) => (typeof s.reps === 'number' ? s.reps : undefined)).filter((v) => typeof v === 'number') as number[]
  if (reps.length === 0) return {}
  return { min: Math.min(...reps), max: Math.max(...reps) }
}

export default function ExerciseDetailsScreen() {
  const { id, returnTo, prefetch } = useLocalSearchParams<{ id: string, returnTo?: string, prefetch?: string }>()
  const router = useRouter()
  const { data, loading } = useMovementTemplate(id || '')
  const mtRaw = data?.movementTemplate
  const pre = React.useMemo(() => {
    try { return prefetch ? JSON.parse(prefetch) : undefined } catch { return undefined }
  }, [prefetch])
  const mt = pre ? {
    ...mtRaw,
    name: pre.name ?? mtRaw?.name,
    description: pre.description ?? mtRaw?.description,
    movement: pre.movement ?? mtRaw?.movement,
    sets: pre.sets ?? mtRaw?.sets,
    metric_value: pre.metric_value ?? mtRaw?.metric_value,
    metric_unit: pre.metric_unit ?? mtRaw?.metric_unit,
    prescribed_sets: pre.prescribed_sets ?? mtRaw?.prescribed_sets,
    rest_duration: pre.rest_duration ?? mtRaw?.rest_duration,
    video_url: pre.video_url ?? (mtRaw?.movement?.shortVideoUrl || mtRaw?.video_url),
  } : mtRaw

  // Fallback movement lookup by name if federation/movement missing
  const movementName = mt?.name || ''
  const search = useSearchMovements(movementName, 1)
  const fallbackMovement = React.useMemo(() => mt?.movement || search.data?.searchMovements?.[0], [mt?.movement, search.data?.searchMovements])
  const bestVideoUrl = mt?.movement?.shortVideoUrl || mt?.video_url || fallbackMovement?.shortVideoUrl || null

  const setChips = React.useMemo(() => {
    if (!Array.isArray(mt?.sets) || mt!.sets.length === 0) return []
    return mt!.sets.map((s: any, i: number) => {
      const which = (typeof s.reps === 'number' ? `${s.reps} reps` : (typeof s.duration === 'number' ? `${s.duration}s` : '—'))
      const load = formatLoad(s.load_value, s.load_unit)
      const loadPart = load && load !== '—' ? ` with ${load}` : ''
      const restPart = typeof s.rest_duration === 'number' ? ` and ${s.rest_duration}s rest` : ''
      return { key: s.id_ || i, label: `${which}${loadPart}${restPart}` }
    })
  }, [mt?.sets])

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title={mt?.name || 'Exercise'} showBackButton onBackPress={() => {
          if (returnTo) {
            try { router.replace(returnTo) } catch { router.back() }
          } else {
            try { router.back() } catch { router.replace('/programs') }
          }
        }} />
        <ScrollView className="flex-1">
          <VStack className="w-full max-w-screen-md mx-auto px-6 py-6" space="lg">
            {loading && !mt ? (
              <Text className="text-typography-600">Loading…</Text>
            ) : !mt ? (
              <Text className="text-typography-600">Not found</Text>
            ) : (
              <>
                <VStack space="sm">
                  <Text className="text-2xl font-bold text-typography-900 dark:text-white">{mt.name}</Text>
                  {mt.description ? <Text className="text-typography-600 dark:text-gray-300">{mt.description}</Text> : null}
                </VStack>

                {/* Set prescription chips */}
                {(Array.isArray(mt.sets) && mt.sets.length > 0) ? (
                  <VStack space="xs">
                    <Text className="text-lg font-semibold text-typography-900 dark:text-white">Set prescription</Text>
                    <VStack className="flex-row flex-wrap gap-2">
                      {setChips.map((chip: { key: string | number; label: string }) => (
                        <Box key={chip.key} className="px-3 py-1 rounded-full border border-border-200 bg-background-50">
                          <Text className="text-sm text-typography-900">{chip.label}</Text>
                        </Box>
                      ))}
                    </VStack>
                  </VStack>
                ) : null}

                {/* Details section under everything else */}
                <DetailsSection movement={fallbackMovement} videoUrl={bestVideoUrl} summary={(() => {
                  // Build a compact summary from first/last set if sets exist
                  if (!Array.isArray(mt.sets) || mt.sets.length === 0) return ''
                  const reps = mt.sets.map((s: any) => s.reps).filter((n: any) => typeof n === 'number')
                  const min = Math.min(...reps)
                  const max = Math.max(...reps)
                  const rest = mt.sets[0]?.rest_duration
                  const parts: string[] = []
                  parts.push(`${mt.sets.length} sets`)
                  if (reps.length) parts.push(`${min === max ? `${min}` : `${min}–${max}`} reps`)
                  if (typeof rest === 'number') parts.push(`${rest}s`)
                  return parts.join(' · ')
                })()} />
              </>
            )}
          </VStack>
        </ScrollView>
      </VStack>
    </SafeAreaView>
  )
} 