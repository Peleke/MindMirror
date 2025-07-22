import { useState, useCallback } from 'react';
import { useMutation } from '@apollo/client';
import { useRouter } from 'expo-router';
import { CREATE_FREEFORM_JOURNAL_ENTRY } from '@/services/api/mutations';

interface SubmitOptions {
  andChat?: boolean;
}

interface UseJournalFlowReturn {
  // Update signature to accept options
  submitEntry: (content: string, options?: SubmitOptions) => Promise<{ success: boolean }>;
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

  // This function now handles both "Save" and "Save and Chat" logic.
  const submitEntry = useCallback(async (
    content: string,
    options: SubmitOptions = { andChat: false }
  ): Promise<{ success: boolean }> => {
    try {
      setError(null);
      
      const result = await createEntry({
        variables: {
          input: { content }
        }
      });

      if (result.data && options.andChat) {
        // Only transition if the 'andChat' option is true.
        setIsTransitioning(true);
        
        setTimeout(() => {
          transitionToChat(content);
        }, 500);
      } else if (!result.data) {
        throw new Error("Submission did not return data.");
      }
      
      return { success: !!result.data };

    } catch (err: any) {
      console.error('Error submitting journal entry:', err);
      setError(`Submission failed: ${err.message}`);
      setIsTransitioning(false); // Ensure transition is reset on failure
      return { success: false };
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