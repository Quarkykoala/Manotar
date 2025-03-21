import { saveAs } from 'file-saver';
import * as XLSX from 'xlsx';

export const exportToExcel = (data: any[], filename: string) => {
  const ws = XLSX.utils.json_to_sheet(data);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Sheet1');
  const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
  const dataBlob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
  saveAs(dataBlob, `${filename}.xlsx`);
};

export const exportToPDF = async (data: any[], filename: string) => {
  const { jsPDF } = await import('jspdf');
  const doc = new jsPDF();
  
  // Add title
  doc.setFontSize(16);
  doc.text(filename, 20, 20);
  
  // Add data
  doc.setFontSize(12);
  let y = 40;
  data.forEach((row) => {
    Object.entries(row).forEach(([key, value]) => {
      doc.text(`${key}: ${value}`, 20, y);
      y += 10;
    });
    y += 10;
  });
  
  doc.save(`${filename}.pdf`);
}; 