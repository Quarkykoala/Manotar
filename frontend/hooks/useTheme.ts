import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'next-i18next';

export type Theme = 'light' | 'dark';
export type ColorScheme = 'default' | 'high-contrast';
export type FontSize = 'normal' | 'large' | 'x-large';
export type MotionPreference = 'no-preference' | 'reduced';

interface ThemePreferences {
  theme: Theme;
  colorScheme: ColorScheme;
  fontSize: FontSize;
  motionPreference: MotionPreference;
}

interface UseThemeOptions {
  defaultTheme?: Theme;
  defaultColorScheme?: ColorScheme;
  defaultFontSize?: FontSize;
  defaultMotionPreference?: MotionPreference;
  storageKey?: string;
}

const DEFAULT_OPTIONS: UseThemeOptions = {
  defaultTheme: 'light',
  defaultColorScheme: 'default',
  defaultFontSize: 'normal',
  defaultMotionPreference: 'no-preference',
  storageKey: 'manotar-theme-preferences'
};

export function useTheme(options: UseThemeOptions = {}) {
  const { t } = useTranslation('common');
  const mergedOptions = { ...DEFAULT_OPTIONS, ...options };

  const [preferences, setPreferences] = useState<ThemePreferences>(() => {
    if (typeof window === 'undefined') {
      return {
        theme: mergedOptions.defaultTheme!,
        colorScheme: mergedOptions.defaultColorScheme!,
        fontSize: mergedOptions.defaultFontSize!,
        motionPreference: mergedOptions.defaultMotionPreference!
      };
    }

    const stored = localStorage.getItem(mergedOptions.storageKey!);
    if (stored) {
      try {
        return JSON.parse(stored);
      } catch (error) {
        console.error('Failed to parse stored theme preferences:', error);
      }
    }

    // Check system preferences
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const prefersHighContrast = window.matchMedia('(prefers-contrast: more)').matches;

    return {
      theme: prefersDark ? 'dark' : mergedOptions.defaultTheme!,
      colorScheme: prefersHighContrast ? 'high-contrast' : mergedOptions.defaultColorScheme!,
      fontSize: mergedOptions.defaultFontSize!,
      motionPreference: prefersReducedMotion ? 'reduced' : mergedOptions.defaultMotionPreference!
    };
  });

  // Save preferences to localStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(mergedOptions.storageKey!, JSON.stringify(preferences));
    }
  }, [preferences, mergedOptions.storageKey]);

  // Apply theme classes to document
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const { theme, colorScheme, fontSize, motionPreference } = preferences;
    const html = document.documentElement;

    // Theme
    html.classList.remove('light', 'dark');
    html.classList.add(theme);

    // Color scheme
    html.classList.remove('default', 'high-contrast');
    html.classList.add(colorScheme);

    // Font size
    html.classList.remove('text-normal', 'text-large', 'text-x-large');
    html.classList.add(`text-${fontSize}`);

    // Motion preference
    html.classList.remove('motion-safe', 'motion-reduce');
    html.classList.add(`motion-${motionPreference === 'reduced' ? 'reduce' : 'safe'}`);

    // Announce changes for screen readers
    const announceChange = (change: string) => {
      const announcement = document.createElement('div');
      announcement.setAttribute('role', 'status');
      announcement.setAttribute('aria-live', 'polite');
      announcement.className = 'sr-only';
      announcement.textContent = change;
      document.body.appendChild(announcement);
      setTimeout(() => document.body.removeChild(announcement), 1000);
    };

    announceChange(t('settings.appearance.themeChanged', { theme: t(`settings.appearance.${theme}`) }));
  }, [preferences, t]);

  const toggleTheme = useCallback(() => {
    setPreferences(prev => ({
      ...prev,
      theme: prev.theme === 'light' ? 'dark' : 'light'
    }));
  }, []);

  const toggleColorScheme = useCallback(() => {
    setPreferences(prev => ({
      ...prev,
      colorScheme: prev.colorScheme === 'default' ? 'high-contrast' : 'default'
    }));
  }, []);

  const increaseFontSize = useCallback(() => {
    setPreferences(prev => {
      const sizes: FontSize[] = ['normal', 'large', 'x-large'];
      const currentIndex = sizes.indexOf(prev.fontSize);
      const nextSize = sizes[Math.min(currentIndex + 1, sizes.length - 1)];
      return { ...prev, fontSize: nextSize };
    });
  }, []);

  const decreaseFontSize = useCallback(() => {
    setPreferences(prev => {
      const sizes: FontSize[] = ['normal', 'large', 'x-large'];
      const currentIndex = sizes.indexOf(prev.fontSize);
      const nextSize = sizes[Math.max(currentIndex - 1, 0)];
      return { ...prev, fontSize: nextSize };
    });
  }, []);

  const toggleMotionPreference = useCallback(() => {
    setPreferences(prev => ({
      ...prev,
      motionPreference: prev.motionPreference === 'no-preference' ? 'reduced' : 'no-preference'
    }));
  }, []);

  const resetPreferences = useCallback(() => {
    setPreferences({
      theme: mergedOptions.defaultTheme!,
      colorScheme: mergedOptions.defaultColorScheme!,
      fontSize: mergedOptions.defaultFontSize!,
      motionPreference: mergedOptions.defaultMotionPreference!
    });
  }, [mergedOptions]);

  return {
    preferences,
    toggleTheme,
    toggleColorScheme,
    increaseFontSize,
    decreaseFontSize,
    toggleMotionPreference,
    resetPreferences
  };
} 