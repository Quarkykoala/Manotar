import React from 'react';
import { useRouter } from 'next/router';
import { useTranslation } from 'next-i18next';
import { Menu } from '@headlessui/react';
import { GlobeAltIcon } from '@heroicons/react/24/outline';

const languages = [
  { code: 'en', name: 'English' },
  { code: 'hi', name: 'हिंदी' }
];

export function LanguageSwitcher() {
  const router = useRouter();
  const { i18n } = useTranslation();

  const changeLanguage = async (locale: string) => {
    const { pathname, asPath, query } = router;
    await router.push({ pathname, query }, asPath, { locale });
    document.documentElement.lang = locale;

    // Announce language change to screen readers
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', 'polite');
    announcement.className = 'sr-only';
    announcement.textContent = `Language changed to ${
      languages.find(lang => lang.code === locale)?.name
    }`;
    document.body.appendChild(announcement);
    setTimeout(() => document.body.removeChild(announcement), 1000);
  };

  return (
    <Menu as="div" className="relative inline-block text-left">
      <Menu.Button
        className="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700"
        aria-label="Select language"
      >
        <GlobeAltIcon className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
        <span>{languages.find(lang => lang.code === i18n.language)?.name}</span>
      </Menu.Button>

      <Menu.Items
        className="absolute right-0 z-10 mt-2 w-56 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none dark:bg-gray-800 dark:ring-gray-700"
        role="menu"
        aria-orientation="vertical"
        aria-labelledby="language-menu"
      >
        <div className="py-1" role="none">
          {languages.map(language => (
            <Menu.Item key={language.code}>
              {({ active }) => (
                <button
                  onClick={() => changeLanguage(language.code)}
                  className={`${
                    active
                      ? 'bg-gray-100 text-gray-900 dark:bg-gray-700 dark:text-white'
                      : 'text-gray-700 dark:text-gray-200'
                  } ${
                    i18n.language === language.code
                      ? 'font-semibold'
                      : 'font-normal'
                  } group flex w-full items-center px-4 py-2 text-sm`}
                  role="menuitem"
                >
                  <span
                    className={`mr-2 h-2 w-2 rounded-full ${
                      i18n.language === language.code
                        ? 'bg-blue-500'
                        : 'bg-transparent'
                    }`}
                    aria-hidden="true"
                  />
                  {language.name}
                  {i18n.language === language.code && (
                    <span className="sr-only">(current language)</span>
                  )}
                </button>
              )}
            </Menu.Item>
          ))}
        </div>
      </Menu.Items>
    </Menu>
  );
} 