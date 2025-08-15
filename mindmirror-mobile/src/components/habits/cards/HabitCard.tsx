import React from 'react'
import { Pressable } from '@/components/ui/pressable'
import { Box } from '@/components/ui/box'
import { VStack } from '@/components/ui/vstack'
import { HStack } from '@/components/ui/hstack'
import { Icon } from '@/components/ui/icon'
import { Text } from '@/components/ui/text'
import { Button, ButtonText } from '@/components/ui/button'
import { HabitTask } from '@/types/habits'
import { Heart } from 'lucide-react-native'
import { useState } from 'react'

export default function HabitCard({ task, onRespond, onPress }: { task: HabitTask; onRespond: (r: 'yes' | 'no') => void; onPress?: () => void }) {
  const [justSwiped, setJustSwiped] = useState(false)
  const [lastResponse, setLastResponse] = useState<'yes' | 'no' | null>(null)
  return (
    <>
      <Pressable className="w-full" onPress={() => { if (!justSwiped && onPress) onPress() }}>
        <Box className="p-4 rounded-lg border bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800 shadow">
          <VStack space="sm">
            <HStack space="sm" className="items-center">
              <Icon as={Heart} size="md" className="text-blue-600 dark:text-blue-400" />
              <Text className="text-lg font-semibold text-typography-900 dark:text-white">{task.title}</Text>
            </HStack>
            <Text className="text-typography-600 dark:text-gray-300">{(task as any).subtitle || task.description || 'No description provided.'}</Text>
            <HStack className="justify-between" space="sm">
              <Button onPress={() => { setLastResponse('yes'); onRespond('yes') }} className={`flex-1 ${lastResponse==='yes' ? 'bg-blue-500' : 'bg-blue-400'}`}>
                <ButtonText>Yes</ButtonText>
              </Button>
              <Button onPress={() => { setLastResponse('no'); onRespond('no') }} className={`flex-1 ${lastResponse==='no' ? 'bg-red-500' : 'bg-red-400'}`}>
                <ButtonText>No</ButtonText>
              </Button>
            </HStack>
          </VStack>
        </Box>
      </Pressable>
    </>
  )
}


