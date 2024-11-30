import axios, { AxiosError } from 'axios';
import { TEST_CONFIG } from '../config/test.config';

// Define types for API responses
export interface KeywordStat {
  keyword: string;
  total_count: number;
}

export interface LoginResponse {
  success: boolean;
  token?: string;
  error?: string;
}

export interface ApiError {
  message: string;
  code?: string;
}

const API_URL = process.env.REACT_APP_API_URL || TEST_CONFIG.API_URL;

export const api = {
  login: async (username: string, password: string): Promise<LoginResponse> => {
    try {
      const response = await axios.post(`${API_URL}/hr/login`, {
        username,
        password
      });
      return response.data;
    } catch (error) {
      const axiosError = error as AxiosError<ApiError>;
      throw {
        message: axiosError.response?.data?.message || 'Login failed',
        code: axiosError.response?.status.toString()
      };
    }
  },

  getKeywordStats: async (): Promise<KeywordStat[]> => {
    try {
      const response = await axios.get(`${API_URL}/api/keyword-stats`);
      return response.data;
    } catch (error) {
      const axiosError = error as AxiosError<ApiError>;
      throw {
        message: axiosError.response?.data?.message || 'Failed to fetch keyword stats',
        code: axiosError.response?.status.toString()
      };
    }
  }
}; 