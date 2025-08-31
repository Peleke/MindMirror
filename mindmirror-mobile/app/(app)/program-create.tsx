import React, { useMemo, useState } from 'react'
import { SafeAreaView } from '@/components/ui/safe-area-view'
import { AppBar } from '@/components/common/AppBar'
import { VStack } from '@/components/ui/vstack'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { Input, InputField } from '@/components/ui/input'
import { Pressable } from '@/components/ui/pressable'
import { ScrollView } from '@/components/ui/scroll-view'
import { usePracticeTemplates, useCreateProgram } from '@/services/api/practices'
import { QUERY_PROGRAM_TEMPLATES } from '@/services/api/practices'
import { useRouter, useLocalSearchParams } from 'expo-router'
import { TextInput, View, Modal, KeyboardAvoidingView, Platform, FlatList } from 'react-native'
import { useApolloClient } from '@apollo/client'

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
  const [createProgram, { loading: saving }] = useCreateProgram()

  // Template search modal state
  const [searchOpen, setSearchOpen] = useState(false)
  const [search, setSearch] = useState('')
  const filteredTemplates = useMemo(() => {
    const q = (search || '').trim().toLowerCase()
    if (!q) return templates
    return templates.filter(t => t.title.toLowerCase().includes(q))
  }, [search, templates])

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
              <Input className="bg-background-50 dark:bg-background-100"><InputField placeholder="Description (optional)" value={description} onChangeText={setDescription} /></Input>
              <Input className="bg-background-50 dark:bg-background-100"><InputField placeholder="Level (optional)" value={level} onChangeText={setLevel} /></Input>
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

            <Pressable disabled={saving || !name || links.length === 0} onPress={onSave} className={`mt-2 items-center justify-center rounded-xl px-4 py-3 ${saving || !name || links.length === 0 ? 'bg-indigo-300' : 'bg-indigo-600'}`}>
              <Text className="text-white font-bold">{saving ? 'Saving…' : 'Save Program'}</Text>
            </Pressable>
          </VStack>
        </ScrollView>

        {/* Template search modal */}
        <Modal visible={searchOpen} transparent animationType="fade" onRequestClose={() => { setSearchOpen(false); setSearch('') }}>
          <View style={{ flex: 1, alignItems: 'center' }}>
            <Pressable onPress={() => { setSearchOpen(false); setSearch('') }} className="absolute top-0 bottom-0 left-0 right-0" style={{ backgroundColor: 'rgba(0,0,0,0.4)' }} />
            <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={{ width: '100%', alignItems: 'center', paddingTop: Platform.OS === 'ios' ? 60 : 30 }}>
              <View style={{ width: '96%', height: '70%', maxHeight: '70%', borderRadius: 16, backgroundColor: '#fff', padding: 16 }}>
                <Text className="text-typography-900" style={{ fontWeight: '700', fontSize: 16, marginBottom: 8 }}>Add Workout Template</Text>
                <View style={{ marginBottom: 12 }}>
                  <TextInput placeholder="Search templates…" value={search} onChangeText={setSearch} autoFocus style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 8, padding: 10 }} />
                </View>
                <FlatList
                  keyboardDismissMode="on-drag"
                  keyboardShouldPersistTaps="handled"
                  data={filteredTemplates}
                  keyExtractor={(item: any, i) => item.id_ ?? `${i}`}
                  renderItem={({ item }) => (
                    <Pressable onPress={() => { addLink(item.id_); setSearchOpen(false); setSearch('') }} className="py-2" style={{ borderTopWidth: 1, borderTopColor: '#e5e7eb' }}>
                      <View>
                        <Text className="font-semibold text-typography-900">{item.title}</Text>
                        {item.description ? <Text className="text-typography-600">{item.description}</Text> : null}
                      </View>
                    </Pressable>
                  )}
                  ListEmptyComponent={(
                    <View style={{ paddingVertical: 16, alignItems: 'center' }}>
                      <Text className="text-typography-600">{(search||'').trim().length === 0 ? 'Type to search templates' : 'No matches found'}</Text>
                    </View>
                  )}
                  style={{ flex: 1 }}
                  contentContainerStyle={{ paddingBottom: 12 }}
                />
                <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: 12 }}>
                  <Pressable onPress={async () => { setSearchOpen(false); setSearch(''); await router.push('/workout-template-create') }} className="px-3 py-1.5 rounded-md border border-indigo-300 bg-indigo-50">
                    <Text className="text-indigo-700 font-semibold">＋ Create Workout Template</Text>
                  </Pressable>
                  <Pressable onPress={() => { setSearchOpen(false); setSearch('') }} className="px-3 py-1.5 rounded-md border border-border-200">
                    <Text className="text-typography-900 font-semibold">Close</Text>
                  </Pressable>
                </View>
              </View>
            </KeyboardAvoidingView>
          </View>
        </Modal>
      </VStack>
    </SafeAreaView>
  )
} 