import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { exportToExcel, exportToPDF } from "@/utils/export";

interface ExportButtonProps {
  data: any[];
  filename: string;
  type: 'excel' | 'pdf';
}

export const ExportButton = ({ data, filename, type }: ExportButtonProps) => {
  const handleExport = () => {
    if (type === 'excel') {
      exportToExcel(data, filename);
    } else {
      exportToPDF(data, filename);
    }
  };

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={handleExport}
      className="flex items-center gap-2"
    >
      <Download className="h-4 w-4" />
      Export {type.toUpperCase()}
    </Button>
  );
}; 