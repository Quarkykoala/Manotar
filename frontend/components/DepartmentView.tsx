import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ResponsiveContainer, LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';
import { CustomTooltip } from './CustomTooltip';
import { motion } from 'framer-motion';

interface DepartmentViewProps {
  department: string;
  data: {
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
  };
}

export const DepartmentView = ({ department, data }: DepartmentViewProps) => {
  const metricsData = Object.entries(data.key_metrics).map(([key, value]) => ({
    name: key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '),
    value
  }));

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Employees</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.total_employees}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Mental Health Score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.mental_health_score}</div>
            <p className="text-xs text-muted-foreground">{data.trend}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Risk Level</CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${
              data.risk_level === 'High' ? 'text-red-500' :
              data.risk_level === 'Medium' ? 'text-yellow-500' :
              'text-green-500'
            }`}>
              {data.risk_level}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Key Metrics</CardTitle>
          <CardDescription>Department performance indicators</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={metricsData}>
                <XAxis dataKey="name" />
                <YAxis domain={[0, 10]} />
                <Tooltip content={<CustomTooltip />} />
                <Bar
                  dataKey="value"
                  fill="#2e86de"
                  animationDuration={1000}
                >
                  {metricsData.map((entry, index) => (
                    <motion.rect
                      key={`bar-${index}`}
                      whileHover={{
                        y: -5,
                        transition: { duration: 0.2 }
                      }}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Common Keywords</CardTitle>
          <CardDescription>Most discussed topics</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {data.recent_keywords.map((keyword, index) => (
              <motion.div
                key={keyword.word}
                className="px-3 py-1 rounded-full bg-primary/10 text-primary"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.05 }}
              >
                {keyword.word} ({keyword.count})
              </motion.div>
            ))}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}; 