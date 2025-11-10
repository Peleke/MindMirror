import React from 'react';
import { VStack } from '@/components/ui/vstack';
import { Text } from '@/components/ui/text';
import { Button, ButtonText } from '@/components/ui/button';
import { Icon } from '@/components/ui/icon';
import { Dumbbell } from 'lucide-react-native';

export interface EmptyStateCardProps {
  title?: string;
  subtitle?: string;
  icon?: React.ReactNode;
  ctaLabel?: string;
  onCTAPress: () => void;
  variant?: 'template' | 'block';
  accentColor?: 'amber' | 'blue' | 'green';
  className?: string;
}

const defaultProps = {
  title: 'No exercises yet',
  subtitle: 'Get started by adding an exercise to your template.',
  ctaLabel: '+ Add Exercise',
  variant: 'template' as const,
};

export const EmptyStateCard: React.FC<EmptyStateCardProps> = ({
  title = defaultProps.title,
  subtitle = defaultProps.subtitle,
  icon,
  ctaLabel = defaultProps.ctaLabel,
  onCTAPress,
  variant = defaultProps.variant,
  accentColor,
  className,
}) => {
  const iconSize = variant === 'template' ? 60 : 40;

  // Determine accent border class based on accentColor
  const accentClass = accentColor
    ? {
        amber: 'border-l-4 border-amber-400',
        blue: 'border-l-4 border-blue-500',
        green: 'border-l-4 border-green-400',
      }[accentColor]
    : '';

  return (
    <VStack
      className={`items-center py-12 px-6 rounded-xl bg-background-50 dark:bg-background-900 ${accentClass} ${className || ''}`}
      space="md"
    >
      {/* Icon */}
      {icon || (
        <Icon
          as={Dumbbell}
          size={iconSize}
          className="text-gray-400"
        />
      )}

      {/* Text Content */}
      <VStack space="xs" className="items-center">
        <Text className="text-lg font-semibold text-center text-typography-900 dark:text-typography-100">
          {title}
        </Text>
        <Text className="text-sm text-center text-typography-500 dark:text-typography-400">
          {subtitle}
        </Text>
      </VStack>

      {/* CTA Button */}
      <Button
        onPress={onCTAPress}
        size="lg"
        action="primary"
        className="min-h-[44px] px-6"
      >
        <ButtonText>{ctaLabel}</ButtonText>
      </Button>
    </VStack>
  );
};

EmptyStateCard.displayName = 'EmptyStateCard';
