import { VStack } from '@/components/ui/vstack';
import { Text } from '@/components/ui/text';
import { Box } from '@/components/ui/box';

interface ReadOnlyFieldProps {
  label: string;
  value: string;
  numberOfLines?: number;
  style?: any;
}

export function ReadOnlyField({ 
  label, 
  value, 
  numberOfLines = 3,
  style 
}: ReadOnlyFieldProps) {
  return (
    <VStack space="xs">
      <Text className="text-sm font-medium text-typography-700 dark:text-gray-300">
        {label}
      </Text>
      <Box className="bg-white dark:bg-gray-100 rounded-lg border border-border-200 p-3">
        <Text 
          className="text-typography-900 dark:text-gray-800"
          style={style}
        >
          {value || 'No content'}
        </Text>
      </Box>
    </VStack>
  );
} 