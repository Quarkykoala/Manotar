import { useTranslation as useNextTranslation } from 'next-i18next';
import { useCallback } from 'react';

// Type for nested translation keys
type TranslationKey = string | {
  [key: string]: TranslationKey;
};

// Type for translation namespace
type Namespace = 'common';

export const useTranslation = (namespace: Namespace = 'common') => {
  const { t: translate, i18n } = useNextTranslation(namespace);

  // Wrapper for translation function with error handling
  const t = useCallback((key: string, params?: Record<string, string>) => {
    try {
      const translation = translate(key, params);
      // Return key if translation is missing
      return translation === key ? `[${key}]` : translation;
    } catch (error) {
      console.error(`Translation error for key "${key}":`, error);
      return `[${key}]`;
    }
  }, [translate]);

  // Change language
  const changeLanguage = useCallback(async (lang: string) => {
    try {
      await i18n.changeLanguage(lang);
    } catch (error) {
      console.error('Failed to change language:', error);
    }
  }, [i18n]);

  // Get current language
  const getCurrentLanguage = useCallback(() => {
    return i18n.language;
  }, [i18n]);

  return {
    t,
    changeLanguage,
    getCurrentLanguage,
    i18n
  };
};

export type { TranslationKey }; 