import { ChevronLeft, ChevronRight } from 'lucide-react';
import { format } from 'date-fns';
import { ComparisonIndicator } from './ComparisonIndicator';

interface MonthNavigatorProps {
  currentDate: Date;
  onPrevious: () => void;
  onNext: () => void;
  disableNext?: boolean;
  currentValue?: number;
  previousValue?: number;
  comparisonFormat?: 'percentage' | 'decimal';
}

export const MonthNavigator = ({
  currentDate,
  onPrevious,
  onNext,
  disableNext = false,
  currentValue,
  previousValue,
  comparisonFormat
}: MonthNavigatorProps) => (
  <div className="flex items-center justify-between mb-4">
    <button
      onClick={onPrevious}
      className="p-2 hover:bg-gray-100 rounded-full transition-colors"
    >
      <ChevronLeft className="h-5 w-5" />
    </button>
    <div className="flex flex-col items-center">
      <span className="font-medium">
        {format(currentDate, 'MMMM yyyy')}
      </span>
      {currentValue !== undefined && previousValue !== undefined && (
        <ComparisonIndicator
          currentValue={currentValue}
          previousValue={previousValue}
          format={comparisonFormat}
        />
      )}
    </div>
    <button
      onClick={onNext}
      disabled={disableNext}
      className={`p-2 hover:bg-gray-100 rounded-full transition-colors ${
        disableNext ? 'opacity-50 cursor-not-allowed' : ''
      }`}
    >
      <ChevronRight className="h-5 w-5" />
    </button>
  </div>
); 