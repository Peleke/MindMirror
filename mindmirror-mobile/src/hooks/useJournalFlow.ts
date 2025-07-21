import { useState, useCallback } from 'react';
import { useMutation } from '@apollo/client';
import { useRouter } from 'expo-router';
import { CREATE_FREEFORM_JOURNAL_ENTRY } from '@/services/api/mutations';
import { JournalType } from '@/components/journal';

interface UseJournalFlowReturn {
  submitEntry: (content: string) => Promise<void>;
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

  // Use the existing freeform journal entry mutation
  const [createEntry, { loading: isSubmitting }] = useMutation(CREATE_FREEFORM_JOURNAL_ENTRY, {
    onError: (error) => {
      console.error('Journal entry error:', error);
      setError(`Failed to save journal entry: ${error.message}`);
    }
  });

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const submitEntry = useCallback(async (content: string): Promise<void> => {
    try {
      setError(null);
      
      // Use freeform mutation for the journal entry
      await createEntry({
        variables: {
          input: { content }
        }
      });

      // Start transition to chat
      setIsTransitioning(true);
      
      // Small delay to show transition animation
      setTimeout(() => {
        transitionToChat(content);
      }, 500);

    } catch (err: any) {
      console.error('Error submitting journal entry:', err);
      setError(`Submission failed: ${err.message}`);
    }
  }, [createEntry]);

  const transitionToChat = useCallback((initialMessage?: string) => {
    try {
      // Navigate to chat with initial message
      if (initialMessage) {
        // TODO: Pass initial message to chat screen
        // For now, we'll need to implement this in the chat screen
        router.push('/(app)/chat' as any);
      } else {
        router.push('/(app)/chat' as any);
      }
    } catch (err) {
      console.error('Error transitioning to chat:', err);
      setError('Failed to open chat');
    } finally {
      setIsTransitioning(false);
    }
  }, [router]);

  return {
    submitEntry,
    transitionToChat,
    isTransitioning,
    isSubmitting,
    error,
    clearError,
  };
} 