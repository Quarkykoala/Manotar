export interface SentimentDataPoint {
  date: string;
  score: number;
  count: number;
  department?: string;
}

export interface DepartmentMetrics {
  departmentId: string;
  departmentName: string;
  averageScore: number;
  participationRate: number;
  riskLevel: RiskLevel;
  trendDirection: TrendDirection;
  checkInCount: number;
}

export interface RiskAlert {
  id: string;
  departmentId: string;
  departmentName: string;
  riskLevel: RiskLevel;
  message: string;
  createdAt: string;
  acknowledgedAt?: string;
}

export enum RiskLevel {
  Low = 'low',
  Medium = 'medium',
  High = 'high',
  Critical = 'critical'
}

export enum TrendDirection {
  Improving = 'improving',
  Declining = 'declining',
  Stable = 'stable'
}

export interface SentimentAnalysisResponse {
  sentiment: {
    score: number;
    magnitude: number;
    label: string;
  };
  entities: Array<{
    name: string;
    type: string;
    sentiment: number;
  }>;
  language: string;
}

export interface SentimentFilter {
  startDate?: string;
  endDate?: string;
  department?: string;
  minScore?: number;
  maxScore?: number;
}

export interface SentimentStats {
  average: number;
  median: number;
  mode: number;
  standardDeviation: number;
  participationRate: number;
  totalResponses: number;
}

// Helper functions for sentiment analysis
export const calculateRiskLevel = (score: number): RiskLevel => {
  if (score < 0.3) return RiskLevel.Critical;
  if (score < 0.5) return RiskLevel.High;
  if (score < 0.7) return RiskLevel.Medium;
  return RiskLevel.Low;
};

export const calculateTrendDirection = (
  currentScore: number,
  previousScore: number,
  threshold: number = 0.1
): TrendDirection => {
  const difference = currentScore - previousScore;
  if (Math.abs(difference) <= threshold) return TrendDirection.Stable;
  return difference > 0 ? TrendDirection.Improving : TrendDirection.Declining;
};

export const formatSentimentScore = (score: number): string => {
  return (score * 100).toFixed(1) + '%';
}; 