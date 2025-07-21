import React from 'react';
import { Text } from '@/components/ui/text';
import { Box } from '@/components/ui/box';
import { VStack } from '@/components/ui/vstack';
import { HStack } from '@/components/ui/hstack';
import { Icon } from '@/components/ui/icon';
import { Sparkles } from 'lucide-react-native';

interface AffirmationDisplayProps {
  affirmation: string;
  isLoading?: boolean;
  className?: string;
}

export function AffirmationDisplay({ 
  affirmation, 
  isLoading = false, 
  className = "" 
}: AffirmationDisplayProps) {
  if (isLoading) {
    return (
      <Box className={`p-4 bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-950 dark:to-blue-950 rounded-lg border border-purple-200 dark:border-purple-700 ${className}`}>
        <VStack className="space-y-2">
          <HStack className="items-center space-x-2">
            <Icon as={Sparkles} size="sm" className="text-purple-600 dark:text-purple-400" />
            <Text className="text-sm font-medium text-purple-700 dark:text-purple-300">
              Generating your affirmation...
            </Text>
          </HStack>
          <HStack className="items-center space-x-1">
            <Box className="w-2 h-2 bg-purple-400 dark:bg-purple-500 rounded-full animate-pulse" />
            <Box className="w-2 h-2 bg-purple-400 dark:bg-purple-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
            <Box className="w-2 h-2 bg-purple-400 dark:bg-purple-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
          </HStack>
        </VStack>
      </Box>
    );
  }

  return (
    <Box className={`p-4 bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-950 dark:to-blue-950 rounded-lg border border-purple-200 dark:border-purple-700 ${className}`}>
      <VStack className="space-y-2">
        <HStack className="items-center space-x-2">
          <Icon as={Sparkles} size="sm" className="text-purple-600 dark:text-purple-400" />
          <Text className="text-sm font-medium text-purple-700 dark:text-purple-300">
            Today's Affirmation
          </Text>
        </HStack>
        <Text className="text-base text-typography-800 dark:text-gray-200 leading-6 italic">
          "{affirmation}"
        </Text>
      </VStack>
    </Box>
  );
} 