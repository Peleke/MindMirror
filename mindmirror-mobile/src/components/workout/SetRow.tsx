import React from 'react';
import { HStack } from '@/components/ui/hstack';
import { VStack } from '@/components/ui/vstack';
import { Text } from '@/components/ui/text';
import { Input, InputField } from '@/components/ui/input';
import { Pressable } from '@/components/ui/pressable';
import { Icon } from '@/components/ui/icon';
import { Trash2 } from 'lucide-react-native';
import { IncrementButton } from './IncrementButton';

type SetDraft = {
  position: number;
  reps?: number;
  duration?: number;
  loadValue?: number;
  loadUnit?: string;
  restDuration?: number;
};

export interface SetRowProps {
  set: SetDraft;
  setNumber: number;
  isWarmup?: boolean;
  metricUnit: 'iterative' | 'temporal' | 'breath' | 'other';
  onUpdate: (updates: Partial<SetDraft>) => void;
  onDelete: () => void;
  canDelete: boolean;
  className?: string;
}

export const SetRow: React.FC<SetRowProps> = ({
  set,
  setNumber,
  isWarmup = false,
  metricUnit,
  onUpdate,
  onDelete,
  canDelete,
  className,
}) => {
  const isIterative = metricUnit === 'iterative';
  const loadIncrement = set.loadUnit === 'kg' ? 2.5 : 5;

  const handleIncrementLoad = () => {
    const newValue = Math.min((set.loadValue || 0) + loadIncrement, 1000);
    onUpdate({ loadValue: newValue });
  };

  const handleDecrementLoad = () => {
    const newValue = Math.max((set.loadValue || 0) - loadIncrement, 0);
    onUpdate({ loadValue: newValue });
  };

  const handleIncrementReps = () => {
    const current = isIterative ? set.reps || 0 : set.duration || 0;
    const newValue = Math.min(current + 1, 100);
    onUpdate(isIterative ? { reps: newValue } : { duration: newValue });
  };

  const handleDecrementReps = () => {
    const current = isIterative ? set.reps || 0 : set.duration || 0;
    const newValue = Math.max(current - 1, 1);
    onUpdate(isIterative ? { reps: newValue } : { duration: newValue });
  };

  const handleIncrementRest = () => {
    const newValue = Math.min((set.restDuration || 0) + 15, 600);
    onUpdate({ restDuration: newValue });
  };

  const handleDecrementRest = () => {
    const newValue = Math.max((set.restDuration || 0) - 15, 0);
    onUpdate({ restDuration: newValue });
  };

  return (
    <HStack
      className={`items-center gap-2 py-2 ${className || ''}`}
      space="sm"
    >
      {/* Set Number Badge */}
      <VStack className="w-[15%] items-center justify-center">
        {isWarmup ? (
          <Text className="text-sm font-bold text-amber-500">W</Text>
        ) : (
          <Text className="text-sm font-semibold text-typography-700 dark:text-typography-300">
            {setNumber}
          </Text>
        )}
      </VStack>

      {/* Load Input with Increment Buttons (35%) */}
      <HStack className="w-[35%] items-center gap-1">
        <Input
          variant="outline"
          size="sm"
          className="flex-1 min-h-[44px]"
        >
          <InputField
            value={set.loadValue?.toString() || '0'}
            onChangeText={(text) => {
              const num = parseFloat(text);
              if (!isNaN(num)) onUpdate({ loadValue: num });
            }}
            keyboardType="numeric"
            placeholder="0"
            className="text-center"
            testID={`set-${setNumber}-load`}
          />
        </Input>
        <Text className="text-xs text-typography-500 w-8">
          {set.loadUnit || 'lb'}
        </Text>
        <VStack space="xs">
          <IncrementButton
            direction="up"
            onPress={handleIncrementLoad}
            size="sm"
            disabled={(set.loadValue || 0) >= 1000}
            testID={`increment-load-up-${setNumber}`}
          />
          <IncrementButton
            direction="down"
            onPress={handleDecrementLoad}
            size="sm"
            disabled={(set.loadValue || 0) <= 0}
            testID={`increment-load-down-${setNumber}`}
          />
        </VStack>
      </HStack>

      {/* Reps/Duration Input with Increment Buttons (30%) */}
      <HStack className="w-[30%] items-center gap-1">
        <Input
          variant="outline"
          size="sm"
          className="flex-1 min-h-[44px]"
        >
          <InputField
            value={
              isIterative
                ? set.reps?.toString() || '0'
                : set.duration?.toString() || '0'
            }
            onChangeText={(text) => {
              const num = parseInt(text, 10);
              if (!isNaN(num)) {
                onUpdate(isIterative ? { reps: num } : { duration: num });
              }
            }}
            keyboardType="numeric"
            placeholder="0"
            className="text-center"
            testID={`set-${setNumber}-reps`}
          />
        </Input>
        <VStack space="xs">
          <IncrementButton
            direction="up"
            onPress={handleIncrementReps}
            size="sm"
            disabled={
              (isIterative ? set.reps || 0 : set.duration || 0) >= 100
            }
            testID={`increment-reps-up-${setNumber}`}
          />
          <IncrementButton
            direction="down"
            onPress={handleDecrementReps}
            size="sm"
            disabled={(isIterative ? set.reps || 0 : set.duration || 0) <= 1}
            testID={`increment-reps-down-${setNumber}`}
          />
        </VStack>
      </HStack>

      {/* Rest Duration (20%) */}
      <HStack className="w-[20%] items-center gap-1">
        <Text className="text-sm text-typography-700 dark:text-typography-300">
          {set.restDuration || 60}s
        </Text>
        <VStack space="xs">
          <IncrementButton
            direction="up"
            onPress={handleIncrementRest}
            size="sm"
            disabled={(set.restDuration || 0) >= 600}
          />
          <IncrementButton
            direction="down"
            onPress={handleDecrementRest}
            size="sm"
            disabled={(set.restDuration || 0) <= 0}
          />
        </VStack>
      </HStack>

      {/* Delete Button (if allowed) */}
      {canDelete && (
        <Pressable
          onPress={onDelete}
          className="ml-2 p-2"
          accessibilityLabel="Delete set"
          testID={`delete-set-${setNumber}`}
        >
          <Icon
            as={Trash2}
            size={16}
            className="text-error-500"
          />
        </Pressable>
      )}
    </HStack>
  );
};

SetRow.displayName = 'SetRow';
