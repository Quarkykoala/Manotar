import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ExportButton } from '../ExportButton';
import { exportToExcel, exportToPDF } from '@/utils/export';

// Mock the export utilities
jest.mock('@/utils/export', () => ({
  exportToExcel: jest.fn(),
  exportToPDF: jest.fn(),
}));

describe('ExportButton', () => {
  const mockData = [{ name: 'John', sentiment: 'Positive' }];
  const mockFilename = 'test-export';
  
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders correctly with Excel type', () => {
    // Arrange & Act
    render(<ExportButton data={mockData} filename={mockFilename} type="excel" />);
    
    // Assert
    expect(screen.getByText('Export EXCEL')).toBeInTheDocument();
    expect(screen.getByRole('button')).toHaveClass('flex items-center gap-2');
  });

  it('renders correctly with PDF type', () => {
    // Arrange & Act
    render(<ExportButton data={mockData} filename={mockFilename} type="pdf" />);
    
    // Assert
    expect(screen.getByText('Export PDF')).toBeInTheDocument();
  });

  it('calls exportToExcel when clicked with excel type', () => {
    // Arrange
    render(<ExportButton data={mockData} filename={mockFilename} type="excel" />);
    
    // Act
    fireEvent.click(screen.getByRole('button'));
    
    // Assert
    expect(exportToExcel).toHaveBeenCalledWith(mockData, mockFilename);
    expect(exportToPDF).not.toHaveBeenCalled();
  });

  it('calls exportToPDF when clicked with pdf type', () => {
    // Arrange
    render(<ExportButton data={mockData} filename={mockFilename} type="pdf" />);
    
    // Act
    fireEvent.click(screen.getByRole('button'));
    
    // Assert
    expect(exportToPDF).toHaveBeenCalledWith(mockData, mockFilename);
    expect(exportToExcel).not.toHaveBeenCalled();
  });
}); 