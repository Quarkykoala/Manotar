import '@testing-library/jest-dom';
import React from 'react';

// Mock ResizeObserver
class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

window.ResizeObserver = ResizeObserver;

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock Framer Motion
jest.mock('framer-motion', () => ({
  motion: {
    div: 'div',
  },
  AnimatePresence: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

// Mock Recharts
jest.mock('recharts', () => {
  const React = require('react');
  
  const ResponsiveContainer = ({ children, width = "100%", height = "100%" }: any) => (
    <div data-testid="responsive-container" style={{ width, height }}>
      {children}
    </div>
  );

  const BarChart = () => <div data-testid="bar-chart" />;
  const Bar = () => <div data-testid="bar" />;
  const XAxis = () => <div data-testid="x-axis" />;
  const YAxis = () => <div data-testid="y-axis" />;
  const CartesianGrid = () => <div data-testid="cartesian-grid" />;
  const Tooltip = () => <div data-testid="tooltip" />;
  const Legend = () => <div data-testid="legend" />;
  const LineChart = () => <div data-testid="line-chart" />;
  const Line = () => <div data-testid="line" />;

  return {
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    LineChart,
    Line,
  };
});

// Mock console methods for cleaner test output
const originalConsole = { ...console };
beforeAll(() => {
  console.error = (...args: any[]) => {
    if (args[0]?.includes?.('Warning:')) return;
    originalConsole.error(...args);
  };
  console.warn = (...args: any[]) => {
    if (args[0]?.includes?.('Warning:')) return;
    originalConsole.warn(...args);
  };
});

afterAll(() => {
  console.error = originalConsole.error;
  console.warn = originalConsole.warn;
});

// Mock MSW if available
try {
  jest.mock('msw', () => ({
    rest: {
      get: jest.fn(),
      post: jest.fn(),
    },
    setupServer: jest.fn(),
  }));
} catch (error) {
  console.warn('MSW not installed, skipping mock');
}
