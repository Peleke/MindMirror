import { renderHook, act } from '@testing-library/react-native';
import { useJournalFlow } from '../useJournalFlow';

// Mock the Apollo useMutation hook
const mockCreateEntry = jest.fn();
// We need a more complete mock for @apollo/client
jest.mock('@apollo/client', () => ({
  ...jest.requireActual('@apollo/client'), // Import and retain default exports
  useMutation: () => [mockCreateEntry, { loading: false, error: null }], // Override useMutation
  gql: jest.fn((literals) => literals.join('')), // Add a mock for gql
}));

// Mock the expo-router useRouter hook
const mockRouterPush = jest.fn();
jest.mock('expo-router', () => ({
  useRouter: () => ({
    push: mockRouterPush,
  }),
}));

describe('useJournalFlow', () => {
  beforeEach(() => {
    // Clear mock history before each test
    mockCreateEntry.mockClear();
    mockRouterPush.mockClear();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should call createEntry mutation on submitEntry', async () => {
    mockCreateEntry.mockResolvedValue({ data: { id: '123' } });
    const { result } = renderHook(() => useJournalFlow());
    const testContent = 'This is a test journal entry.';

    await act(async () => {
      await result.current.submitEntry(testContent);
    });

    expect(mockCreateEntry).toHaveBeenCalledWith({
      variables: {
        input: { content: testContent },
      },
    });
  });

  it('should transition to chat when submitted with andChat: true', async () => {
    mockCreateEntry.mockResolvedValue({ data: { id: '123' } });
    const { result } = renderHook(() => useJournalFlow());
    const testContent = 'This message should trigger a chat.';

    await act(async () => {
      // Explicitly call with the andChat option
      await result.current.submitEntry(testContent, { andChat: true });
    });

    // Fast-forward past the setTimeout
    act(() => {
      jest.advanceTimersByTime(500);
    });

    expect(mockRouterPush).toHaveBeenCalledWith({
      pathname: '/(app)/chat',
      params: { initialMessage: testContent },
    });
  });

  it('should NOT transition to chat when submitted with andChat: false', async () => {
    mockCreateEntry.mockResolvedValue({ data: { id: '123' } });
    const { result } = renderHook(() => useJournalFlow());
    const testContent = 'This message should only be saved.';

    await act(async () => {
      // Explicitly call with andChat: false
      await result.current.submitEntry(testContent, { andChat: false });
    });

    act(() => {
        jest.advanceTimersByTime(500);
    });

    expect(mockRouterPush).not.toHaveBeenCalled();
  });

  it('should NOT transition to chat when andChat option is omitted', async () => {
    mockCreateEntry.mockResolvedValue({ data: { id: '123' } });
    const { result } = renderHook(() => useJournalFlow());
    const testContent = 'This message should also only be saved.';

    await act(async () => {
      // Omit the options parameter entirely to test the default
      await result.current.submitEntry(testContent);
    });

    act(() => {
        jest.advanceTimersByTime(500);
    });

    expect(mockRouterPush).not.toHaveBeenCalled();
  });

  it('should not transition to chat if submission fails, even if andChat is true', async () => {
    mockCreateEntry.mockRejectedValue(new Error('Submission failed'));
    const { result } = renderHook(() => useJournalFlow());
    const testContent = 'This submission will fail.';

    await act(async () => {
      await result.current.submitEntry(testContent, { andChat: true });
    });

    act(() => {
        jest.advanceTimersByTime(500);
    });

    expect(mockRouterPush).not.toHaveBeenCalled();
    expect(result.current.isTransitioning).toBe(false);
  });

  it('should call router.push directly when transitionToChat is used', () => {
    const { result } = renderHook(() => useJournalFlow());
    const testMessage = 'Direct transition.';

    act(() => {
      result.current.transitionToChat(testMessage);
    });

    expect(mockRouterPush).toHaveBeenCalledWith({
      pathname: '/(app)/chat',
      params: { initialMessage: testMessage },
    });
  });
}); 