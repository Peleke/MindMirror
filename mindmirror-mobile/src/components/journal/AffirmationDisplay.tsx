import React from 'react';
import { Box } from '@/components/ui/box';
import { Sparkles } from 'lucide-react-native';
import { Icon } from '@/components/ui/icon';
import { Text } from '@/components/ui/text';
import { HStack } from '@/components/ui/hstack';

export type AffirmationDisplayProps = {
  affirmation: string;
  className?: string;
};

export function AffirmationDisplay({ affirmation, className = "" }: AffirmationDisplayProps) {
  return (
    <Box className={`p-4 rounded-lg bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950 dark:to-indigo-950 ${className}`}>
      <HStack className="items-center space-x-3">
        <Icon 
          as={Sparkles}
          size="md"
          className="text-blue-600 dark:text-blue-400"
        />
        <Text className="text-base text-typography-800 dark:text-gray-200 flex-1">
          {affirmation}
        </Text>
      </HStack>
    </Box>
  );
} 