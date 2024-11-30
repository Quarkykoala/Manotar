import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

interface DepartmentDetails {
  department: string;
  total_employees: number;
  mental_health_score: number;
  risk_level: string;
  support_requests: number;
  trend: string;
  key_metrics: {
    work_life_balance: number;
    job_satisfaction: number;
    stress_level: number;
    team_morale: number;
  };
  recent_keywords: Array<{ word: string; count: number }>;
}

interface Props {
  isOpen: boolean;
  onClose: () => void;
  data: DepartmentDetails | null;
}

export const DepartmentDetailsModal = ({ isOpen, onClose, data }: Props) => {
  if (!data) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{data.department} Department Details</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h4 className="text-sm font-medium">Total Employees</h4>
              <p className="text-2xl font-bold">{data.total_employees}</p>
            </div>
            <div>
              <h4 className="text-sm font-medium">Mental Health Score</h4>
              <p className="text-2xl font-bold">{data.mental_health_score}</p>
            </div>
          </div>
          
          <div>
            <h4 className="text-sm font-medium mb-2">Key Metrics</h4>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(data.key_metrics).map(([key, value]) => (
                <div key={key} className="bg-muted p-2 rounded">
                  <p className="text-sm capitalize">{key.replace('_', ' ')}</p>
                  <p className="text-lg font-medium">{value}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}; 