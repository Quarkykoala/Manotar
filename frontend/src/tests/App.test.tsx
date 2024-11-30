import React from 'react';
import { render, screen } from '../utils/test-utils';
import App from '../App';
import { testLogger } from '../utils/testLogger';

describe('App Component', () => {
  beforeEach(() => {
    testLogger.info('App Test', 'Starting new test case');
  });

  afterEach(() => {
    testLogger.info('App Test', 'Test case completed');
  });

  test('renders the main app title', () => {
    testLogger.debug('App Test', 'Rendering App component');
    render(<App />);
    
    const titleElement = screen.getByText(/Enterprise Mental Health Analytics/i);
    expect(titleElement).toBeInTheDocument();
    testLogger.info('App Test', 'Title element found and verified');
  });

  test('renders the login page by default', () => {
    testLogger.debug('App Test', 'Rendering App component for login test');
    render(<App />);
    
    const loginElement = screen.getByText(/HR Mental Health Analytics/i);
    expect(loginElement).toBeInTheDocument();
    testLogger.info('App Test', 'Login page rendered successfully');
  });
}); 
