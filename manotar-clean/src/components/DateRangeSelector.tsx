import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Calendar } from "@/components/ui/calendar";

interface DateRangeSelectorProps {
  startDate: Date;
  endDate: Date;
  onStartDateChange: (date: Date | undefined) => void;
  onEndDateChange: (date: Date | undefined) => void;
  onRangePresetChange: (preset: string) => void;
}

const presets = [
  { label: 'Last 7 Days', value: '7d' },
  { label: 'Last 30 Days', value: '30d' },
  { label: 'Last 3 Months', value: '90d' },
  { label: 'Last 6 Months', value: '180d' },
  { label: 'Last Year', value: '365d' },
];

export const DateRangeSelector = ({
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
  onRangePresetChange,
}: DateRangeSelectorProps) => {
  return (
    <Card className="p-4">
      <CardContent className="flex flex-col gap-4">
        <div className="flex items-center gap-4">
          <Select onValueChange={onRangePresetChange}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select time range" />
            </SelectTrigger>
            <SelectContent>
              {presets.map((preset) => (
                <SelectItem key={preset.value} value={preset.value}>
                  {preset.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <span className="text-sm text-muted-foreground">or select custom range</span>
        </div>
        
        <div className="flex gap-4">
          <div>
            <p className="text-sm mb-2">Start Date</p>
            <Calendar
              mode="single"
              selected={startDate}
              onSelect={onStartDateChange}
              disabled={(date) => date > endDate || date > new Date()}
              className="rounded-md border"
            />
          </div>
          <div>
            <p className="text-sm mb-2">End Date</p>
            <Calendar
              mode="single"
              selected={endDate}
              onSelect={onEndDateChange}
              disabled={(date) => date < startDate || date > new Date()}
              className="rounded-md border"
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}; 