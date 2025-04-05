import React from 'react';
import { useTranslation } from '../hooks/useTranslation';
import { ThemeProvider } from '../contexts/ThemeContext';
import { ErrorBoundary } from './ErrorBoundary';
import { LanguageSwitcher } from './LanguageSwitcher';
import { Settings } from './Settings';
import { LoadingSpinner } from './LoadingSpinner';

interface LayoutProps {
  children: React.ReactNode;
  loading?: boolean;
}

const SkipLink = () => {
  const { t } = useTranslation();
  
  return (
    <a
      href="#main-content"
      className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:p-4 focus:bg-white focus:text-primary-600"
    >
      {t('accessibility.skipToMain')}
    </a>
  );
};

const Header = () => {
  const { t } = useTranslation();

  return (
    <header className="bg-white dark:bg-gray-800 shadow-sm">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center">
          <img
            className="h-8 w-auto"
            src="/logo.svg"
            alt="Manotar"
          />
          <h1 className="ml-3 text-xl font-semibold text-gray-900 dark:text-white">
            {t('dashboard.title')}
          </h1>
        </div>
        <div className="flex items-center space-x-4">
          <LanguageSwitcher />
        </div>
      </nav>
    </header>
  );
};

const Footer = () => {
  const { t } = useTranslation();
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            © {currentYear} Manotar. {t('common.rights')}
          </p>
          <div className="flex space-x-6">
            <a
              href="/privacy"
              className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
            >
              {t('common.privacy')}
            </a>
            <a
              href="/terms"
              className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
            >
              {t('common.terms')}
            </a>
            <a
              href="/accessibility"
              className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
            >
              {t('common.accessibility')}
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export const Layout = ({ children, loading = false }: LayoutProps) => {
  return (
    <ThemeProvider>
      <ErrorBoundary>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
          <SkipLink />
          <Header />
          
          <main
            id="main-content"
            className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
          >
            {loading ? (
              <LoadingSpinner fullScreen />
            ) : (
              children
            )}
          </main>

          <Footer />
        </div>
      </ErrorBoundary>
    </ThemeProvider>
  );
};

// HOC to wrap pages with the layout
export const withLayout = <P extends object>(
  Component: React.ComponentType<P>
) => {
  return function WrappedComponent(props: P) {
    return (
      <Layout>
        <Component {...props} />
      </Layout>
    );
  };
};