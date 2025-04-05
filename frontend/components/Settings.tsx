import React from 'react';
import { useTranslation } from 'next-i18next';
import { Switch } from '@headlessui/react';
import { useTheme } from '../hooks/useTheme';
import { useFocusTrap } from '../hooks/useFocusTrap';

interface SettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

export function Settings({ isOpen, onClose }: SettingsProps) {
  const { t } = useTranslation('common');
  const {
    preferences,
    toggleTheme,
    toggleColorScheme,
    increaseFontSize,
    decreaseFontSize,
    toggleMotionPreference,
    resetPreferences
  } = useTheme();

  const containerRef = useFocusTrap({ enabled: isOpen, onEscape: onClose });

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      role="dialog"
      aria-modal="true"
      aria-labelledby="settings-title"
    >
      <div
        ref={containerRef}
        className="relative w-full max-w-lg rounded-lg bg-white p-6 shadow-xl dark:bg-gray-800"
      >
        <h2
          id="settings-title"
          className="mb-6 text-2xl font-bold text-gray-900 dark:text-white"
        >
          {t('settings.title')}
        </h2>

        <div className="space-y-6">
          {/* Appearance Section */}
          <section aria-labelledby="appearance-title">
            <h3
              id="appearance-title"
              className="mb-4 text-lg font-semibold text-gray-700 dark:text-gray-300"
            >
              {t('settings.appearance')}
            </h3>

            {/* Dark Mode */}
            <div className="flex items-center justify-between py-2">
              <label
                htmlFor="dark-mode-toggle"
                className="text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                {t('settings.darkMode')}
              </label>
              <Switch
                id="dark-mode-toggle"
                checked={preferences.theme === 'dark'}
                onChange={toggleTheme}
                className={`${
                  preferences.theme === 'dark' ? 'bg-blue-600' : 'bg-gray-200'
                } relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2`}
              >
                <span className="sr-only">{t('settings.toggleDarkMode')}</span>
                <span
                  className={`${
                    preferences.theme === 'dark' ? 'translate-x-6' : 'translate-x-1'
                  } inline-block h-4 w-4 transform rounded-full bg-white transition-transform`}
                />
              </Switch>
            </div>

            {/* High Contrast */}
            <div className="flex items-center justify-between py-2">
              <label
                htmlFor="high-contrast-toggle"
                className="text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                {t('settings.highContrast')}
              </label>
              <Switch
                id="high-contrast-toggle"
                checked={preferences.colorScheme === 'high-contrast'}
                onChange={toggleColorScheme}
                className={`${
                  preferences.colorScheme === 'high-contrast'
                    ? 'bg-blue-600'
                    : 'bg-gray-200'
                } relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2`}
              >
                <span className="sr-only">{t('settings.toggleHighContrast')}</span>
                <span
                  className={`${
                    preferences.colorScheme === 'high-contrast'
                      ? 'translate-x-6'
                      : 'translate-x-1'
                  } inline-block h-4 w-4 transform rounded-full bg-white transition-transform`}
                />
              </Switch>
            </div>

            {/* Font Size */}
            <div className="py-2">
              <label
                id="font-size-label"
                className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                {t('settings.fontSize')}
              </label>
              <div
                className="flex items-center space-x-4"
                role="group"
                aria-labelledby="font-size-label"
              >
                <button
                  onClick={decreaseFontSize}
                  disabled={preferences.fontSize === 'normal'}
                  className="rounded-md bg-gray-100 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 dark:bg-gray-700 dark:text-gray-300"
                  aria-label={t('settings.decreaseFontSize')}
                >
                  A-
                </button>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {preferences.fontSize}
                </span>
                <button
                  onClick={increaseFontSize}
                  disabled={preferences.fontSize === 'x-large'}
                  className="rounded-md bg-gray-100 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 dark:bg-gray-700 dark:text-gray-300"
                  aria-label={t('settings.increaseFontSize')}
                >
                  A+
                </button>
              </div>
            </div>

            {/* Reduced Motion */}
            <div className="flex items-center justify-between py-2">
              <label
                htmlFor="reduced-motion-toggle"
                className="text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                {t('settings.reducedMotion')}
              </label>
              <Switch
                id="reduced-motion-toggle"
                checked={preferences.motionPreference === 'reduced'}
                onChange={toggleMotionPreference}
                className={`${
                  preferences.motionPreference === 'reduced'
                    ? 'bg-blue-600'
                    : 'bg-gray-200'
                } relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2`}
              >
                <span className="sr-only">{t('settings.toggleReducedMotion')}</span>
                <span
                  className={`${
                    preferences.motionPreference === 'reduced'
                      ? 'translate-x-6'
                      : 'translate-x-1'
                  } inline-block h-4 w-4 transform rounded-full bg-white transition-transform`}
                />
              </Switch>
            </div>
          </section>

          <p className="text-sm text-gray-500 dark:text-gray-400">
            {t('settings.helpText')}
          </p>

          <div className="flex justify-between">
            <button
              onClick={resetPreferences}
              className="rounded-md bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:bg-gray-700 dark:text-gray-300"
            >
              {t('settings.reset')}
            </button>
            <button
              onClick={onClose}
              className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              {t('common.save')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
} 