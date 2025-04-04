import '../styles/globals.css';
import { ReactNode } from 'react';
import { ErrorBoundary } from '../components/ErrorBoundary';

export const metadata = {
  title: 'Manotar - Mental Health Analytics Platform',
  description: 'AI-powered platform for employee mental health analytics',
};

export default function RootLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <ErrorBoundary>
          {children}
        </ErrorBoundary>
      </body>
    </html>
  );
} 