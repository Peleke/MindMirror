import { useState, useEffect } from 'react';

interface UseAffirmationReturn {
  affirmation: string;
  isLoading: boolean;
  error: string | null;
  generateAffirmation: () => void;
}

// Static fallback affirmations, rephrased to sound like they are derived from past journal entries.
const FALLBACK_AFFIRMATIONS = [
  "You've mentioned feeling capable and resilient before. Today is another chance to embody that.",
  "Remembering your goal to 'procrastinate less,' try tackling one small task right now.",
  "You often write about the importance of 'good health.' A short walk today could be a great step.",
  "Your entries show a lot of gratitude for your friends. Leaning on them is a sign of strength.",
  "You wrote about being excited for an 'upcoming vacation.' Holding onto that positive feeling can brighten your day.",
  "You've faced challenges before and your writing shows you've always grown stronger. You have that same resilience today.",
  "Seeing your focus on 'better code reviews' shows your commitment to growth. Keep that momentum going.",
];

export function useAffirmation(): UseAffirmationReturn {
  const [affirmation, setAffirmation] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const getRandomAffirmation = (): string => {
    if (FALLBACK_AFFIRMATIONS.length === 0) {
      return "Take a moment to reflect on your journey."; // A safe default
    }
    const randomIndex = Math.floor(Math.random() * FALLBACK_AFFIRMATIONS.length);
    return FALLBACK_AFFIRMATIONS[randomIndex] || "Focus on your strengths today."; // Fallback for safety
  };

  const generateAffirmation = async (): Promise<void> => {
    setIsLoading(true);
    setError(null);
    try {
      // For now, we'll just use a random fallback affirmation.
      // In the future, this could be an API call to an LLM.
      const randomAffirmation = getRandomAffirmation();
      setAffirmation(randomAffirmation);
    } catch (err) {
      console.error("Failed to generate affirmation:", err);
      setError("Could not load an affirmation. Please try again later.");
      // Fallback to a random affirmation even if the API fails
      setAffirmation(getRandomAffirmation());
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    generateAffirmation();
  }, []);

  return {
    affirmation,
    isLoading,
    error,
    generateAffirmation,
  };
} 