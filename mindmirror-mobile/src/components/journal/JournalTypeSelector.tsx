import React from 'react';
import { Text } from '@/components/ui/text';
import { Box } from '@/components/ui/box';
import { HStack } from '@/components/ui/hstack';
import { VStack } from '@/components/ui/vstack';
import { Pressable } from '@/components/ui/pressable';
import { Icon } from '@/components/ui/icon';
import { Heart, Lightbulb } from 'lucide-react-native';

export type JournalType = 'gratitude' | 'reflection' | 'freeform';

interface JournalTypeSelectorProps {
  onGratitudePress: () => void;
  onReflectionPress: () => void;
  className?: string;
}



export function JournalTypeSelector({ 
  onGratitudePress, 
  onReflectionPress, 
  className = "" 
}: JournalTypeSelectorProps) {
  return (
    <HStack className={`space-x-3 ${className}`}>
      <Pressable
        onPress={onGratitudePress}
        className="flex-1"
      >
        <Box className="p-4 rounded-lg border bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-700">
          <VStack className="space-y-2">
            <HStack className="items-center space-x-2">
              <Icon 
                as={Heart}
                size="sm"
                className="text-blue-600 dark:text-blue-400"
              />
              <Text className="text-sm font-medium text-typography-700 dark:text-gray-300">
                Gratitude
              </Text>
            </HStack>
            <Text className="text-xs text-typography-500 dark:text-gray-400">
              What are you grateful for?
            </Text>
          </VStack>
        </Box>
      </Pressable>

      <Pressable
        onPress={onReflectionPress}
        className="flex-1"
      >
        <Box className="p-4 rounded-lg border bg-indigo-50 dark:bg-indigo-950 border-indigo-200 dark:border-indigo-700">
          <VStack className="space-y-2">
            <HStack className="items-center space-x-2">
              <Icon 
                as={Lightbulb}
                size="sm"
                className="text-indigo-600 dark:text-indigo-400"
              />
              <Text className="text-sm font-medium text-typography-700 dark:text-gray-300">
                Reflection
              </Text>
            </HStack>
            <Text className="text-xs text-typography-500 dark:text-gray-400">
              Reflect on your day
            </Text>
          </VStack>
        </Box>
      </Pressable>
    </HStack>
  );
} 