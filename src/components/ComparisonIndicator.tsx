import { ArrowUp, ArrowDown, Minus } from 'lucide-react';

interface ComparisonIndicatorProps {
  currentValue: number;
  previousValue: number;
  format?: 'percentage' | 'decimal';
}

export const ComparisonIndicator = ({ currentValue, previousValue, format = 'percentage' }: ComparisonIndicatorProps) => {
  const difference = currentValue - previousValue;
  const percentageChange = ((difference / previousValue) * 100).toFixed(1);
  
  return (
    <div className="flex items-center gap-1 text-sm">
      {difference > 0 ? (
        <ArrowUp className="h-4 w-4 text-green-500" />
      ) : difference < 0 ? (
        <ArrowDown className="h-4 w-4 text-red-500" />
      ) : (
        <Minus className="h-4 w-4 text-gray-500" />
      )}
      <span className={difference > 0 ? 'text-green-500' : difference < 0 ? 'text-red-500' : 'text-gray-500'}>
        {format === 'percentage' ? `${Math.abs(Number(percentageChange))}%` : Math.abs(difference).toFixed(1)}
      </span>
      <span className="text-gray-500 text-xs">vs last month</span>
    </div>
  );
}; 