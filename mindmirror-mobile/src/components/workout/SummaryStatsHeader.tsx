import React from 'react';
import { HStack } from '@/components/ui/hstack';
import { VStack } from '@/components/ui/vstack';
import { Text } from '@/components/ui/text';
import { Divider } from '@/components/ui/divider';
import { Icon } from '@/components/ui/icon';
import { Clock, Dumbbell, TrendingUp } from 'lucide-react-native';

export interface SummaryStatsHeaderProps {
  exerciseCount: number;
  totalSets: number;
  estimatedDuration: number; // minutes
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
  exerciseCount,
  totalSets,
  estimatedDuration,
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

  return (
    <HStack
      className={`bg-background-100 dark:bg-background-800 p-4 rounded-lg ${className || ''}`}
      space="md"
    >
      {/* Estimated Duration */}
      <StatItem
        icon={Clock}
        label="Est"
        value={`${estimatedDuration}min`}
      />

      <Divider orientation="vertical" className="h-6" />

      {/* Exercise Count */}
      <StatItem
        icon={Dumbbell}
        value={`${exerciseCount} exercise${exerciseCount !== 1 ? 's' : ''}`}
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
