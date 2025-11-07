/**
 * React Query hooks for system statistics
 */

import { useQuery } from '@tanstack/react-query';
import { healthApi } from '@/services/api';

// Health check
export function useHealthCheck() {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => healthApi.check(),
    staleTime: 60000, // 1 minute
    retry: 3,
  });
}

// System statistics
export function useSystemStats() {
  return useQuery({
    queryKey: ['stats'],
    queryFn: () => healthApi.getStats(),
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // Refetch every minute
    retry: 1, // Only retry once
    retryDelay: 1000, // Wait 1 second before retry
  });
}

