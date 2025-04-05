import { exportToExcel, exportToPDF } from '../export';
import { saveAs } from 'file-saver';
import * as XLSX from 'xlsx';

// Mock dependencies
jest.mock('file-saver', () => ({
  saveAs: jest.fn(),
}));

jest.mock('xlsx', () => ({
  utils: {
    json_to_sheet: jest.fn().mockReturnValue({}),
    book_new: jest.fn().mockReturnValue({}),
    book_append_sheet: jest.fn(),
  },
  write: jest.fn().mockReturnValue(new ArrayBuffer(8)),
}));

jest.mock('jspdf', () => ({
  jsPDF: jest.fn().mockImplementation(() => ({
    setFontSize: jest.fn(),
    text: jest.fn(),
    save: jest.fn(),
  })),
}));

describe('Export Utilities', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('exportToExcel', () => {
    it('should convert data to Excel and trigger download', () => {
      // Arrange
      const mockData = [{ name: 'John', sentiment: 'Positive' }];
      const filename = 'test-export';

      // Act
      exportToExcel(mockData, filename);

      // Assert
      expect(XLSX.utils.json_to_sheet).toHaveBeenCalledWith(mockData);
      expect(XLSX.utils.book_new).toHaveBeenCalled();
      expect(XLSX.utils.book_append_sheet).toHaveBeenCalled();
      expect(XLSX.write).toHaveBeenCalled();
      expect(saveAs).toHaveBeenCalledWith(
        expect.any(Blob),
        `${filename}.xlsx`
      );
    });
  });

  describe('exportToPDF', () => {
    it('should convert data to PDF and trigger download', async () => {
      // Arrange
      const mockData = [{ name: 'John', sentiment: 'Positive' }];
      const filename = 'test-export';
      const mockJsPDF = {
        setFontSize: jest.fn(),
        text: jest.fn(),
        save: jest.fn(),
      };
      
      jest.spyOn(global, 'import').mockImplementation(() => 
        Promise.resolve({ jsPDF: jest.fn(() => mockJsPDF) })
      );

      // Act
      await exportToPDF(mockData, filename);

      // Assert
      expect(mockJsPDF.setFontSize).toHaveBeenCalledTimes(2);
      expect(mockJsPDF.text).toHaveBeenCalledWith(filename, 20, 20);
      expect(mockJsPDF.save).toHaveBeenCalledWith(`${filename}.pdf`);
    });
  });
}); 