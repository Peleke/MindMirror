import React, { useState } from 'react'
import { Modal, View, TextInput, Text as RNText, FlatList, Pressable as RNPressable } from 'react-native'
import { useRouter } from 'expo-router'
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
import { MovementCard } from '@/components/workout'

type BlockType = 'warmup' | 'workout' | 'cooldown'

type Set = {
  position: number
  reps?: number
  duration?: number
  loadValue?: number
  loadUnit?: string
  restDuration?: number
}

type Movement = {
  id: string // local ID for React keys
  name: string
  position: number
  block: BlockType
  metricUnit: 'iterative' | 'temporal'
  sets: Set[]
  shortVideoUrl?: string
  movementId?: string
}

export default function WorkoutTemplateCreateV2Screen() {
  const router = useRouter()
  const apollo = useApolloClient()
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [movements, setMovements] = useState<Movement[]>([])

  // Movement search
  const [isPickerOpen, setPickerOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [runSearch, { data: searchData }] = useLazySearchMovements()

  const addMovement = (m: any) => {
    const newMovement: Movement = {
      id: `${Date.now()}-${Math.random()}`,
      name: m.name,
      position: movements.length + 1,
      block: 'workout', // default block
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
      const newSet: Set = {
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
      const updatedSet: Set = {
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

  return (
    <SafeAreaView className="h-full w-full">
      <VStack className="h-full w-full bg-background-0">
        <AppBar title="Create Workout Template" showBackButton onBackPress={() => router.back()} />
        <ScrollView className="flex-1">
          <VStack className="w-full max-w-screen-md mx-auto px-6 py-6" space="lg">
            {/* Title & Description */}
            <VStack space="sm">
              <Text className="text-2xl font-bold text-typography-900 dark:text-white">Template Details</Text>
              <Input className="bg-background-50"><InputField placeholder="Title" value={title} onChangeText={setTitle} /></Input>
              <Input className="bg-background-50"><InputField placeholder="Description (optional)" value={description} onChangeText={setDescription} /></Input>
            </VStack>

            <Box className="h-px bg-border-200 dark:bg-border-700" />

            {/* Add Movement Button */}
            <Pressable
              onPress={() => setPickerOpen(true)}
              className="px-4 py-3 rounded-xl border-2 border-dashed border-indigo-300 bg-indigo-50 dark:bg-indigo-900"
            >
              <Text className="text-center text-indigo-700 dark:text-indigo-200 font-semibold">+ Add Movement</Text>
            </Pressable>

            {/* Movements List */}
            <VStack space="md">
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
                />
              ))}
            </VStack>

            {/* Save Button */}
            <Pressable
              disabled={saving || !title}
              onPress={onSubmit}
              className="mt-4 px-4 py-3 rounded-xl bg-indigo-600 disabled:bg-indigo-300"
            >
              <Text className="text-center text-white font-bold">
                {saving ? 'Saving...' : 'Save Template'}
              </Text>
            </Pressable>
          </VStack>
        </ScrollView>
      </VStack>

      {/* Movement Search Modal */}
      <Modal visible={isPickerOpen} transparent animationType="fade" onRequestClose={() => setPickerOpen(false)}>
        <View style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'center', alignItems: 'center' }}>
          <RNPressable style={{ position: 'absolute', top: 0, bottom: 0, left: 0, right: 0 }} onPress={() => setPickerOpen(false)} />
          <Box className="w-11/12 max-w-md bg-white dark:bg-background-100 rounded-xl p-4">
            <Text className="text-lg font-bold mb-3">Search Movements</Text>
            <TextInput
              placeholder="Type to search..."
              value={searchTerm}
              onChangeText={(t) => {
                setSearchTerm(t)
                if (t.length > 2) runSearch({ variables: { searchTerm: t, limit: 20 } })
              }}
              className="bg-background-50 dark:bg-background-200 border border-border-200 rounded-lg px-3 py-2 mb-3"
            />
            <FlatList
              data={searchData?.searchMovements?.filter((m: any) => !m.isExternal) || []}
              keyExtractor={(item: any) => item.id_}
              renderItem={({ item }) => (
                <RNPressable
                  onPress={() => {
                    addMovement(item)
                    setPickerOpen(false)
                    setSearchTerm('')
                  }}
                  style={{ paddingVertical: 12, borderTopWidth: 1, borderTopColor: '#e5e7eb' }}
                >
                  <RNText style={{ fontWeight: '600' }}>{item.name}</RNText>
                  <RNText style={{ color: '#6b7280', fontSize: 12 }}>{item.bodyRegion}</RNText>
                </RNPressable>
              )}
              style={{ maxHeight: 300 }}
            />
            <Pressable onPress={() => setPickerOpen(false)} className="mt-3 px-4 py-2 border border-border-200 rounded-lg">
              <Text className="text-center font-semibold">Close</Text>
            </Pressable>
          </Box>
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
    </SafeAreaView>
  )
}
