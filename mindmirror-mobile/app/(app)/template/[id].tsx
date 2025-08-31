import React from 'react'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { AppBar } from '@/components/common/AppBar'
import { VStack } from '@/components/ui/vstack'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { ScrollView } from '@/components/ui/scroll-view'
import { useLocalSearchParams, useRouter } from 'expo-router'
import { usePracticeTemplate, useMovementTemplate, useSearchMovements } from '@/services/api/practices'
import { Pressable } from '@/components/ui/pressable'
import { View } from 'react-native'
import { Button, ButtonText } from '@/components/ui/button'
import { HStack } from '@/components/ui/hstack'
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
    <Box className="overflow-hidden rounded-xl border border-border-200" style={{ height: 200 }}>
      <WebView source={{ uri: src }} allowsInlineMediaPlayback javaScriptEnabled />
    </Box>
  )
}

function FallbackYouTube({ name, primaryUrl }: { name: string; primaryUrl?: string | null }) {
  const search = useSearchMovements(name, 1)
  const url = React.useMemo(() => {
    return primaryUrl || search.data?.searchMovements?.[0]?.shortVideoUrl || null
  }, [primaryUrl, search.data?.searchMovements])
  if (!url) return null
  return <YouTubeEmbed url={url} />
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

function computeRepsRange(sets?: any[] | null): { min?: number; max?: number } {
  if (!Array.isArray(sets) || sets.length === 0) return {}
  const reps = sets.map((s) => (typeof s.reps === 'number' ? s.reps : undefined)).filter((v) => typeof v === 'number') as number[]
  if (reps.length === 0) return {}
  return { min: Math.min(...reps), max: Math.max(...reps) }
}

function buildSetSummary(m: any): string {
  const setsCount = m.prescribed_sets || (m.sets?.length || 0)
  const { min, max } = computeRepsRange(m.sets)
  const rest = typeof m.rest_duration === 'number' ? `${m.rest_duration}s` : undefined
  const parts: string[] = []
  if (setsCount) parts.push(`${setsCount} sets`)
  if (typeof min === 'number' && typeof max === 'number') {
    parts.push(`${min === max ? `${min}` : `${min}–${max}`} reps`)
  }
  if (rest) parts.push(rest)
  return parts.join(' · ')
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
    <VStack space="xs">
      <VStack className="rounded-xl border border-border-200 divide-y divide-border-200 bg-background-0">
        {rows.map((r, i) => (
          <VStack key={`${r.label}-${i}`} className="flex-row items-start p-3">
            <Box className="w-40"><Text className="text-typography-700 text-sm font-semibold">{r.label}</Text></Box>
            <Box className="flex-1"><Text className="text-typography-900 text-sm dark:text-white">{r.value}</Text></Box>
          </VStack>
        ))}
      </VStack>
    </VStack>
  )
}

function buildSignature(m: any): string {
  const setsCount = m.prescribed_sets || (m.sets?.length || 0)
  const repsList = Array.isArray(m.sets) ? m.sets.map((s: any) => (typeof s.reps === 'number' ? s.reps : undefined)).filter((n: any) => typeof n === 'number') : []
  const reps = repsList.length ? Math.min(...repsList) : undefined
  const first = Array.isArray(m.sets) && m.sets.length ? m.sets[0] : undefined
  const load = first ? formatLoad(first.load_value, first.load_unit) : undefined
  const rest = typeof (first?.rest_duration) === 'number' ? `${first.rest_duration}s` : (typeof m.rest_duration === 'number' ? `${m.rest_duration}s` : undefined)
  const parts: string[] = []
  if (setsCount && reps) parts.push(`${setsCount} x ${reps}`)
  else if (setsCount) parts.push(`${setsCount} sets`)
  if (load && load !== '—') parts.push(load)
  if (rest) parts.push(rest)
  return parts.join(' · ')
}

function buildDisplayRows(m: any): any[] {
  const base: any[] = Array.isArray(m?.sets) ? m.sets : []
  const prescribed: number = typeof m?.prescribed_sets === 'number' ? m.prescribed_sets : base.length
  if (!prescribed) return base
  if (base.length >= prescribed) return base
  const rows = [...base]
  const seed = base[base.length - 1] || { reps: undefined, duration: undefined, rest_duration: m?.rest_duration, load_value: undefined, load_unit: undefined }
  while (rows.length < prescribed) {
    rows.push({ ...seed, __synthetic: true })
  }
  return rows.map((r, i) => ({ ...r, __idx: i }))
}

export default function TemplateDetailsScreen() {
  const { id, returnTo } = useLocalSearchParams<{ id: string, returnTo?: string }>()
  const router = useRouter()
  const { data, loading } = usePracticeTemplate(id || '')
  const t = data?.practiceTemplate
  const [movementModalId, setMovementModalId] = React.useState<string | null>(null)
  const movementQ = useMovementTemplate(movementModalId || '')
  const mt = movementQ.data?.movementTemplate
  // Fallback lookup if federation fails to supply movement
  const fallbackSearch = useSearchMovements(mt?.name || '', 1)
  const fallbackMovement = React.useMemo(() => mt?.movement || fallbackSearch.data?.searchMovements?.[0], [mt?.movement, fallbackSearch.data?.searchMovements])
  const bestVideoUrl = mt?.movement?.shortVideoUrl || mt?.video_url || fallbackMovement?.shortVideoUrl || null

  const [videoOpenById, setVideoOpenById] = React.useState<Record<string, boolean>>({})
  const [setsOpenById, setSetsOpenById] = React.useState<Record<string, boolean>>({})
  const toggleVideo = (key: string) => setVideoOpenById((prev) => ({ ...prev, [key]: !prev[key] }))
  const toggleSets = (key: string) => setSetsOpenById((prev) => ({ ...prev, [key]: !prev[key] }))

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title={t?.title || 'Template'} showBackButton onBackPress={() => {
          if (returnTo) {
            try { router.replace(returnTo) } catch { router.back() }
          } else {
            try { router.back() } catch { router.replace('/programs') }
          }
        }} />
        <ScrollView className="flex-1">
          <VStack className="w-full max-w-screen-md mx-auto px-6 py-6" space="lg">
            {loading ? (
              <Text className="text-typography-600">Loading…</Text>
            ) : !t ? (
              <Text className="text-typography-600">Not found</Text>
            ) : (
              <>
                <VStack space="xs">
                  <Text className="text-2xl font-bold text-typography-900 dark:text-white">{t.title}</Text>
                  {t.description ? <Text className="text-typography-600 dark:text-gray-300">{t.description}</Text> : null}
                </VStack>

                <VStack space="md">
                  <Text className="text-lg font-semibold text-typography-900 dark:text-white">Blocks</Text>
                  {(t.prescriptions || []).map((p: any, idx: number) => (
                    <VStack key={p.id_ || idx} space="sm">
                      <Text className="text-sm font-semibold text-typography-900 dark:text-white">{p.name || String(p.block).toUpperCase()}</Text>
                      <Box className="h-2" />
                      {(p.movements || []).length === 0 ? (
                        <Text className="text-typography-600 dark:text-gray-300 text-center">
                          {(() => {
                            const b = String(p.block || '').toLowerCase()
                            if (b === 'warmup') return 'No warm-up movements'
                            if (b === 'workout') return 'No main workout movements'
                            if (b === 'cooldown') return 'No cooldown movements'
                            return 'No movements'
                          })()}
                        </Text>
                      ) : (
                        (p.movements || []).map((m: any, mi: number) => {
                          const preferredUrl = m.movement?.shortVideoUrl || m.video_url || null
                          const key = String(m.id_ || `${idx}_${mi}`)
                          const videoOpen = !!videoOpenById[key]
                          const setsOpen = !!setsOpenById[key]
                          return (
                            <Box key={m.id_ || mi} className="p-4 rounded-xl border border-border-200 bg-background-50 dark:bg-background-100">
                              <VStack space="sm">
                                <VStack className="flex-row items-center justify-between">
                                  <Pressable onPress={() => setMovementModalId(m.id_)}>
                                    <Text className="font-semibold text-typography-900 dark:text-white">{m.name}</Text>
                                  </Pressable>
                                  <Text className="text-typography-600 dark:text-gray-300">{(() => { const sig = buildSignature(m); return sig || buildSetSummary(m) })()}</Text>
                                </VStack>

                                {/* Signature chip */}
                                <HStack className="flex-row flex-wrap gap-2">
                                  <Box className="px-3 py-1 rounded-full border border-border-200 bg-background-0">
                                    <Text className="text-sm text-typography-900">{buildSignature(m)}</Text>
                                  </Box>
                                </HStack>

                                {/* Collapsible Video */}
                                <Pressable onPress={() => toggleVideo(key)} className="flex-row items-center justify-between px-3 py-2 rounded-md border border-border-200 bg-background-0">
                                  <Text className="font-semibold text-typography-900">Video</Text>
                                  <Text className="text-typography-600">{videoOpen ? '−' : '+'}</Text>
                                </Pressable>
                                {videoOpen ? (
                                  preferredUrl ? (
                                    <YouTubeEmbed url={preferredUrl} />
                                  ) : (
                                    <Box className="overflow-hidden rounded-xl border border-border-200 bg-background-50" style={{ height: 160, alignItems: 'center', justifyContent: 'center' }}>
                                      <Text className="text-typography-600">🎥 Video placeholder</Text>
                                    </Box>
                                  )
                                ) : null}

                                {/* Collapsible Sets */}
                                <Pressable onPress={() => toggleSets(key)} className="flex-row items-center justify-between px-3 py-2 rounded-md border border-border-200 bg-background-0">
                                  <Text className="font-semibold text-typography-900">Sets</Text>
                                  <Text className="text-typography-600">{setsOpen ? '−' : '+'}</Text>
                                </Pressable>
                                {setsOpen ? (
                                  <VStack>
                                    <VStack className="flex-row px-3 py-2 rounded bg-background-100 border border-border-200">
                                      <Box className="w-10"><Text className="text-xs font-semibold text-typography-600">#</Text></Box>
                                      <Box className="flex-1"><Text className="text-xs font-semibold text-typography-600">Reps/Dur</Text></Box>
                                      <Box className="flex-1"><Text className="text-xs font-semibold text-typography-600">Load</Text></Box>
                                      <Box className="flex-1"><Text className="text-xs font-semibold text-typography-600">Rest</Text></Box>
                                    </VStack>
                                    {buildDisplayRows(m).map((s: any, si: number) => (
                                      <VStack key={si}>
                                        <VStack className="flex-row items-center px-3 py-2 bg-white dark:bg-background-50">
                                          <Box className="w-10"><Text className="text-typography-700">{si + 1}</Text></Box>
                                          <Box className="flex-1"><Text className="text-typography-900">{s.reps ?? s.duration ?? '—'}</Text></Box>
                                          <Box className="flex-1"><Text className="text-typography-900">{formatLoad(s.load_value, s.load_unit)}</Text></Box>
                                          <Box className="flex-1"><Text className="text-typography-900">{s.rest_duration ? `${s.rest_duration}s` : (typeof m?.rest_duration === 'number' ? `${m.rest_duration}s` : '—')}</Text></Box>
                                        </VStack>
                                        <Box className="h-px bg-border-200" />
                                      </VStack>
                                    ))}
                                  </VStack>
                                ) : null}


                              </VStack>
                            </Box>
                          )
                        })
                      )}
                    </VStack>
                  ))}
                </VStack>
              </>
            )}
          </VStack>
        </ScrollView>
      </VStack>

      {movementModalId ? (
        <View style={{ position: 'absolute', left: 0, right: 0, top: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.45)', justifyContent: 'center', alignItems: 'center', padding: 24 }}>
          <Box className="w-full max-w-md p-5 rounded-2xl bg-background-0 border border-border-200 dark:border-border-700">
            <VStack space="md">
              <Text className="text-xl font-bold text-typography-900 dark:text-white">{mt?.name || 'Exercise'}</Text>
              {mt?.description ? <Text className="text-typography-700 dark:text-gray-300">{mt.description}</Text> : null}
              {/* Signature chip above Details */}
              <HStack className="flex-row flex-wrap gap-2">
                <Box className="px-3 py-1 rounded-full border border-border-200 bg-background-50">
                  <Text className="text-sm text-typography-900">{buildSignature(mt || {})}</Text>
                </Box>
              </HStack>

              {/* Details section with video area and table (fallback-aware) */}
              <VStack space="sm">
                <Text className="text-lg font-semibold text-typography-900 dark:text-white">Details</Text>
                {/* Collapsible Video */}
                <Box className="overflow-hidden rounded-xl border border-border-200 bg-background-50" style={{ height: 200, alignItems: 'center', justifyContent: 'center' }}>
                  {bestVideoUrl ? <YouTubeEmbed url={bestVideoUrl} /> : <Text className="text-typography-600">🎥 Video placeholder</Text>}
                </Box>
                {/* Details table */}
                <DetailsTable movement={fallbackMovement} />
              </VStack>

              <HStack className="justify-end space-x-3">
                <Button className="bg-gray-600" onPress={() => setMovementModalId(null)}>
                  <ButtonText>Dismiss</ButtonText>
                </Button>
                <Button className="bg-primary-600" onPress={() => { 
                  const prefetch = encodeURIComponent(JSON.stringify({
                    name: mt?.name,
                    description: mt?.description,
                    movement: mt?.movement || undefined,
                    sets: mt?.sets,
                    metric_value: mt?.metric_value,
                    metric_unit: mt?.metric_unit,
                    prescribed_sets: mt?.prescribed_sets,
                    rest_duration: mt?.rest_duration,
                    video_url: (mt?.movement?.shortVideoUrl || mt?.video_url) || undefined,
                  }))
                  setMovementModalId(null); 
                  // Pass prefetch data to avoid re-fetch on details
                  router.push(`/(app)/exercise/${movementModalId}?prefetch=${prefetch}&returnTo=${encodeURIComponent(`/template/${t?.id_}`)}`) 
                }}>
                  <ButtonText>More info</ButtonText>
                </Button>
              </HStack>
            </VStack>
          </Box>
        </View>
      ) : null}
    </SafeAreaView>
  )
} 