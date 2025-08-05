import { Box } from '@/components/ui/box';
import { CheckCircle } from 'lucide-react-native';
import { Icon } from '@/components/ui/icon';
import { Text } from '@/components/ui/text';
import { HStack } from '@/components/ui/hstack';

type CompletedJournalCardProps = {
  journalType: 'Gratitude' | 'Reflection';
  className?: string;
};

export function CompletedJournalCard({ journalType, className = "" }: CompletedJournalCardProps) {
  const message = journalType === 'Gratitude' 
    ? "You've completed your gratitude entry for today. Well done!" 
    : "You've completed your reflection for today. See you tomorrow!";

  return (
    <Box className={`flex-1 p-4 rounded-lg bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800 ${className}`}>
      <HStack className="items-center space-x-3">
        <Icon as={CheckCircle} size="lg" className="text-green-600 dark:text-green-400" />
        <Text className="text-sm font-medium text-green-800 dark:text-green-200 flex-1">
          {message}
        </Text>
      </HStack>
    </Box>
  );
} 