import React from 'react';
import { VStack } from '@/components/ui/vstack';
import { HStack } from '@/components/ui/hstack';
import { Text } from '@/components/ui/text';
import { Pressable } from '@/components/ui/pressable';
import { Button, ButtonText } from '@/components/ui/button';
import { ChevronDown, ChevronRight } from 'lucide-react-native';
import { Icon } from '@/components/ui/icon';
import Animated, { FadeIn, FadeOut } from 'react-native-reanimated';

export interface CollapsibleBlockSectionProps {
  blockType: 'warmup' | 'workout' | 'cooldown';
  title: string;
  exerciseCount: number;
  totalSets: number;
  isCollapsed?: boolean;
  onToggleCollapse: () => void;
  onAddExercise: () => void;
  children: React.ReactNode;
  className?: string;
}

const AnimatedVStack = Animated.createAnimatedComponent(VStack);

export const CollapsibleBlockSection: React.FC<CollapsibleBlockSectionProps> = ({
  blockType,
  title,
  exerciseCount,
  totalSets,
  isCollapsed = false,
  onToggleCollapse,
  onAddExercise,
  children,
  className,
}) => {
  // Accent colors per block type
  const accentColorClass = {
    warmup: 'border-l-4 border-amber-400',
    workout: 'border-l-4 border-blue-500',
    cooldown: 'border-l-4 border-green-400',
  }[blockType];

  return (
    <VStack
      className={`rounded-xl bg-background-50 dark:bg-background-900 ${accentColorClass} ${className || ''}`}
      space="none"
    >
      {/* Collapsible Header */}
      <Pressable
        onPress={onToggleCollapse}
        className="flex-row items-center justify-between p-4 min-h-[44px]"
        accessibilityRole="button"
        accessibilityLabel={`${title} section, ${exerciseCount} exercises, ${totalSets} sets, ${isCollapsed ? 'collapsed' : 'expanded'}`}
        accessibilityHint="Double tap to toggle"
      >
        <HStack space="sm" className="items-center">
          <Icon
            as={isCollapsed ? ChevronRight : ChevronDown}
            size={20}
            className="text-typography-700 dark:text-typography-300"
          />
          <Text className="text-base font-semibold text-typography-900 dark:text-typography-100">
            {title}
          </Text>
          <Text className="text-sm text-typography-500 dark:text-typography-400">
            ({exerciseCount} exercise{exerciseCount !== 1 ? 's' : ''}, {totalSets} set{totalSets !== 1 ? 's' : ''})
          </Text>
        </HStack>
      </Pressable>

      {/* Collapsible Content */}
      {!isCollapsed && (
        <AnimatedVStack
          entering={FadeIn.duration(200)}
          exiting={FadeOut.duration(200)}
          className="px-4 pb-4"
          space="md"
        >
          {children}

          {/* Add Movement Button */}
          <Button
            onPress={onAddExercise}
            variant="outline"
            action="primary"
            size="md"
            className="min-h-[44px]"
          >
            <ButtonText>+ Add Movement</ButtonText>
          </Button>
        </AnimatedVStack>
      )}
    </VStack>
  );
};

CollapsibleBlockSection.displayName = 'CollapsibleBlockSection';
