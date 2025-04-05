import React from 'react';
import { useTranslation } from 'next-i18next';

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  className?: string;
  message?: string;
}

export function LoadingSpinner({
  size = 'medium',
  className = '',
  message
}: LoadingSpinnerProps) {
  const { t } = useTranslation('common');
  const defaultMessage = t('common.loading');

  const sizeClasses = {
    small: 'h-4 w-4 border-2',
    medium: 'h-8 w-8 border-3',
    large: 'h-12 w-12 border-4'
  };

  return (
    <div
      role="status"
      aria-live="polite"
      className={`flex flex-col items-center justify-center space-y-2 ${className}`}
    >
      <div
        className={`animate-spin rounded-full border-gray-300 border-t-blue-600 dark:border-gray-600 dark:border-t-blue-400 ${sizeClasses[size]}`}
      />
      {(message || defaultMessage) && (
        <p className="text-sm text-gray-500 dark:text-gray-400">
          {message || defaultMessage}
        </p>
      )}
      <span className="sr-only">{t('accessibility.loadingState')}</span>
    </div>
  );
}

interface LoadingOverlayProps extends LoadingSpinnerProps {
  isLoading: boolean;
  children: React.ReactNode;
}

export function LoadingOverlay({
  isLoading,
  children,
  size = 'large',
  message,
  className = ''
}: LoadingOverlayProps) {
  if (!isLoading) return <>{children}</>;

  return (
    <div className="relative">
      <div
        className={`absolute inset-0 z-50 flex items-center justify-center bg-white bg-opacity-75 dark:bg-gray-900 dark:bg-opacity-75 ${className}`}
      >
        <LoadingSpinner size={size} message={message} />
      </div>
      <div className="pointer-events-none opacity-50">{children}</div>
    </div>
  );
}

interface LoadingButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  isLoading: boolean;
  loadingText?: string;
  children: React.ReactNode;
}

export function LoadingButton({
  isLoading,
  loadingText,
  children,
  disabled,
  className = '',
  ...props
}: LoadingButtonProps) {
  const { t } = useTranslation('common');
  const defaultLoadingText = t('common.loading');

  return (
    <button
      {...props}
      disabled={isLoading || disabled}
      className={`relative inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
      aria-busy={isLoading}
    >
      {isLoading && (
        <LoadingSpinner
          size="small"
          className="absolute left-3"
          message={loadingText || defaultLoadingText}
        />
      )}
      <span className={isLoading ? 'invisible' : undefined}>{children}</span>
      {isLoading && (
        <span className="sr-only">{loadingText || defaultLoadingText}</span>
      )}
    </button>
  );
} 