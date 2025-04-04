import React, { useState } from 'react';
import { 
  Select, 
  SelectTrigger, 
  SelectValue, 
  SelectItem, 
  SelectContent 
} from '../../../components/ui/select';

interface DashboardViewProps {
  className?: string;
}

export const DashboardView: React.FC<DashboardViewProps> = ({ className }) => {
  const [department, setDepartment] = useState('all');

  return (
    <div className={className}>
      <Select 
        value={department} 
        onValueChange={setDepartment}
      >
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="Select Department" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Departments</SelectItem>
          <SelectItem value="engineering">Engineering</SelectItem>
          <SelectItem value="sales">Sales</SelectItem>
          <SelectItem value="marketing">Marketing</SelectItem>
          <SelectItem value="finance">Finance</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
};

export default DashboardView; 