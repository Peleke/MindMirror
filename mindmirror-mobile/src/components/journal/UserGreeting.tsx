import React from 'react';
import { Text } from '@/components/ui/text';
import { VStack } from '@/components/ui/vstack';
import { Box } from '@/components/ui/box';

interface UserGreetingProps {
  userName?: string;
  lastEntryDate?: Date;
  className?: string;
}

export function UserGreeting({ 
  userName, 
  lastEntryDate, 
  className = "" 
}: UserGreetingProps) {
  const getGreeting = () => {
    return 'Welcome back';
  };

  const getLastEntryText = () => {
    if (!lastEntryDate) return "Ready to start your journaling journey?";
    
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - lastEntryDate.getTime());
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return "Welcome back! It's been less than a day since your last entry.";
    if (diffDays === 1) return "Welcome back! It's been a day since your last entry.";
    if (diffDays < 7) return `Welcome back! It's been ${diffDays} days since your last entry.`;
    return "Welcome back! It's been a while since your last entry.";
  };

  return (
    <VStack className={`space-y-2 ${className}`}>
      <Text className="text-2xl font-semibold text-typography-900 dark:text-white">
        {getGreeting()}{userName ? `, ${userName}` : ''}.
      </Text>
      <Text className="text-base text-typography-600 dark:text-gray-300 leading-6">
        {getLastEntryText()}
      </Text>
    </VStack>
  );
} 