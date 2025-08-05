import { useQuery } from '@apollo/client';
import { JOURNAL_ENTRY_EXISTS_TODAY } from '@/services/api/queries';

export function useJournalStatus() {
  const { data: gratitudeData, loading: gratitudeLoading, error: gratitudeError } = useQuery(JOURNAL_ENTRY_EXISTS_TODAY, {
    variables: { entryType: 'GRATITUDE' },
    fetchPolicy: 'cache-and-network',
    notifyOnNetworkStatusChange: true,
  });

  const { data: reflectionData, loading: reflectionLoading, error: reflectionError } = useQuery(JOURNAL_ENTRY_EXISTS_TODAY, {
    variables: { entryType: 'REFLECTION' },
    fetchPolicy: 'cache-and-network', 
    notifyOnNetworkStatusChange: true,
  });

  return {
    hasCompletedGratitude: gratitudeData?.journalEntryExistsToday || false,
    hasCompletedReflection: reflectionData?.journalEntryExistsToday || false,
    isLoading: gratitudeLoading || reflectionLoading,
    error: gratitudeError || reflectionError,
  };
} 