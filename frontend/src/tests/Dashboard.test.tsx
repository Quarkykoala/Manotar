import React from 'react';
import { render, screen, fireEvent } from '../utils/test-utils';
import Dashboard from '../pages/Dashboard';
import { testLogger } from '../utils/testLogger';

describe('Dashboard Component', () => {
  beforeEach(() => {
    testLogger.info('Dashboard Test', 'Starting new test case');
  });

  afterEach(() => {
    testLogger.info('Dashboard Test', 'Test case completed');
  });

  test('renders department filter', () => {
    testLogger.debug('Dashboard Test', 'Rendering Dashboard component');
    render(<Dashboard />);
    
    const filterElement = screen.getByText(/Department/i);
    expect(filterElement).toBeInTheDocument();
    testLogger.info('Dashboard Test', 'Department filter found');
  });

  test('renders time range filter', () => {
    testLogger.debug('Dashboard Test', 'Rendering Dashboard component');
    render(<Dashboard />);
    
    const filterElement = screen.getByText(/Time Range/i);
    expect(filterElement).toBeInTheDocument();
    testLogger.info('Dashboard Test', 'Time range filter found');
  });

  test('changes department selection', () => {
    testLogger.debug('Dashboard Test', 'Testing department selection');
    render(<Dashboard />);
    
    const select = screen.getByLabelText(/Department/i);
    fireEvent.change(select, { target: { value: 'Engineering' } });
    
    expect(select).toHaveValue('Engineering');
    testLogger.info('Dashboard Test', 'Department selection changed successfully');
  });
}); 
