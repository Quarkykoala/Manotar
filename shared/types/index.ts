/**
 * Shared type definitions between frontend and backend
 */

/**
 * Employee type shared between frontend and backend
 */
export interface Employee {
  id: number;
  name: string;
  email: string;
  phone_number?: string;
  department?: string;
  location?: string;
  consent_given: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * SentimentSnapshot type for analytics
 */
export interface SentimentSnapshot {
  id: number;
  employee_id: number;
  sentiment_score: number;
  date: string;
  keywords?: string[];
}

/**
 * Filter type for API requests
 */
export interface Filter {
  startDate?: string;
  endDate?: string;
  department?: string;
  location?: string;
}

/**
 * Standard API response payload
 */
export interface ResponsePayload<T> {
  data: T;
  success: boolean;
  message?: string;
  error?: string;
} 