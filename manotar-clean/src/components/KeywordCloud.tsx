import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

type KeywordData = {
  keyword: string;
  count: number;
  trend: string;
};

export const KeywordCloud = ({ data }: { data: Record<string, KeywordData> }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Keyword Analysis</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-2">
          {Object.entries(data).map(([keyword, { count, trend }]) => (
            <div
              key={keyword}
              className="px-3 py-1 rounded-full bg-primary/10 text-primary flex items-center gap-2"
            >
              <span>{keyword}</span>
              <span className="text-xs">{count}</span>
              <span className="text-xs">{trend}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}; 