import { useState, useEffect } from 'react';

/**
 * A custom hook that creates a typewriter effect for a given string.
 *
 * @param text The full text to be displayed with the effect.
 * @param speed The delay in milliseconds between each character being revealed.
 * @returns The portion of the text to be displayed at the current time.
 */
export function useTypewriter(text: string, speed: number = 50): string {
  const [displayedText, setDisplayedText] = useState('');

  useEffect(() => {
    if (text) {
      const intervalId = setInterval(() => {
        // Use a functional update to get the latest state of the displayed text.
        setDisplayedText(current => {
          // If we've already displayed the full text, we clear the interval.
          if (current.length === text.length) {
            clearInterval(intervalId);
            return current;
          }
          // Otherwise, we return a substring of the full text, extended by one character.
          // This is more robust than using an external counter.
          return text.slice(0, current.length + 1);
        });
      }, speed);

      // The cleanup function runs when the component unmounts or when the `text` prop changes.
      return () => {
        clearInterval(intervalId);
        // Reset the text to start fresh for the new prop value.
        setDisplayedText('');
      };
    }
  }, [text, speed]);

  return displayedText;
} 