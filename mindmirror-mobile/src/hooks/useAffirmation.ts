import { useState, useEffect } from 'react';

interface UseAffirmationReturn {
  affirmation: string;
  isLoading: boolean;
  error: string | null;
  refresh: () => void;
}

// Static fallback affirmations for when LLM is not available
const FALLBACK_AFFIRMATIONS = [
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

export function useAffirmation(): UseAffirmationReturn {
  const [affirmation, setAffirmation] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const getRandomAffirmation = (): string => {
    const randomIndex = Math.floor(Math.random() * FALLBACK_AFFIRMATIONS.length);
    return FALLBACK_AFFIRMATIONS[randomIndex];
  };

  const generateAffirmation = async (): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      // TODO: Replace with actual LLM API call when available
      // For now, simulate API call with delay
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
      
      // Use fallback for now
      const newAffirmation = getRandomAffirmation();
      setAffirmation(newAffirmation);
    } catch (err) {
      console.error('Error generating affirmation:', err);
      setError('Failed to generate affirmation');
      // Fallback to static affirmation
      setAffirmation(getRandomAffirmation());
    } finally {
      setIsLoading(false);
    }
  };

  const refresh = (): void => {
    generateAffirmation();
  };

  useEffect(() => {
    generateAffirmation();
  }, []);

  return {
    affirmation,
    isLoading,
    error,
    refresh,
  };
} 