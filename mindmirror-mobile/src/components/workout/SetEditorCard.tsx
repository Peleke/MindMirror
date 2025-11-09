import React from 'react';
import { VStack } from '@/components/ui/vstack';
import { HStack } from '@/components/ui/hstack';
import { Text } from '@/components/ui/text';
import { Button, ButtonText } from '@/components/ui/button';
import { SetRow } from './SetRow';

type SetDraft = {
  position: number;
  reps?: number;
  duration?: number;
  loadValue?: number;
  loadUnit?: string;
  restDuration?: number;
};

export interface SetEditorCardProps {
  sets: SetDraft[];
  metricUnit: 'iterative' | 'temporal' | 'breath' | 'other';
  onUpdateSet: (index: number, updates: Partial<SetDraft>) => void;
  onAddSet: () => void;
  onDeleteSet: (index: number) => void;
  onCopyLastSet: () => void;
  className?: string;
}

export const SetEditorCard: React.FC<SetEditorCardProps> = ({
  sets,
  metricUnit,
  onUpdateSet,
  onAddSet,
  onDeleteSet,
  onCopyLastSet,
  className,
}) => {
  const canDelete = sets.length > 1;

  const handleUpdateSet = (index: number) => (updates: Partial<SetDraft>) => {
    onUpdateSet(index, updates);
  };

  const handleDeleteSet = (index: number) => () => {
    if (canDelete) {
      onDeleteSet(index);
    }
  };

  return (
    <VStack
      className={`rounded-xl bg-background-50 dark:bg-background-900 p-4 border border-outline-200 dark:border-outline-700 ${className || ''}`}
      space="sm"
    >
      {/* Column Headers */}
      <HStack className="px-2 pb-2 border-b border-outline-200 dark:border-outline-700">
        <Text className="w-[15%] text-xs font-bold text-typography-700 dark:text-typography-300">
          SET
        </Text>
        <Text className="w-[35%] text-xs font-bold text-typography-700 dark:text-typography-300">
          LOAD
        </Text>
        <Text className="w-[30%] text-xs font-bold text-typography-700 dark:text-typography-300">
          {metricUnit === 'iterative' ? 'REPS' : 'DUR'}
        </Text>
        <Text className="w-[20%] text-xs font-bold text-typography-700 dark:text-typography-300">
          REST
        </Text>
      </HStack>

      {/* Set Rows */}
      <VStack space="xs">
        {sets.map((set, index) => (
          <SetRow
            key={`set-${index}`}
            set={set}
            setNumber={index + 1}
            metricUnit={metricUnit}
            onUpdate={handleUpdateSet(index)}
            onDelete={handleDeleteSet(index)}
            canDelete={canDelete}
          />
        ))}
      </VStack>

      {/* Action Buttons */}
      <HStack className="gap-2 pt-2">
        <Button
          variant="outline"
          size="sm"
          onPress={onCopyLastSet}
          className="flex-1"
          disabled={sets.length === 0}
        >
          <ButtonText>📋 Copy Last Set</ButtonText>
        </Button>
        <Button
          variant="solid"
          action="primary"
          size="sm"
          onPress={onAddSet}
          className="flex-1"
        >
          <ButtonText>+ Add Set</ButtonText>
        </Button>
      </HStack>
    </VStack>
  );
};

SetEditorCard.displayName = 'SetEditorCard';
