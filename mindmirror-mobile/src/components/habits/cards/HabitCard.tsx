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
import { useThemeVariant } from '@/theme/ThemeContext'

export default function HabitCard({ task, onRespond, onPress }: { task: HabitTask; onRespond: (r: 'yes' | 'no') => void; onPress?: () => void }) {
  const [justSwiped, setJustSwiped] = useState(false)
  const [lastResponse, setLastResponse] = useState<'yes' | 'no' | null>(null)
  const { themeId } = useThemeVariant()
  const isClassic = themeId === 'classic'
  return (
    <>
      <Pressable className="w-full" onPress={() => { if (!justSwiped && onPress) onPress() }}>
        <Box className={`p-4 rounded-lg border shadow ${isClassic ? 'bg-teal-50 dark:bg-teal-950 border-teal-200 dark:border-teal-800' : 'bg-background-200 dark:bg-background-700 border-border-300 dark:border-border-700'}`}>
          <VStack space="sm">
            <HStack space="sm" className="items-center">
              <Icon as={Heart} size="md" className={isClassic ? 'text-teal-700 dark:text-teal-300' : 'text-primary-700 dark:text-primary-300'} />
              <Text className="text-lg font-semibold text-typography-900 dark:text-white">{task.title}</Text>
            </HStack>
            <Text className="text-typography-600 dark:text-gray-300">{(task as any).subtitle || task.description || ''}</Text>
            <HStack className="justify-between" space="sm">
              {isClassic ? (
                <>
              <Button onPress={() => { setLastResponse('yes'); onRespond('yes') }} className={`flex-1 ${lastResponse==='yes' ? 'bg-blue-500' : 'bg-blue-400'}`}>
                <ButtonText>Yes</ButtonText>
              </Button>
              <Button onPress={() => { setLastResponse('no'); onRespond('no') }} className={`flex-1 ${lastResponse==='no' ? 'bg-red-500' : 'bg-red-400'}`}>
                <ButtonText>No</ButtonText>
              </Button>
                </>
              ) : (
                <>
                  <Button onPress={() => { setLastResponse('yes'); onRespond('yes') }} className={`flex-1 ${lastResponse==='yes' ? 'bg-success-600' : 'bg-success-500'}`}>
                    <ButtonText>Yes</ButtonText>
                  </Button>
                  <Button onPress={() => { setLastResponse('no'); onRespond('no') }} className={`flex-1 border ${lastResponse==='no' ? 'bg-error-50 border-error-300' : 'bg-background-0 border-border-200'}`}>
                    <ButtonText>No</ButtonText>
                  </Button>
                </>
              )}
            </HStack>
          </VStack>
        </Box>
      </Pressable>
    </>
  )
}


