import React from 'react'
import { Pressable } from '@/components/ui/pressable'
import Markdown from 'react-native-markdown-display'
import { Box } from '@/components/ui/box'
import { VStack } from '@/components/ui/vstack'
import { HStack } from '@/components/ui/hstack'
import { Icon } from '@/components/ui/icon'
import { Text } from '@/components/ui/text'
import { Dumbbell } from 'lucide-react-native'

interface WorkoutTask {
  id_: string
  name: string
  description?: string
  level?: string
  date: string
  completed: boolean
  enrollment_id?: string
  practice_instance_id?: string
}

export default function WorkoutCard({ 
  task, 
  onPress, 
  onDefer 
}: { 
  task: WorkoutTask
  onPress: () => void
  onDefer?: () => void | Promise<void>
}) {
  return (
    <Pressable className="w-full" onPress={onPress}>
      <Box className="p-4 rounded-lg border bg-indigo-50 dark:bg-indigo-950 border-indigo-200 dark:border-indigo-800 shadow">
        <VStack space="sm">
          <HStack space="sm" className="items-center justify-between">
            <HStack space="sm" className="items-center flex-1">
              <Icon as={Dumbbell} size="md" className="text-indigo-700 dark:text-indigo-300" />
              <Text className="text-lg font-semibold text-typography-900 dark:text-white flex-1">{task.name}</Text>
            </HStack>
            {!!task.level && (
              <Box className="px-2 py-0.5 rounded-full bg-indigo-100 border border-indigo-200">
                <Text className="text-xs text-indigo-700 font-semibold">{task.level}</Text>
              </Box>
            )}
          </HStack>
          {!!task.description && (
            <Box className="rounded border border-indigo-200/60 bg-white/60 p-2">
              <Markdown>{task.description}</Markdown>
            </Box>
          )}
          {task.enrollment_id && onDefer && (
            <HStack className="justify-end">
              <Pressable onPress={onDefer} className="px-2 py-1 rounded border border-indigo-200 bg-white/60">
                <Text className="text-xs text-indigo-700">Defer</Text>
              </Pressable>
            </HStack>
          )}
        </VStack>
      </Box>
    </Pressable>
  )
} 