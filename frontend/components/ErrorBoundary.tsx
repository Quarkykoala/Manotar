import React from 'react';
import { useTranslation } from 'next-i18next';
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

export class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log the error to an error reporting service
    console.error('Error caught by ErrorBoundary:', error, errorInfo);
    this.props.onError?.(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <ErrorFallback error={this.state.error} resetError={() => this.setState({ hasError: false, error: null })} />
        )
      );
    }

    return this.props.children;
  }
}

interface ErrorFallbackProps {
  error: Error | null;
  resetError: () => void;
}

export function ErrorFallback({ error, resetError }: ErrorFallbackProps) {
  const { t } = useTranslation('common');

  return (
    <div
      role="alert"
      className="flex min-h-[200px] flex-col items-center justify-center rounded-lg bg-red-50 p-6 text-center dark:bg-red-900/10"
    >
      <ExclamationTriangleIcon
        className="h-12 w-12 text-red-500 dark:text-red-400"
        aria-hidden="true"
      />
      <h2 className="mt-4 text-lg font-semibold text-red-800 dark:text-red-200">
        {t('errors.title')}
      </h2>
      <p className="mt-2 max-w-md text-sm text-red-700 dark:text-red-300">
        {error?.message || t('errors.unknown')}
      </p>
      <div className="mt-6 flex space-x-4">
        <button
          onClick={() => window.location.reload()}
          className="rounded-md bg-red-100 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 dark:bg-red-900/20 dark:text-red-200 dark:hover:bg-red-900/30"
        >
          {t('errors.refresh')}
        </button>
        <button
          onClick={resetError}
          className="rounded-md bg-white px-4 py-2 text-sm font-medium text-red-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 dark:bg-gray-800 dark:text-red-200 dark:hover:bg-gray-700"
        >
          {t('errors.retry')}
        </button>
      </div>
    </div>
  );
}

interface AsyncBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  onError?: (error: Error) => void;
  suspenseFallback?: React.ReactNode;
}

export function AsyncBoundary({
  children,
  fallback,
  onError,
  suspenseFallback
}: AsyncBoundaryProps) {
  return (
    <ErrorBoundary
      fallback={fallback}
      onError={(error) => onError?.(error)}
    >
      <React.Suspense fallback={suspenseFallback || <LoadingFallback />}>
        {children}
      </React.Suspense>
    </ErrorBoundary>
  );
}

function LoadingFallback() {
  const { t } = useTranslation('common');

  return (
    <div className="flex min-h-[200px] items-center justify-center">
      <div
        className="h-8 w-8 animate-spin rounded-full border-4 border-gray-300 border-t-blue-600"
        role="status"
      >
        <span className="sr-only">{t('common.loading')}</span>
      </div>
    </div>
  );
} 