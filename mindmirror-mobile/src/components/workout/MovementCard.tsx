import React, { useState } from 'react'
import { Image, TextInput } from 'react-native'
import { Pressable } from '@/components/ui/pressable'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { VStack } from '@/components/ui/vstack'
import { HStack } from '@/components/ui/hstack'

type BlockType = 'warmup' | 'workout' | 'cooldown'

type Set = {
  position: number
  reps?: number
  duration?: number
  loadValue?: number
  loadUnit?: string
  restDuration?: number
}

export interface MovementCardProps {
  movementName: string
  block: BlockType
  sets: Set[]
  shortVideoUrl?: string
  metricUnit: 'iterative' | 'temporal'
  onBlockChange: (block: BlockType) => void
  onRemove: () => void
  onAddSet: () => void
  onEditSet?: (setIndex: number) => void // Optional - for modal-based editing
  onUpdateSet?: (setIndex: number, field: keyof Set, value: string) => void // For inline editing
  onRemoveSet: (setIndex: number) => void
  onViewDetails?: () => void
}

/**
 * Circular video thumbnail like Hevy - clickable to open details
 * Shows play icon placeholder (video thumbnails require external API)
 */
function CircularThumbnail({
  videoUrl,
  onPress
}: {
  videoUrl: string
  onPress: () => void
}) {
  return (
    <Pressable onPress={onPress}>
      <Box
        className="overflow-hidden rounded-full border-2 border-indigo-300 dark:border-indigo-700 bg-indigo-50 dark:bg-indigo-900"
        style={{ width: 48, height: 48, alignItems: 'center', justifyContent: 'center' }}
      >
        <Text className="text-indigo-700 dark:text-indigo-200 text-2xl">▶</Text>
      </Box>
    </Pressable>
  )
}

/**
 * Block type selector chips
 */
function BlockSelector({
  currentBlock,
  onChange
}: {
  currentBlock: BlockType
  onChange: (block: BlockType) => void
}) {
  const blocks: BlockType[] = ['warmup', 'workout', 'cooldown']

  return (
    <HStack space="xs">
      {blocks.map(block => {
        const isSelected = currentBlock === block
        return (
          <Pressable
            key={block}
            onPress={() => onChange(block)}
            className={`px-3 py-1.5 rounded-full border ${
              isSelected
                ? 'border-indigo-400 bg-indigo-50 dark:bg-indigo-900'
                : 'border-border-200 bg-background-50'
            }`}
          >
            <Text className={`text-xs font-semibold ${
              isSelected
                ? 'text-indigo-700 dark:text-indigo-200'
                : 'text-typography-600'
            }`}>
              {block.charAt(0).toUpperCase() + block.slice(1)}
            </Text>
          </Pressable>
        )
      })}
    </HStack>
  )
}

/**
 * Editable set row - shows duration OR reps based on metricUnit
 */
function SetRow({
  setNumber,
  set,
  metricUnit,
  onUpdate,
  onRemove
}: {
  setNumber: number
  set: Set
  metricUnit: 'iterative' | 'temporal'
  onUpdate: (field: keyof Set, value: string) => void
  onRemove: () => void
}) {
  // Sync local state with prop values
  const [repsValue, setRepsValue] = useState(String(set.reps ?? ''))
  const [durationValue, setDurationValue] = useState(String(set.duration ?? ''))
  const [loadValue, setLoadValue] = useState(String(set.loadValue ?? ''))
  const [restValue, setRestValue] = useState(String(set.restDuration ?? ''))

  React.useEffect(() => {
    setRepsValue(String(set.reps ?? ''))
    setDurationValue(String(set.duration ?? ''))
    setLoadValue(String(set.loadValue ?? ''))
    setRestValue(String(set.restDuration ?? ''))
  }, [set.reps, set.duration, set.loadValue, set.restDuration])

  return (
    <Box className="flex-row items-center px-2 py-1 rounded-md border border-border-200 dark:border-border-700 bg-background-50 dark:bg-background-100">
      {/* Set number */}
      <Box className="w-8">
        <Text className="text-typography-700 dark:text-gray-200 text-sm">{setNumber}</Text>
      </Box>

      {/* Reps or Duration field */}
      <Box className="flex-1 mr-1">
        <TextInput
          keyboardType="numeric"
          value={metricUnit === 'temporal' ? durationValue : repsValue}
          onChangeText={metricUnit === 'temporal' ? setDurationValue : setRepsValue}
          onBlur={() => onUpdate(metricUnit === 'temporal' ? 'duration' : 'reps', metricUnit === 'temporal' ? durationValue : repsValue)}
          placeholder={metricUnit === 'temporal' ? '30' : '10'}
          style={{
            borderWidth: 1,
            borderColor: '#e5e7eb',
            borderRadius: 6,
            paddingHorizontal: 8,
            paddingVertical: 6,
            backgroundColor: '#fff',
            fontSize: 13
          }}
        />
      </Box>

      {/* Load field */}
      <Box className="flex-1 mr-1">
        <TextInput
          keyboardType="numeric"
          value={loadValue}
          onChangeText={setLoadValue}
          onBlur={() => onUpdate('loadValue', loadValue)}
          placeholder="45"
          style={{
            borderWidth: 1,
            borderColor: '#e5e7eb',
            borderRadius: 6,
            paddingHorizontal: 8,
            paddingVertical: 6,
            backgroundColor: '#fff',
            fontSize: 13
          }}
        />
      </Box>

      {/* Rest duration field */}
      <Box className="flex-1 mr-1">
        <TextInput
          keyboardType="numeric"
          value={restValue}
          onChangeText={setRestValue}
          onBlur={() => onUpdate('restDuration', restValue)}
          placeholder="60"
          style={{
            borderWidth: 1,
            borderColor: '#e5e7eb',
            borderRadius: 6,
            paddingHorizontal: 8,
            paddingVertical: 6,
            backgroundColor: '#fff',
            fontSize: 13
          }}
        />
      </Box>

      {/* Remove button */}
      <Box className="w-10 items-center">
        <Pressable onPress={onRemove}>
          <Text className="text-red-700 dark:text-red-400 text-sm">✕</Text>
        </Pressable>
      </Box>
    </Box>
  )
}

/**
 * Compact movement card with thumbnail, block selector, and set editor
 */
export function MovementCard({
  movementName,
  block,
  sets,
  shortVideoUrl,
  metricUnit,
  onBlockChange,
  onRemove,
  onAddSet,
  onEditSet,
  onUpdateSet,
  onRemoveSet,
  onViewDetails,
}: MovementCardProps) {
  return (
    <Box className="p-3 rounded-xl border bg-white dark:bg-background-0 border-border-200 dark:border-border-700">
      <VStack space="sm">
        {/* Header row: thumbnail | name | remove */}
        <HStack space="sm" className="items-center">
          {shortVideoUrl && onViewDetails && (
            <CircularThumbnail videoUrl={shortVideoUrl} onPress={onViewDetails} />
          )}

          <Text
            className="flex-1 font-semibold text-typography-900 dark:text-white text-base"
            numberOfLines={1}
            ellipsizeMode="tail"
          >
            {movementName}
          </Text>

          <Pressable
            onPress={onRemove}
            className="px-2 py-1 rounded-md border border-red-300 bg-white dark:bg-background-0"
          >
            <Text className="text-red-700 dark:text-red-300 text-sm">Remove</Text>
          </Pressable>
        </HStack>

        {/* Block selector */}
        <BlockSelector currentBlock={block} onChange={onBlockChange} />

        {/* Set count + Add Set button */}
        <HStack space="sm" className="items-center justify-between">
          <Text className="text-typography-600 dark:text-gray-300">{sets.length} sets</Text>
          <Pressable
            onPress={onAddSet}
            className="px-3 py-1.5 rounded-md border border-border-200 dark:border-border-700"
          >
            <Text className="text-typography-700 dark:text-gray-200 font-semibold text-sm">Add Set</Text>
          </Pressable>
        </HStack>

        {/* Set table - vertical stacked editable rows */}
        {sets.length > 0 && (
          <VStack space="xs">
            {/* Header row */}
            <Box className="flex-row items-center px-2 py-1 bg-background-100 rounded-md">
              <Box className="w-8"><Text className="text-typography-600 dark:text-gray-400 text-xs font-semibold">#</Text></Box>
              <Box className="flex-1">
                <Text className="text-typography-600 dark:text-gray-400 text-xs font-semibold">
                  {metricUnit === 'temporal' ? 'Duration' : 'Reps'}
                </Text>
              </Box>
              <Box className="flex-1"><Text className="text-typography-600 dark:text-gray-400 text-xs font-semibold">Load</Text></Box>
              <Box className="flex-1"><Text className="text-typography-600 dark:text-gray-400 text-xs font-semibold">Rest (s)</Text></Box>
              <Box className="w-10" />
            </Box>

            {/* Editable set rows */}
            {sets.map((set, index) => (
              <SetRow
                key={index}
                setNumber={index + 1}
                set={set}
                metricUnit={metricUnit}
                onUpdate={(field, value) => {
                  // Use inline update if available, fallback to modal
                  if (onUpdateSet) {
                    onUpdateSet(index, field, value)
                  } else if (onEditSet) {
                    onEditSet(index)
                  }
                }}
                onRemove={() => onRemoveSet(index)}
              />
            ))}
          </VStack>
        )}
      </VStack>
    </Box>
  )
}
