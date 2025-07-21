import { renderHook, act, waitFor } from '@testing-library/react-native';
import { useJournalFlow } from '../useJournalFlow';
import { JournalType } from '@/components/journal';

// Mock Apollo Client
jest.mock('@apollo/client', () => ({
  useMutation: jest.fn(),
}));

// Mock expo-router
jest.mock('expo-router', () => ({
  useRouter: jest.fn(() => ({
    push: jest.fn(),
  })),
}));

// Mock the mutation
const mockCreateEntry = jest.fn();
const mockUseMutation = require('@apollo/client').useMutation;

describe('useJournalFlow', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockUseMutation.mockReturnValue([
      mockCreateEntry,
      { loading: false }
    ]);
  });

  it('returns initial state', () => {
    const { result } = renderHook(() => useJournalFlow());

    expect(result.current.isTransitioning).toBe(false);
    expect(result.current.isSubmitting).toBe(false);
    expect(result.current.error).toBe(null);
    expect(typeof result.current.submitEntry).toBe('function');
    expect(typeof result.current.transitionToChat).toBe('function');
    expect(typeof result.current.clearError).toBe('function');
  });

  it('submits entry successfully and transitions to chat', async () => {
    mockCreateEntry.mockResolvedValue({ data: { createFreeformJournalEntry: { id: '123' } } });

    const { result } = renderHook(() => useJournalFlow());

    await act(async () => {
      await result.current.submitEntry('Test journal content');
    });

    expect(mockCreateEntry).toHaveBeenCalledWith({
      variables: {
        input: { content: 'Test journal content' }
      }
    });

    // Should start transition
    expect(result.current.isTransitioning).toBe(true);
  });

  it('handles submission errors', async () => {
    const mockError = new Error('GraphQL Error: Something went wrong');
    mockCreateEntry.mockRejectedValue(mockError);

    const { result } = renderHook(() => useJournalFlow());

    await act(async () => {
      await result.current.submitEntry('Test content');
    });

    expect(result.current.error).toBe('Submission failed: GraphQL Error: Something went wrong');
    expect(result.current.isTransitioning).toBe(false);
  });

  it('handles GraphQL errors from mutation', async () => {
    const mockError = { message: 'GraphQL Error: Network error' };
    mockUseMutation.mockReturnValue([
      mockCreateEntry,
      { 
        loading: false,
        error: mockError
      }
    ]);

    const { result } = renderHook(() => useJournalFlow());

    await act(async () => {
      await result.current.submitEntry('Test content');
    });

    expect(result.current.error).toBe('Failed to save journal entry: GraphQL Error: Network error');
  });

  it('clears error when clearError is called', () => {
    const { result } = renderHook(() => useJournalFlow());

    // Set an error
    act(() => {
      result.current.clearError();
    });

    expect(result.current.error).toBe(null);
  });

  it('transitions to chat successfully', () => {
    const mockPush = jest.fn();
    const mockUseRouter = require('expo-router').useRouter;
    mockUseRouter.mockReturnValue({ push: mockPush });

    const { result } = renderHook(() => useJournalFlow());

    act(() => {
      result.current.transitionToChat('Initial message');
    });

    expect(mockPush).toHaveBeenCalledWith('/(app)/chat');
    expect(result.current.isTransitioning).toBe(false);
  });

  it('handles transition errors', () => {
    const mockPush = jest.fn().mockImplementation(() => {
      throw new Error('Navigation error');
    });
    const mockUseRouter = require('expo-router').useRouter;
    mockUseRouter.mockReturnValue({ push: mockPush });

    const { result } = renderHook(() => useJournalFlow());

    act(() => {
      result.current.transitionToChat();
    });

    expect(result.current.error).toBe('Failed to open chat');
    expect(result.current.isTransitioning).toBe(false);
  });

  it('shows loading state during submission', async () => {
    mockUseMutation.mockReturnValue([
      mockCreateEntry,
      { loading: true }
    ]);

    const { result } = renderHook(() => useJournalFlow());

    expect(result.current.isSubmitting).toBe(true);
  });

  it('trims whitespace from content before submission', async () => {
    mockCreateEntry.mockResolvedValue({ data: { createFreeformJournalEntry: { id: '123' } } });

    const { result } = renderHook(() => useJournalFlow());

    await act(async () => {
      await result.current.submitEntry('   Test content with whitespace   ');
    });

    expect(mockCreateEntry).toHaveBeenCalledWith({
      variables: {
        input: { content: 'Test content with whitespace' }
      }
    });
  });

  it('handles empty content gracefully', async () => {
    const { result } = renderHook(() => useJournalFlow());

    await act(async () => {
      await result.current.submitEntry('   ');
    });

    expect(mockCreateEntry).toHaveBeenCalledWith({
      variables: {
        input: { content: '' }
      }
    });
  });

  it('maintains state between submissions', async () => {
    mockCreateEntry.mockResolvedValue({ data: { createFreeformJournalEntry: { id: '123' } } });

    const { result } = renderHook(() => useJournalFlow());

    // First submission
    await act(async () => {
      await result.current.submitEntry('First content');
    });

    expect(result.current.isTransitioning).toBe(true);

    // Reset transition state for testing
    act(() => {
      // Simulate transition completion
      result.current.transitionToChat();
    });

    // Second submission
    await act(async () => {
      await result.current.submitEntry('Second content');
    });

    expect(mockCreateEntry).toHaveBeenCalledTimes(2);
    expect(result.current.isTransitioning).toBe(true);
  });

  it('handles rapid successive calls', async () => {
    mockCreateEntry.mockResolvedValue({ data: { createFreeformJournalEntry: { id: '123' } } });

    const { result } = renderHook(() => useJournalFlow());

    // Make multiple rapid calls
    await act(async () => {
      await Promise.all([
        result.current.submitEntry('Content 1'),
        result.current.submitEntry('Content 2'),
        result.current.submitEntry('Content 3'),
      ]);
    });

    // Should handle all calls (though in practice, we'd want to prevent multiple submissions)
    expect(mockCreateEntry).toHaveBeenCalledTimes(3);
  });
}); 