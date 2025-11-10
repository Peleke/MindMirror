import React from 'react';
import { VStack } from '@/components/ui/vstack';
import { HStack } from '@/components/ui/hstack';
import { Text } from '@/components/ui/text';
import { Button, ButtonText } from '@/components/ui/button';
import { Pressable } from '@/components/ui/pressable';
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
  movementName: string;
  sets: SetDraft[];
  metricUnit: 'iterative' | 'temporal' | 'breath' | 'other';
  onSetChange: (setIndex: number, field: keyof SetDraft, value: string | number) => void;
  onCopyLastSet: () => void;
  onRemoveMovement?: () => void;
  onViewDetails?: () => void;
  className?: string;
}

export const SetEditorCard: React.FC<SetEditorCardProps> = ({
  movementName,
  sets,
  metricUnit,
  onSetChange,
  onCopyLastSet,
  onRemoveMovement,
  onViewDetails,
  className,
}) => {
  return (
    <VStack
      className={`rounded-xl bg-background-50 dark:bg-background-900 p-4 border border-outline-200 dark:border-outline-700 ${className || ''}`}
      space="md"
    >
      {/* Movement Header */}
      <HStack className="justify-between items-center">
        <Pressable onPress={onViewDetails}>
          <Text className="text-lg font-semibold text-typography-900 dark:text-white">
            {movementName}
          </Text>
        </Pressable>
        {onRemoveMovement && (
          <Pressable
            onPress={onRemoveMovement}
            className="px-3 py-1.5 rounded-md border border-red-300 dark:border-red-700 bg-white dark:bg-background-0"
          >
            <Text className="text-red-700 dark:text-red-300 font-semibold">Remove</Text>
          </Pressable>
        )}
      </HStack>

      {/* Column Headers */}
      <HStack className="px-2 pb-2 border-b border-outline-200 dark:border-outline-700">
        <Text className="w-[12%] text-xs font-bold text-typography-700 dark:text-typography-300">
          SET
        </Text>
        <Text className="w-[30%] text-xs font-bold text-typography-700 dark:text-typography-300">
          LOAD
        </Text>
        <Text className="w-[28%] text-xs font-bold text-typography-700 dark:text-typography-300">
          {metricUnit === 'iterative' ? 'REPS' : 'DUR'}
        </Text>
        <Text className="w-[30%] text-xs font-bold text-typography-700 dark:text-typography-300">
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
            onUpdate={(updates) => {
              Object.entries(updates).forEach(([field, value]) => {
                onSetChange(index, field as keyof SetDraft, value as any);
              });
            }}
            onDelete={() => {}}
            canDelete={false}
          />
        ))}
      </VStack>

      {/* Action Button */}
      <Button
        variant="outline"
        size="sm"
        onPress={onCopyLastSet}
        className="mt-2"
        disabled={sets.length === 0}
      >
        <ButtonText>📋 Copy Last Set</ButtonText>
      </Button>
    </VStack>
  );
};

SetEditorCard.displayName = 'SetEditorCard';
