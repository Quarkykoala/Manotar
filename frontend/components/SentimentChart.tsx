import { useEffect, useRef } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartData,
  ChartOptions
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { useTranslation } from '../hooks/useTranslation';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface SentimentDataPoint {
  date: string;
  score: number;
  count: number;
}

interface SentimentChartProps {
  data: SentimentDataPoint[];
  title?: string;
  height?: number;
  width?: number;
}

export const SentimentChart = ({
  data,
  title = 'Sentiment Trends',
  height = 300,
  width = 600
}: SentimentChartProps) => {
  const { t } = useTranslation();
  const chartRef = useRef<ChartJS>(null);

  const chartData: ChartData<'line'> = {
    labels: data.map(d => d.date),
    datasets: [
      {
        label: t('analytics.sentimentScore'),
        data: data.map(d => d.score),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        tension: 0.4,
      },
      {
        label: t('analytics.checkInCompletion'),
        data: data.map(d => d.count),
        borderColor: 'rgb(53, 162, 235)',
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
        tension: 0.4,
      }
    ]
  };

  const options: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: title,
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value) {
            return value.toFixed(1);
          }
        }
      }
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false
    }
  };

  useEffect(() => {
    // Update chart accessibility
    if (chartRef.current) {
      chartRef.current.canvas.setAttribute('role', 'img');
      chartRef.current.canvas.setAttribute('aria-label', 
        t('accessibility.chartDescription', { type: title })
      );
    }
  }, [title, t]);

  return (
    <div 
      className="relative bg-white p-4 rounded-lg shadow"
      style={{ height, width }}
    >
      <Line
        ref={chartRef}
        data={chartData}
        options={options}
        aria-label={t('accessibility.chartDescription', { type: title })}
      />
    </div>
  );
}; 