import React, { createContext, useContext, useEffect, useState } from 'react';

interface ThemeContextType {
  isDarkMode: boolean;
  toggleDarkMode: () => void;
  highContrast: boolean;
  toggleHighContrast: () => void;
  fontSize: number;
  increaseFontSize: () => void;
  decreaseFontSize: () => void;
  resetFontSize: () => void;
  reducedMotion: boolean;
  toggleReducedMotion: () => void;
}

interface ThemeProviderProps {
  children: React.ReactNode;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const STORAGE_KEY = 'manotar_theme_preferences';
const DEFAULT_FONT_SIZE = 16;
const MIN_FONT_SIZE = 12;
const MAX_FONT_SIZE = 24;

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  // Initialize state from localStorage or system preferences
  const [preferences, setPreferences] = useState(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
    return {
      isDarkMode: window.matchMedia('(prefers-color-scheme: dark)').matches,
      highContrast: false,
      fontSize: DEFAULT_FONT_SIZE,
      reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    };
  });

  const { isDarkMode, highContrast, fontSize, reducedMotion } = preferences;

  // Update localStorage when preferences change
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences));
    
    // Update document classes and styles
    document.documentElement.classList.toggle('dark', isDarkMode);
    document.documentElement.classList.toggle('high-contrast', highContrast);
    document.documentElement.classList.toggle('reduced-motion', reducedMotion);
    document.documentElement.style.fontSize = `${fontSize}px`;
  }, [preferences]);

  // Listen for system preference changes
  useEffect(() => {
    const darkModeMedia = window.matchMedia('(prefers-color-scheme: dark)');
    const motionMedia = window.matchMedia('(prefers-reduced-motion: reduce)');

    const handleDarkModeChange = (e: MediaQueryListEvent) => {
      setPreferences(prev => ({ ...prev, isDarkMode: e.matches }));
    };

    const handleMotionChange = (e: MediaQueryListEvent) => {
      setPreferences(prev => ({ ...prev, reducedMotion: e.matches }));
    };

    darkModeMedia.addEventListener('change', handleDarkModeChange);
    motionMedia.addEventListener('change', handleMotionChange);

    return () => {
      darkModeMedia.removeEventListener('change', handleDarkModeChange);
      motionMedia.removeEventListener('change', handleMotionChange);
    };
  }, []);

  const toggleDarkMode = () => {
    setPreferences(prev => ({ ...prev, isDarkMode: !prev.isDarkMode }));
  };

  const toggleHighContrast = () => {
    setPreferences(prev => ({ ...prev, highContrast: !prev.highContrast }));
  };

  const increaseFontSize = () => {
    setPreferences(prev => ({
      ...prev,
      fontSize: Math.min(prev.fontSize + 2, MAX_FONT_SIZE),
    }));
  };

  const decreaseFontSize = () => {
    setPreferences(prev => ({
      ...prev,
      fontSize: Math.max(prev.fontSize - 2, MIN_FONT_SIZE),
    }));
  };

  const resetFontSize = () => {
    setPreferences(prev => ({ ...prev, fontSize: DEFAULT_FONT_SIZE }));
  };

  const toggleReducedMotion = () => {
    setPreferences(prev => ({ ...prev, reducedMotion: !prev.reducedMotion }));
  };

  const value = {
    isDarkMode,
    toggleDarkMode,
    highContrast,
    toggleHighContrast,
    fontSize,
    increaseFontSize,
    decreaseFontSize,
    resetFontSize,
    reducedMotion,
    toggleReducedMotion,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// Custom hook for dynamic styles based on theme
export const useThemeStyles = () => {
  const { isDarkMode, highContrast } = useTheme();

  return {
    backgroundColor: isDarkMode ? 'rgb(17, 24, 39)' : 'white',
    textColor: isDarkMode ? 'white' : 'rgb(17, 24, 39)',
    primaryColor: highContrast ? 'rgb(37, 99, 235)' : 'rgb(59, 130, 246)',
    borderColor: isDarkMode ? 'rgb(75, 85, 99)' : 'rgb(229, 231, 235)',
  };
}; 