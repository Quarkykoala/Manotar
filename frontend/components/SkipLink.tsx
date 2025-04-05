import React, { useCallback } from 'react';
import { useTranslation } from 'next-i18next';

interface SkipLinkProps {
  targetId: string;
  className?: string;
}

export function SkipLink({ targetId, className = '' }: SkipLinkProps) {
  const { t } = useTranslation('common');

  const handleClick = useCallback(
    (event: React.MouseEvent<HTMLAnchorElement>) => {
      event.preventDefault();
      const target = document.getElementById(targetId);
      
      if (target) {
        // Set tabindex to make the element focusable
        target.setAttribute('tabindex', '-1');
        target.focus({ preventScroll: false });
        
        // Remove tabindex after blur
        const handleBlur = () => {
          target.removeAttribute('tabindex');
          target.removeEventListener('blur', handleBlur);
        };
        target.addEventListener('blur', handleBlur);

        // Announce to screen readers
        const announcement = document.createElement('div');
        announcement.setAttribute('role', 'status');
        announcement.setAttribute('aria-live', 'polite');
        announcement.className = 'sr-only';
        announcement.textContent = t('accessibility.skippedToContent');
        document.body.appendChild(announcement);
        setTimeout(() => document.body.removeChild(announcement), 1000);
      }
    },
    [targetId, t]
  );

  return (
    <a
      href={`#${targetId}`}
      onClick={handleClick}
      className={`fixed left-4 top-4 z-50 -translate-y-full transform rounded-md bg-blue-600 px-4 py-2 text-white transition-transform focus:translate-y-0 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${className}`}
    >
      {t('accessibility.skipToMain')}
    </a>
  );
}

interface SkipLinksProps {
  links: Array<{
    targetId: string;
    label: string;
  }>;
  className?: string;
}

export function SkipLinks({ links, className = '' }: SkipLinksProps) {
  const { t } = useTranslation('common');

  const handleClick = useCallback(
    (event: React.MouseEvent<HTMLAnchorElement>, targetId: string) => {
      event.preventDefault();
      const target = document.getElementById(targetId);
      
      if (target) {
        target.setAttribute('tabindex', '-1');
        target.focus({ preventScroll: false });
        
        const handleBlur = () => {
          target.removeAttribute('tabindex');
          target.removeEventListener('blur', handleBlur);
        };
        target.addEventListener('blur', handleBlur);

        const announcement = document.createElement('div');
        announcement.setAttribute('role', 'status');
        announcement.setAttribute('aria-live', 'polite');
        announcement.className = 'sr-only';
        announcement.textContent = t('accessibility.skippedToSection', {
          section: event.currentTarget.textContent
        });
        document.body.appendChild(announcement);
        setTimeout(() => document.body.removeChild(announcement), 1000);
      }
    },
    [t]
  );

  return (
    <nav
      aria-label={t('accessibility.skipLinks')}
      className={`fixed left-4 top-4 z-50 flex -translate-y-full transform flex-col space-y-2 focus-within:translate-y-0 ${className}`}
    >
      {links.map(({ targetId, label }) => (
        <a
          key={targetId}
          href={`#${targetId}`}
          onClick={(event) => handleClick(event, targetId)}
          className="rounded-md bg-blue-600 px-4 py-2 text-white transition-colors hover:bg-blue-700 focus:translate-y-0 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          {t(label)}
        </a>
      ))}
    </nav>
  );
} 