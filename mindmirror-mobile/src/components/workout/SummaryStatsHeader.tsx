import React from 'react';
import { HStack } from '@/components/ui/hstack';
import { VStack } from '@/components/ui/vstack';
import { Text } from '@/components/ui/text';
import { Divider } from '@/components/ui/divider';
import { Icon } from '@/components/ui/icon';
import { Clock, Dumbbell, TrendingUp } from 'lucide-react-native';

export interface SummaryStatsHeaderProps {
  totalExercises: number;
  totalSets: number;
  totalDuration: number; // seconds
  loading?: boolean;
  className?: string;
}

interface StatItemProps {
  icon: React.ComponentType;
  label?: string;
  value: string;
}

const StatItem: React.FC<StatItemProps> = ({ icon: IconComponent, label, value }) => (
  <HStack space="xs" className="items-center">
    <Icon as={IconComponent} size={16} className="text-primary-500" />
    {label && (
      <Text className="text-xs text-typography-500 dark:text-typography-400">
        {label}
      </Text>
    )}
    <Text className="text-sm font-semibold text-typography-900 dark:text-typography-100">
      {value}
    </Text>
  </HStack>
);

export const SummaryStatsHeader: React.FC<SummaryStatsHeaderProps> = ({
  totalExercises,
  totalSets,
  totalDuration,
  loading = false,
  className,
}) => {
  if (loading) {
    return (
      <HStack
        className={`bg-background-100 dark:bg-background-800 p-4 rounded-lg ${className || ''}`}
        space="md"
      >
        <Text className="text-sm text-typography-500">Loading stats...</Text>
      </HStack>
    );
  }

  // Format duration as MM:SS
  const minutes = Math.floor(totalDuration / 60);
  const seconds = totalDuration % 60;
  const durationDisplay = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

  return (
    <HStack
      className={`bg-background-100 dark:bg-background-800 p-4 rounded-lg ${className || ''}`}
      space="md"
    >
      {/* Estimated Duration */}
      <StatItem
        icon={Clock}
        label="Est"
        value={durationDisplay}
      />

      <Divider orientation="vertical" className="h-6" />

      {/* Exercise Count */}
      <StatItem
        icon={Dumbbell}
        value={`${totalExercises} exercise${totalExercises !== 1 ? 's' : ''}`}
      />

      <Divider orientation="vertical" className="h-6" />

      {/* Total Sets */}
      <StatItem
        icon={TrendingUp}
        value={`${totalSets} set${totalSets !== 1 ? 's' : ''}`}
      />
    </HStack>
  );
};

SummaryStatsHeader.displayName = 'SummaryStatsHeader';
