import { useQuery } from '@apollo/client';
import { JOURNAL_ENTRY_EXISTS_TODAY } from '@/services/api/queries';
import { useAuth } from '@/features/auth/context/AuthContext'

export function useJournalStatus() {
  const { session, loading: authLoading } = useAuth()
  const hasSession = !!session?.access_token

  const { data: gratitudeData, loading: gratitudeLoading, error: gratitudeError } = useQuery(JOURNAL_ENTRY_EXISTS_TODAY, {
    variables: { entryType: 'GRATITUDE' },
    fetchPolicy: 'cache-and-network',
    notifyOnNetworkStatusChange: true,
    skip: authLoading || !hasSession,
  });

  const { data: reflectionData, loading: reflectionLoading, error: reflectionError } = useQuery(JOURNAL_ENTRY_EXISTS_TODAY, {
    variables: { entryType: 'REFLECTION' },
    fetchPolicy: 'cache-and-network', 
    notifyOnNetworkStatusChange: true,
    skip: authLoading || !hasSession,
  });

  return {
    hasCompletedGratitude: gratitudeData?.journalEntryExistsToday || false,
    hasCompletedReflection: reflectionData?.journalEntryExistsToday || false,
    isLoading: authLoading || gratitudeLoading || reflectionLoading,
    error: gratitudeError || reflectionError,
  };
}