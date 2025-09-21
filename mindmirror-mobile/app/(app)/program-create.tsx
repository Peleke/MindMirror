import React, { useMemo, useState } from 'react'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { AppBar } from '@/components/common/AppBar'
import { VStack } from '@/components/ui/vstack'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { Input, InputField } from '@/components/ui/input'
import { Pressable } from '@/components/ui/pressable'
import { ScrollView } from '@/components/ui/scroll-view'
import { usePracticeTemplates, useCreateProgram, useLazySearchPracticeTemplates, useHabitsProgramTemplates } from '@/services/api/practices'
import { QUERY_PROGRAM_TEMPLATES } from '@/services/api/practices'
import { useRouter, useLocalSearchParams } from 'expo-router'
import { TextInput, View, Modal, KeyboardAvoidingView, Platform, FlatList, Pressable as RNPressable, ScrollView as RNSV } from 'react-native'
import { useApolloClient } from '@apollo/client'
import Markdown from 'react-native-markdown-display'

export default function ProgramCreateScreen() {
  const router = useRouter()
  const params = useLocalSearchParams<{ addTemplateId?: string }>()
  const apollo = useApolloClient()
  const { data, loading } = usePracticeTemplates()
  const templates = (data?.practiceTemplates || []) as Array<{ id_: string, title: string, description?: string }>
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [level, setLevel] = useState('')
  const [links, setLinks] = useState<Array<{ practice_template_id: string; sequence_order: number; interval_days_after: number }>>([])
  const [selectedHabitsProgram, setSelectedHabitsProgram] = useState<{id: string, title: string, description?: string} | null>(null)
  const [createProgram, { loading: saving }] = useCreateProgram()
  
  // Habits program templates
  const { data: habitsData, loading: habitsLoading } = useHabitsProgramTemplates()
  const habitsPrograms = (habitsData?.programTemplates || []) as Array<{ id: string, title: string, description?: string, subtitle?: string }>

  // Template search modal state
  const [searchOpen, setSearchOpen] = useState(false)
  const [search, setSearch] = useState('')
  const [runSearch, { data: searchData, loading: searching }] = useLazySearchPracticeTemplates()
  const serverResults = (searchData?.searchPracticeTemplates || []) as Array<{ id_: string, title: string, description?: string }>

  // Habits program search modal state
  const [habitsSearchOpen, setHabitsSearchOpen] = useState(false)
  const [habitsSearch, setHabitsSearch] = useState('')
  const [pairingCollapsed, setPairingCollapsed] = useState(true)

  // Debounced server search when term length >= 2
  React.useEffect(() => {
    if (!searchOpen) return
    const term = (search || '').trim()
    const h = setTimeout(() => {
      if (term.length >= 2) {
        runSearch({ variables: { term, limit: 25 } })
      }
    }, 250)
    return () => clearTimeout(h)
  }, [searchOpen, search])

  const filteredTemplates = useMemo(() => {
    const q = (search || '').trim().toLowerCase()
    if (!q) return templates
    if (q.length >= 2) {
      if ((serverResults?.length || 0) > 0 || searching) return serverResults
      return templates.filter(t => t.title.toLowerCase().includes(q))
    }
    return templates.filter(t => t.title.toLowerCase().includes(q))
  }, [search, serverResults, templates, searching])

  const filteredHabitsPrograms = useMemo(() => {
    const q = (habitsSearch || '').trim().toLowerCase()
    if (!q) return habitsPrograms
    return habitsPrograms.filter(p => 
      p.title.toLowerCase().includes(q) || 
      (p.description || '').toLowerCase().includes(q) ||
      (p.subtitle || '').toLowerCase().includes(q)
    )
  }, [habitsSearch, habitsPrograms])

  React.useEffect(() => {
    const tplId = params?.addTemplateId
    if (!tplId) return
    setLinks(prev => {
      if (prev.some(l => l.practice_template_id === tplId)) return prev
      return [...prev, { practice_template_id: tplId, sequence_order: prev.length, interval_days_after: 1 }]
    })
  }, [params?.addTemplateId])

  const addLink = (tplId: string) => {
    if (!tplId) return
    setLinks(prev => [...prev, { practice_template_id: tplId, sequence_order: prev.length, interval_days_after: 1 }])
  }
  const removeLink = (idx: number) => setLinks(prev => prev.filter((_, i) => i !== idx).map((l, i) => ({ ...l, sequence_order: i })))
  const updateInterval = (idx: number, v: string) => {
    const n = Math.max(0, parseInt(v || '0', 10) || 0)
    setLinks(prev => prev.map((l, i) => i === idx ? { ...l, interval_days_after: n } : l))
  }

  const onSave = async () => {
    if (!name || links.length === 0) return
    try {
      const input = {
        name,
        description: description || null,
        level: level || null,
        habitsProgramTemplateId: selectedHabitsProgram?.id || null,
        tags: [],
        practiceLinks: links.map(l => ({ practiceTemplateId: l.practice_template_id, sequenceOrder: l.sequence_order, intervalDaysAfter: l.interval_days_after })),
      }
      await createProgram({ variables: { input } })
      apollo.refetchQueries({ include: [QUERY_PROGRAM_TEMPLATES] })
      // Navigate to detail of the most recently created program by refetching list and using the first match by name
      try {
        const res = await apollo.query({ query: QUERY_PROGRAM_TEMPLATES, fetchPolicy: 'network-only' })
        const match = (res.data?.programs || []).find((p: any) => p.name === name)
        if (match?.id_) router.replace(`/(app)/program/${match.id_}`)
        else router.replace('/programs')
      } catch { router.replace('/programs') }
    } catch {}
  }

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title="Create Program" showBackButton onBackPress={() => router.back()} />
        <ScrollView className="flex-1">
          <VStack className="w-full max-w-screen-md mx-auto px-6 py-6" space="lg">
            <VStack space="sm">
              <Text className="text-2xl font-bold text-typography-900 dark:text-white">Program Details</Text>
              <Input className="bg-background-50 dark:bg-background-100"><InputField placeholder="Name" value={name} onChangeText={setName} /></Input>
              {/* Markdown-enabled description input with live preview */}
              <Text className="text-typography-900 font-semibold dark:text-white">Description</Text>
              <TextInput
                placeholder="Optional description (markdown supported)"
                value={description}
                onChangeText={setDescription}
                multiline
                numberOfLines={3}
                className="bg-background-50 dark:bg-background-100 text-typography-600 dark:text-gray-300"
                style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10, minHeight: 48, textAlignVertical: 'top' }}
              />
              {description.trim().length > 0 ? (
                <Box className="mt-2 mb-3 p-3 rounded-lg border border-border-200 bg-background-50 dark:bg-background-100" style={{ height: 140, zIndex: 10 }}>
                  <RNSV
                    nestedScrollEnabled
                    keyboardShouldPersistTaps="handled"
                    showsVerticalScrollIndicator
                    style={{ flex: 1 }}
                    contentContainerStyle={{ paddingBottom: 8 }}
                  >
                    <Markdown>{description}</Markdown>
                  </RNSV>
                </Box>
              ) : null}
              <Input className="bg-background-50 dark:bg-background-100"><InputField placeholder="Level (optional)" value={level} onChangeText={setLevel} /></Input>
            </VStack>
            
            {/* Habits Program Pairing */}
            <VStack space="sm">
              <Pressable 
                onPress={() => setPairingCollapsed(!pairingCollapsed)}
                className="flex-row items-center justify-between"
              >
                <Text className="text-lg font-semibold text-typography-900 dark:text-white">Pair with Lessons Program (Optional)</Text>
                <Text className="text-2xl text-typography-600 dark:text-gray-400">{pairingCollapsed ? '+' : '−'}</Text>
              </Pressable>
              
              {!pairingCollapsed && (
                <VStack space="sm">
                  <Text className="text-sm text-typography-600 dark:text-gray-400">Select a lessons program to auto-enroll users when they join this workout program.</Text>
                  
                  {selectedHabitsProgram ? (
                    <Box className="p-3 rounded-lg border border-border-200 bg-background-50 dark:bg-background-100">
                      <VStack space="xs">
                        <Text className="font-semibold text-typography-900 dark:text-white">{selectedHabitsProgram.title}</Text>
                        {selectedHabitsProgram.description && (
                          <Text className="text-sm text-typography-600 dark:text-gray-400">{selectedHabitsProgram.description}</Text>
                        )}
                        <Pressable 
                          onPress={() => setSelectedHabitsProgram(null)}
                          className="self-start mt-2 px-3 py-1 rounded-md bg-red-100 dark:bg-red-900"
                        >
                          <Text className="text-red-700 dark:text-red-300 text-sm">Remove</Text>
                        </Pressable>
                      </VStack>
                    </Box>
                  ) : (
                    <Pressable
                      onPress={() => setHabitsSearchOpen(true)}
                      className="p-3 rounded-lg border border-border-200 bg-background-50 dark:bg-background-100 active:bg-background-100 dark:active:bg-background-200"
                    >
                      <Text className="text-typography-600 dark:text-gray-400">Search for lessons program...</Text>
                    </Pressable>
                  )}
                </VStack>
              )}
            </VStack>

            <VStack space="sm">
              <Text className="text-lg font-semibold text-typography-900 dark:text-white">Workouts</Text>
              <Box className="p-3 rounded-xl border border-border-200 bg-background-50 dark:bg-background-100">
                <Text className="text-typography-600 dark:text-gray-300">Search to add templates; they’ll appear in the sequence below.</Text>
              </Box>

              {/* Search bar opens modal */}
              <Pressable onPress={() => setSearchOpen(true)} className="px-3 py-2 rounded-md border border-border-200 bg-white">
                <Text className="text-typography-600">Search workout templates…</Text>
              </Pressable>

              {/* Divider before sequence preview */}
              <View style={{ height: 1, backgroundColor: '#e5e7eb', marginVertical: 8 }} />

              {/* Sequence list (preview) */}
              <VStack space="sm">
                {links.map((l, idx) => {
                  const t = templates.find(tt => tt.id_ === l.practice_template_id)
                  return (
                    <Box key={`${l.practice_template_id}-${idx}`} className="p-3 rounded-lg border border-indigo-200 bg-indigo-50">
                      <VStack>
                        <Text className="font-semibold text-indigo-800">{idx + 1}. {t?.title || 'Untitled Template'}</Text>
                        <Box className="h-2" />
                        <Text className="text-indigo-800/80">Rest days after:</Text>
                        <View style={{ marginTop: 6, borderWidth: 1, borderColor: '#c7d2fe', borderRadius: 8 }}>
                          <TextInput value={String(l.interval_days_after)} onChangeText={(v) => updateInterval(idx, v)} keyboardType="numeric" style={{ padding: 8 }} />
                        </View>
                        <Box className="h-2" />
                        <Pressable onPress={() => removeLink(idx)} className="self-start px-3 py-1.5 rounded-md border border-red-300"><Text className="text-red-700 font-semibold">Remove</Text></Pressable>
                      </VStack>
                    </Box>
                  )
                })}
              </VStack>
            </VStack>

            <Pressable disabled={saving || !name || links.length === 0} onPress={onSave} className={`${saving || !name || links.length === 0 ? 'bg-indigo-300' : 'bg-indigo-600'} mt-2 items-center justify-center rounded-xl px-4 py-3`}>
              <Text className="text-white font-bold">{saving ? 'Saving…' : 'Save Program'}</Text>
            </Pressable>
          </VStack>
        </ScrollView>

        {/* Template search modal */}
        <Modal visible={searchOpen} transparent animationType="fade" onRequestClose={() => { setSearchOpen(false); setSearch('') }}>
          <View style={{ flex: 1, alignItems: 'center' }}>
            <RNPressable style={{ position: 'absolute', top: 0, bottom: 0, left: 0, right: 0, backgroundColor: 'rgba(0,0,0,0.4)' }} onPress={() => { setSearchOpen(false); setSearch('') }} />
            <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={{ width: '100%', alignItems: 'center', paddingTop: Platform.OS === 'ios' ? 60 : 30 }}>
              <View style={{ width: '96%', maxWidth: 560, maxHeight: 520, borderRadius: 16, backgroundColor: '#fff', padding: 16, flexDirection: 'column', alignSelf: 'center', borderWidth: 1, borderColor: '#e5e7eb' }}>
                <Text style={{ fontSize: 18, fontWeight: '600', marginBottom: 8 }}>Add Workout Template</Text>
                <View style={{ marginBottom: 12 }}>
                  <TextInput placeholder="Search templates…" value={search} onChangeText={setSearch} autoFocus style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10 }} />
                </View>
                <View style={{ flex: 1, minHeight: 240, overflow: 'hidden' }}>
                  <FlatList
                    nestedScrollEnabled
                    keyboardDismissMode="on-drag"
                    keyboardShouldPersistTaps="handled"
                    data={filteredTemplates}
                    keyExtractor={(item: any, i) => item.id_ ?? `${i}`}
                    renderItem={({ item }) => (
                      <RNPressable onPress={() => { addLink(item.id_); setSearchOpen(false); setSearch('') }} style={{ paddingVertical: 10, borderTopWidth: 1, borderTopColor: '#e5e7eb' }}>
                        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                          <View style={{ flex: 1, paddingRight: 8 }}>
                            <Text style={{ fontWeight: '600' }}>{item.title}</Text>
                            {item.description ? <Text style={{ color: '#6b7280' }}>{item.description}</Text> : null}
                          </View>
                          <View style={{ paddingVertical: 4, paddingHorizontal: 8, borderRadius: 999, backgroundColor: '#f0fdf4', borderWidth: 1, borderColor: '#dcfce7' }}>
                            <Text style={{ color: '#16a34a', fontWeight: '700' }}>Template</Text>
                          </View>
                        </View>
                      </RNPressable>
                    )}
                    ListEmptyComponent={(
                      <View style={{ paddingVertical: 16, alignItems: 'center' }}>
                        <Text style={{ color: '#6b7280' }}>{(search||'').trim().length === 0 ? 'Type to search templates' : (searching ? 'Searching…' : 'No matches found')}</Text>
                      </View>
                    )}
                    style={{ flex: 1 }}
                    contentContainerStyle={{ paddingBottom: 8 }}
                  />
                </View>
                <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: 8 }}>
                  <RNPressable onPress={async () => { setSearchOpen(false); setSearch(''); await router.push('/workout-template-create') }} style={{ alignSelf: 'flex-start', paddingVertical: 8, paddingHorizontal: 12, borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8 }}>
                    <Text style={{ color: '#111827', fontWeight: '700' }}>＋ Create Workout Template</Text>
                  </RNPressable>
                  <RNPressable onPress={() => { setSearchOpen(false); setSearch('') }} style={{ alignSelf: 'flex-end', paddingVertical: 8, paddingHorizontal: 12, borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8 }}>
                    <Text style={{ color: '#374151', fontWeight: '600' }}>Close</Text>
                  </RNPressable>
                </View>
              </View>
            </KeyboardAvoidingView>
          </View>
        </Modal>

        {/* Habits Program Search Modal */}
        <Modal visible={habitsSearchOpen} animationType="slide" presentationStyle="pageSheet">
          <View style={{ backgroundColor: '#f9fafb', flex: 1 }}>
            <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
              <View style={{ flexDirection: 'row', alignItems: 'center', padding: 16, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#e5e7eb' }}>
                <TextInput
                  placeholder="Search lessons programs..."
                  value={habitsSearch}
                  onChangeText={setHabitsSearch}
                  style={{ flex: 1, borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 12, backgroundColor: '#fff' }}
                  autoFocus
                />
              </View>
              <View style={{ flex: 1, margin: 16, backgroundColor: '#fff', borderRadius: 8, borderWidth: 1, borderColor: '#e5e7eb', overflow: 'hidden' }}>
                <FlatList
                  nestedScrollEnabled
                  keyboardDismissMode="on-drag"
                  keyboardShouldPersistTaps="handled"
                  data={filteredHabitsPrograms}
                  keyExtractor={(item: any, i) => item.id ?? `${i}`}
                  renderItem={({ item }) => (
                    <RNPressable onPress={() => { setSelectedHabitsProgram(item); setHabitsSearchOpen(false); setHabitsSearch('') }} style={{ paddingVertical: 10, borderTopWidth: 1, borderTopColor: '#e5e7eb' }}>
                      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                        <View style={{ flex: 1, paddingRight: 8 }}>
                          <Text style={{ fontWeight: '600' }}>{item.title}</Text>
                          {item.subtitle ? <Text style={{ color: '#6b7280', fontSize: 14 }}>{item.subtitle}</Text> : null}
                          {item.description ? <Text style={{ color: '#6b7280', fontSize: 12 }} numberOfLines={2}>{item.description}</Text> : null}
                        </View>
                        <View style={{ paddingVertical: 4, paddingHorizontal: 8, borderRadius: 999, backgroundColor: '#fef3c7', borderWidth: 1, borderColor: '#fde68a' }}>
                          <Text style={{ color: '#d97706', fontWeight: '700' }}>Lessons</Text>
                        </View>
                      </View>
                    </RNPressable>
                  )}
                  ListEmptyComponent={(
                    <View style={{ paddingVertical: 16, alignItems: 'center' }}>
                      <Text style={{ color: '#6b7280' }}>{habitsLoading ? 'Loading lessons programs...' : ((habitsSearch||'').trim().length === 0 ? 'Type to search lessons programs' : 'No matches found')}</Text>
                    </View>
                  )}
                  style={{ flex: 1 }}
                  contentContainerStyle={{ paddingBottom: 8 }}
                />
              </View>
              <View style={{ flexDirection: 'row', justifyContent: 'flex-end', marginHorizontal: 16, marginBottom: 16 }}>
                <RNPressable onPress={() => { setHabitsSearchOpen(false); setHabitsSearch('') }} style={{ alignSelf: 'flex-end', paddingVertical: 8, paddingHorizontal: 12, borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8 }}>
                  <Text style={{ color: '#374151', fontWeight: '600' }}>Close</Text>
                </RNPressable>
              </View>
            </KeyboardAvoidingView>
          </View>
        </Modal>
      </VStack>
    </SafeAreaView>
  )
} 