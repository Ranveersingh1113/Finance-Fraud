/**
 * React Query hooks for case management
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { casesApi, sarApi } from '@/services/api';
import type { Case, CreateCaseRequest } from '@/types/api';
import { toast } from 'sonner';

// Get all cases
export function useCases(status?: string) {
  return useQuery({
    queryKey: ['cases', status],
    queryFn: () => casesApi.getAll(status),
    staleTime: 30000, // 30 seconds
    retry: 1, // Only retry once
    retryDelay: 1000, // Wait 1 second before retry
  });
}

// Get single case
export function useCase(caseId: string | undefined) {
  return useQuery({
    queryKey: ['case', caseId],
    queryFn: () => casesApi.getById(caseId!),
    enabled: !!caseId,
  });
}

// Create case mutation
export function useCreateCase() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: CreateCaseRequest) => casesApi.create(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cases'] });
      toast.success('Case created successfully!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to create case');
    },
  });
}

// Delete case mutation
export function useDeleteCase() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (caseId: string) => casesApi.delete(caseId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cases'] });
      toast.success('Case deleted successfully!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to delete case');
    },
  });
}

// Analyze case mutation
export function useAnalyzeCase() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ caseId, query }: { caseId: string; query: string }) =>
      casesApi.analyze(caseId, query),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['case', variables.caseId] });
      queryClient.invalidateQueries({ queryKey: ['cases'] });
      toast.success('Analysis completed!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Analysis failed');
    },
  });
}

// Generate SAR mutation
export function useGenerateSAR() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (caseId: string) => sarApi.generate(caseId),
    onSuccess: (data, caseId) => {
      queryClient.invalidateQueries({ queryKey: ['case', caseId] });
      queryClient.invalidateQueries({ queryKey: ['sar', caseId] });
      toast.success('SAR generated successfully!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to generate SAR');
    },
  });
}

// Get SAR reports
export function useSARReports(caseId: string | undefined) {
  return useQuery({
    queryKey: ['sar', caseId],
    queryFn: () => sarApi.getReports(caseId!),
    enabled: !!caseId,
  });
}

