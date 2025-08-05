import { VStack } from '@/components/ui/vstack';
import { HStack } from '@/components/ui/hstack';
import { Text } from '@/components/ui/text';

interface MoodDisplayProps {
  mood: number;
}

export function MoodDisplay({ mood }: MoodDisplayProps) {
  const getMoodLabel = (moodValue: number): string => {
    if (moodValue <= 3) return 'Low';
    if (moodValue <= 7) return 'Good';
    return 'Great';
  };

  return (
    <VStack space="xs">
      <Text className="text-sm font-medium text-typography-700 dark:text-gray-300">
        Mood Rating
      </Text>
      <HStack className="items-center justify-between bg-white dark:bg-gray-100 rounded-lg p-4">
        <Text className="text-xs text-typography-500">1</Text>
        <VStack className="items-center">
          <Text className="text-2xl font-bold text-typography-900">
            {mood}
          </Text>
          <Text className="text-xs text-typography-500">
            {getMoodLabel(mood)}
          </Text>
        </VStack>
        <Text className="text-xs text-typography-500">10</Text>
      </HStack>
    </VStack>
  );
} 