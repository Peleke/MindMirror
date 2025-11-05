import React, { createContext, useContext, useState, useCallback } from 'react';

type ThemeVariant = 'warm' | 'cool';

interface LandingThemeContextType {
  theme: ThemeVariant;
  toggleTheme: () => void;
  isWarm: boolean;
  isCool: boolean;
}

const LandingThemeContext = createContext<LandingThemeContextType | undefined>(undefined);

export function LandingThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<ThemeVariant>('cool'); // Default to cool (current brand)

  const toggleTheme = useCallback(() => {
    setTheme((prev) => (prev === 'warm' ? 'cool' : 'warm'));
  }, []);

  const value = {
    theme,
    toggleTheme,
    isWarm: theme === 'warm',
    isCool: theme === 'cool',
  };

  return <LandingThemeContext.Provider value={value}>{children}</LandingThemeContext.Provider>;
}

export function useLandingTheme() {
  const context = useContext(LandingThemeContext);
  if (!context) {
    throw new Error('useLandingTheme must be used within LandingThemeProvider');
  }
  return context;
}
