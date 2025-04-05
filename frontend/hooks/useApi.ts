import { useState, useCallback } from 'react';
import { useTranslation } from './useTranslation';

interface ApiError extends Error {
  status?: number;
  data?: any;
}

interface ApiResponse<T> {
  data: T | null;
  error: ApiError | null;
  loading: boolean;
  execute: (...args: any[]) => Promise<T | null>;
}

interface ApiOptions {
  onSuccess?: (data: any) => void;
  onError?: (error: ApiError) => void;
  transform?: (data: any) => any;
}

export function useApi<T = any>(
  apiFunction: (...args: any[]) => Promise<T>,
  options: ApiOptions = {}
): ApiResponse<T> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const { t } = useTranslation();

  const execute = useCallback(
    async (...args: any[]) => {
      try {
        setLoading(true);
        setError(null);

        const response = await apiFunction(...args);
        const transformedData = options.transform ? options.transform(response) : response;

        setData(transformedData);
        options.onSuccess?.(transformedData);

        return transformedData;
      } catch (err) {
        const apiError: ApiError = err instanceof Error ? err : new Error(t('errors.fetchFailed'));
        
        if (err instanceof Response) {
          apiError.status = err.status;
          try {
            apiError.data = await err.json();
          } catch {
            // If JSON parsing fails, use status text
            apiError.message = err.statusText || t('errors.fetchFailed');
          }
        }

        setError(apiError);
        options.onError?.(apiError);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiFunction, options, t]
  );

  return {
    data,
    error,
    loading,
    execute
  };
}

// Helper function to create a debounced version of useApi
export function useDebouncedApi<T = any>(
  apiFunction: (...args: any[]) => Promise<T>,
  delay: number = 300,
  options: ApiOptions = {}
): ApiResponse<T> {
  const [debouncedExecute] = useState(() => {
    let timeoutId: NodeJS.Timeout;
    
    return (...args: any[]) => {
      return new Promise<T | null>((resolve) => {
        if (timeoutId) {
          clearTimeout(timeoutId);
        }

        timeoutId = setTimeout(async () => {
          try {
            const result = await apiFunction(...args);
            resolve(result);
          } catch (error) {
            resolve(null);
          }
        }, delay);
      });
    };
  });

  return useApi(debouncedExecute, options);
}

// Helper function to create a cached version of useApi
export function useCachedApi<T = any>(
  apiFunction: (...args: any[]) => Promise<T>,
  cacheKey: string,
  options: ApiOptions = {}
): ApiResponse<T> {
  const [cache] = useState(() => new Map<string, T>());

  const cachedApiFunction = async (...args: any[]) => {
    const key = `${cacheKey}-${JSON.stringify(args)}`;
    
    if (cache.has(key)) {
      return cache.get(key)!;
    }

    const result = await apiFunction(...args);
    cache.set(key, result);
    return result;
  };

  return useApi(cachedApiFunction, options);
}