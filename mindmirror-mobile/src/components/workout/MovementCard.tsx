import React, { useState } from 'react'
import { View, Image, Modal, Pressable as RNPressable, Platform } from 'react-native'
import { Pressable } from '@/components/ui/pressable'
import { Box } from '@/components/ui/box'
import { Text } from '@/components/ui/text'
import { VStack } from '@/components/ui/vstack'
import { HStack } from '@/components/ui/hstack'
import { useVideoPlayer, VideoView } from 'expo-video'
import { WebView } from 'react-native-webview'

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
  onEditSet: (setIndex: number) => void
  onRemoveSet: (setIndex: number) => void
}

/**
 * Renders video thumbnail or full video modal
 */
function VideoThumbnail({ videoUrl }: { videoUrl: string }) {
  const [showVideo, setShowVideo] = useState(false)

  // Check if it's an mp4 for thumbnail
  const isMp4 = /\.mp4$/i.test(videoUrl)

  return (
    <>
      {/* Thumbnail */}
      <Pressable onPress={() => setShowVideo(true)}>
        <Box className="overflow-hidden rounded-lg border border-border-200" style={{ width: 60, height: 60 }}>
          <Image
            source={{ uri: videoUrl }}
            style={{ width: '100%', height: '100%', resizeMode: 'cover' }}
          />
        </Box>
      </Pressable>

      {/* Full video modal */}
      <Modal visible={showVideo} transparent animationType="fade" onRequestClose={() => setShowVideo(false)}>
        <View style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.8)', justifyContent: 'center', alignItems: 'center' }}>
          <RNPressable
            style={{ position: 'absolute', top: 0, bottom: 0, left: 0, right: 0 }}
            onPress={() => setShowVideo(false)}
          />
          <Box className="overflow-hidden rounded-xl border border-border-200" style={{ width: '90%', height: 300 }}>
            {isMp4 ? (
              <VideoView
                style={{ width: '100%', height: '100%' }}
                player={useVideoPlayer(videoUrl, (p) => { p.loop = false })}
                allowsFullscreen
                allowsPictureInPicture
              />
            ) : (
              // Handle YouTube/Vimeo
              <WebView source={{ uri: videoUrl }} allowsInlineMediaPlayback javaScriptEnabled />
            )}
          </Box>
          <Pressable onPress={() => setShowVideo(false)} className="mt-4 px-4 py-2 bg-white rounded-lg">
            <Text className="font-semibold">Close</Text>
          </Pressable>
        </View>
      </Modal>
    </>
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
  onRemoveSet,
}: MovementCardProps) {
  return (
    <Box className="p-3 rounded-xl border bg-white dark:bg-background-0 border-border-200 dark:border-border-700">
      <VStack space="sm">
        {/* Header row: thumbnail | name | remove */}
        <HStack space="sm" className="items-center">
          {shortVideoUrl && <VideoThumbnail videoUrl={shortVideoUrl} />}

          <Text
            className="flex-1 font-semibold text-typography-900 dark:text-white"
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

        {/* Set summary - compact chips */}
        {sets.length > 0 && (
          <HStack space="xs" className="flex-wrap">
            {sets.map((set, index) => {
              const repsOrDuration = metricUnit === 'temporal'
                ? `${set.duration ?? 0}s`
                : `${set.reps ?? 0} reps`

              const load = set.loadValue
                ? `${set.loadValue}${set.loadUnit === 'bodyweight' ? 'BW' : set.loadUnit === 'pounds' ? 'lb' : set.loadUnit === 'kilograms' ? 'kg' : ''}`
                : 'BW'

              return (
                <Pressable
                  key={index}
                  onPress={() => onEditSet(index)}
                >
                  <Box className="px-2 py-1 rounded-md border border-border-200 dark:border-border-700 bg-background-50 dark:bg-background-100">
                    <HStack space="xs" className="items-center">
                      <Text className="text-typography-700 dark:text-gray-200 text-xs font-semibold">
                        {index + 1}.
                      </Text>
                      <Text className="text-typography-700 dark:text-gray-200 text-xs">
                        {repsOrDuration} × {load}
                      </Text>
                      <Pressable onPress={() => onRemoveSet(index)}>
                        <Text className="text-red-700 text-xs">✕</Text>
                      </Pressable>
                    </HStack>
                  </Box>
                </Pressable>
              )
            })}
          </HStack>
        )}
      </VStack>
    </Box>
  )
}
