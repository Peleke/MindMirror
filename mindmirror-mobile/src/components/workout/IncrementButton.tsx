import React from 'react';
import { Pressable } from '@/components/ui/pressable';
import { Icon } from '@/components/ui/icon';
import { Plus, Minus } from 'lucide-react-native';
import * as Haptics from 'expo-haptics';

export interface IncrementButtonProps {
  direction: 'up' | 'down';
  onPress: () => void;
  disabled?: boolean;
  size?: 'sm' | 'md';
  className?: string;
}

export const IncrementButton: React.FC<IncrementButtonProps> = ({
  direction,
  onPress,
  disabled = false,
  size = 'md',
  className,
}) => {
  const handlePress = async () => {
    if (!disabled) {
      // Trigger haptic feedback
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      onPress();
    }
  };

  const sizeClass = {
    sm: 'min-w-[40px] min-h-[40px]',
    md: 'min-w-[44px] min-h-[44px]',
  }[size];

  const iconSize = {
    sm: 16,
    md: 20,
  }[size];

  return (
    <Pressable
      onPress={handlePress}
      disabled={disabled}
      className={`
        ${sizeClass}
        rounded-full
        bg-background-100 dark:bg-background-800
        items-center justify-center
        data-[hover=true]:bg-background-200 dark:data-[hover=true]:bg-background-700
        data-[active=true]:bg-background-300 dark:data-[active=true]:bg-background-600
        data-[disabled=true]:opacity-50
        ${className || ''}
      `}
      accessibilityRole="button"
      accessibilityLabel={`${direction === 'up' ? 'Increase' : 'Decrease'} value`}
    >
      <Icon
        as={direction === 'up' ? Plus : Minus}
        size={iconSize}
        className="text-typography-700 dark:text-typography-300"
      />
    </Pressable>
  );
};

IncrementButton.displayName = 'IncrementButton';
