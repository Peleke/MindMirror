import React from 'react';
import { Box } from '@/components/ui/box';
import { Sparkles } from 'lucide-react-native';
import { Icon } from '@/components/ui/icon';
import { Text } from '@/components/ui/text';
import { HStack } from '@/components/ui/hstack';
import { useTypewriter } from '@/hooks/useTypewriter';
import { useThemeVariant } from '@/theme/ThemeContext';

export type AffirmationDisplayProps = {
  affirmation: string;
  className?: string;
};

export function AffirmationDisplay({ affirmation, className = "" }: AffirmationDisplayProps) {
  const animatedAffirmation = useTypewriter(affirmation, 30);
  const { themeId } = useThemeVariant();
  const isClassic = themeId === 'classic'

  return (
    <Box className={`${isClassic ? 'bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950 dark:to-indigo-950' : 'bg-background-200 dark:bg-background-700 border border-border-300 dark:border-border-700'} p-4 rounded-lg ${className}`}>
      <HStack className="items-center space-x-3">
        <Icon 
          as={Sparkles}
          size="md"
          className={isClassic ? 'text-blue-600 dark:text-blue-400' : 'text-primary-700 dark:text-primary-400'}
        />
        <Text className={`text-base ${isClassic ? 'text-typography-800 dark:text-gray-200' : 'text-typography-900 dark:text-white'} flex-1`}>
          {animatedAffirmation}
        </Text>
      </HStack>
    </Box>
  );
} 