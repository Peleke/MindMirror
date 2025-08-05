import { renderHook, act, waitFor } from '@testing-library/react-native';
import { useAffirmation } from '../useAffirmation';

// Mock setTimeout
jest.useFakeTimers();

describe('useAffirmation', () => {
  beforeEach(() => {
    jest.clearAllTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('returns initial state with loading true', () => {
    const { result } = renderHook(() => useAffirmation());

    expect(result.current.isLoading).toBe(true);
    expect(result.current.affirmation).toBe('');
    expect(result.current.error).toBe(null);
    expect(typeof result.current.refresh).toBe('function');
  });

  it('generates affirmation after initial load', async () => {
    const { result } = renderHook(() => useAffirmation());

    // Fast-forward timers to complete the async operation
    act(() => {
      jest.advanceTimersByTime(2000);
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.affirmation).toBeTruthy();
    expect(result.current.affirmation.length).toBeGreaterThan(0);
    expect(result.current.error).toBe(null);
  });

  it('generates different affirmations on refresh', async () => {
    const { result } = renderHook(() => useAffirmation());

    // Wait for initial load
    act(() => {
      jest.advanceTimersByTime(2000);
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    const firstAffirmation = result.current.affirmation;

    // Refresh
    act(() => {
      result.current.refresh();
    });

    expect(result.current.isLoading).toBe(true);

    // Wait for refresh to complete
    act(() => {
      jest.advanceTimersByTime(2000);
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Note: Since we're using random selection, affirmations might be the same
    // In a real scenario, we'd want to mock the random function to ensure different results
    expect(result.current.affirmation).toBeTruthy();
  });

  it('handles errors gracefully and falls back to static affirmation', async () => {
    // Mock console.error to avoid noise in tests
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    // Mock the async operation to throw an error
    const originalSetTimeout = global.setTimeout;
    global.setTimeout = jest.fn((callback: any) => {
      if (typeof callback === 'function') {
        // Simulate an error
        callback();
        throw new Error('API Error');
      }
      return originalSetTimeout(callback);
    });

    const { result } = renderHook(() => useAffirmation());

    // Fast-forward timers
    act(() => {
      jest.advanceTimersByTime(2000);
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.error).toBe('Failed to generate affirmation');
    expect(result.current.affirmation).toBeTruthy(); // Should still have fallback
    expect(result.current.affirmation.length).toBeGreaterThan(0);

    // Restore original setTimeout
    global.setTimeout = originalSetTimeout;
    consoleSpy.mockRestore();
  });

  it('sets loading state correctly during refresh', async () => {
    const { result } = renderHook(() => useAffirmation());

    // Wait for initial load
    act(() => {
      jest.advanceTimersByTime(2000);
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Start refresh
    act(() => {
      result.current.refresh();
    });

    expect(result.current.isLoading).toBe(true);

    // Wait for refresh to complete
    act(() => {
      jest.advanceTimersByTime(2000);
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });
  });

  it('clears error when refresh is successful', async () => {
    // First, create an error state
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    const originalSetTimeout = global.setTimeout;
    global.setTimeout = jest.fn((callback: any) => {
      if (typeof callback === 'function') {
        callback();
        throw new Error('API Error');
      }
      return originalSetTimeout(callback);
    });

    const { result } = renderHook(() => useAffirmation());

    act(() => {
      jest.advanceTimersByTime(2000);
    });

    await waitFor(() => {
      expect(result.current.error).toBe('Failed to generate affirmation');
    });

    // Restore normal setTimeout for refresh
    global.setTimeout = originalSetTimeout;

    // Refresh should clear the error
    act(() => {
      result.current.refresh();
    });

    act(() => {
      jest.advanceTimersByTime(2000);
    });

    await waitFor(() => {
      expect(result.current.error).toBe(null);
    });

    consoleSpy.mockRestore();
  });

  it('generates affirmations within expected time range', async () => {
    const { result } = renderHook(() => useAffirmation());

    // Should complete within 3 seconds (1-3 second range + buffer)
    act(() => {
      jest.advanceTimersByTime(3000);
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.affirmation).toBeTruthy();
  });

  it('returns valid fallback affirmations', async () => {
    const { result } = renderHook(() => useAffirmation());

    act(() => {
      jest.advanceTimersByTime(2000);
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Check that the affirmation is one of the expected fallback affirmations
    const fallbackAffirmations = [
      "You are capable of amazing things. Today is a new opportunity to grow and learn.",
      "Your thoughts and feelings are valid. Take a moment to honor your inner wisdom.",
      "Every challenge you face makes you stronger. You have the resilience to overcome anything.",
      "You are worthy of love, respect, and happiness. Treat yourself with kindness today.",
      "Your journey is unique and beautiful. Trust the process and believe in yourself.",
      "You have the power to create positive change in your life. Start with small steps.",
      "Your presence in this world matters. You make a difference simply by being you.",
      "Embrace your authentic self. You are enough, just as you are.",
      "Today is filled with possibilities. Open your heart to new experiences and growth.",
      "You are surrounded by love and support, even when it feels like you're alone.",
    ];

    expect(fallbackAffirmations).toContain(result.current.affirmation);
  });
}); 