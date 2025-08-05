import { HStack } from '@/components/ui/hstack';
import { Text } from '@/components/ui/text';
import { Button, ButtonText } from '@/components/ui/button';
import { Icon } from '@/components/ui/icon';
import { ChevronLeftIcon, ChevronRightIcon } from 'lucide-react-native';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  loading?: boolean;
}

export function Pagination({ 
  currentPage, 
  totalPages, 
  onPageChange, 
  loading = false 
}: PaginationProps) {
  if (totalPages <= 1) {
    return null; // Don't show pagination if only one page
  }

  const isFirstPage = currentPage === 1;
  const isLastPage = currentPage === totalPages;

  const handlePrevious = () => {
    if (!isFirstPage && !loading) {
      onPageChange(currentPage - 1);
    }
  };

  const handleNext = () => {
    if (!isLastPage && !loading) {
      onPageChange(currentPage + 1);
    }
  };

  return (
    <HStack className="items-center justify-center space-x-4 py-4 px-6">
      <Button
        onPress={handlePrevious}
        disabled={isFirstPage || loading}
        variant="outline"
        size="sm"
        className={`${isFirstPage || loading ? 'opacity-50' : ''} border-border-300`}
      >
        <Icon 
          as={ChevronLeftIcon} 
          size="sm" 
          className={`mr-1 ${isFirstPage || loading ? 'text-gray-400' : 'text-primary-600'}`} 
        />
        <ButtonText className={isFirstPage || loading ? 'text-gray-400' : 'text-primary-600'}>
          Previous
        </ButtonText>
      </Button>

      <Text className="text-sm text-typography-600 dark:text-gray-300 min-w-[100px] text-center">
        {loading ? 'Loading...' : `Page ${currentPage} of ${totalPages}`}
      </Text>

      <Button
        onPress={handleNext}
        disabled={isLastPage || loading}
        variant="outline"
        size="sm"
        className={`${isLastPage || loading ? 'opacity-50' : ''} border-border-300`}
      >
        <ButtonText className={isLastPage || loading ? 'text-gray-400' : 'text-primary-600'}>
          Next
        </ButtonText>
        <Icon 
          as={ChevronRightIcon} 
          size="sm" 
          className={`ml-1 ${isLastPage || loading ? 'text-gray-400' : 'text-primary-600'}`} 
        />
      </Button>
    </HStack>
  );
}
