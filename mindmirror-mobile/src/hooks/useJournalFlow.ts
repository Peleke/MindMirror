import { useState, useCallback } from 'react';
import { useMutation } from '@apollo/client';
import { useRouter } from 'expo-router';
import { CREATE_FREEFORM_JOURNAL_ENTRY } from '@/services/api/mutations';

interface UseJournalFlowReturn {
  submitEntry: (content: string) => Promise<void>;
  // This function is now the primary navigation method, so we expose it.
  transitionToChat: (initialMessage?: string) => void;
  isTransitioning: boolean;
  isSubmitting: boolean;
  error: string | null;
  clearError: () => void;
}

export function useJournalFlow(): UseJournalFlowReturn {
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const [createEntry, { loading: isSubmitting }] = useMutation(CREATE_FREEFORM_JOURNAL_ENTRY, {
    onError: (error) => {
      console.error('Journal entry error:', error);
      setError(`Failed to save journal entry: ${error.message}`);
    }
  });

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Define transitionToChat first so it can be used in submitEntry's useCallback dependency array.
  const transitionToChat = useCallback((initialMessage?: string) => {
    try {
      router.push({
        pathname: '/(app)/chat',
        params: { initialMessage: initialMessage || '' },
      });
    } catch (err) {
      console.error('Error transitioning to chat:', err);
      setError('Failed to open chat');
    } finally {
      setIsTransitioning(false);
    }
  }, [router]);

  const submitEntry = useCallback(async (content: string): Promise<void> => {
    try {
      setError(null);
      
      const result = await createEntry({
        variables: {
          input: { content }
        }
      });

      if (result.data) {
        setIsTransitioning(true);
        
        setTimeout(() => {
          transitionToChat(content);
        }, 500);
      } else {
        throw new Error("Submission did not return data.");
      }

    } catch (err: any) {
      console.error('Error submitting journal entry:', err);
      setError(`Submission failed: ${err.message}`);
      setIsTransitioning(false);
    }
  }, [createEntry, transitionToChat]);

  return {
    submitEntry,
    transitionToChat,
    isTransitioning,
    isSubmitting,
    error,
    clearError,
  };
} 