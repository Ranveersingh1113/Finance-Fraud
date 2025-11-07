/**
 * React Query hooks for search functionality
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { searchApi } from '@/services/api';
import type { QueryRequest } from '@/types/api';
import { toast } from 'sonner';

export function useUnifiedSearch() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: QueryRequest) => searchApi.unifiedQuery(request),
    onSuccess: (data) => {
      // Cache the result
      queryClient.setQueryData(['search', data.query], data);
      toast.success(`Search completed in ${data.processing_time.toFixed(2)}s`);
    },
    onError: (error: any) => {
      toast.error(error.message || 'Search failed. Please try again.');
    },
  });
}

