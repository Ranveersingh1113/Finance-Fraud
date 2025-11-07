/**
 * API Service Layer
 * All backend API calls organized by feature
 */

import { apiClient } from '@/lib/api-client';
import type {
  QueryRequest,
  QueryResponse,
  Case,
  CreateCaseRequest,
  CaseResponse,
  SARResponse,
  SystemStats,
  HealthResponse,
  UserProfile,
} from '@/types/api';

// Health & System
export const healthApi = {
  check: () => apiClient.get<HealthResponse>('/health'),
  getStats: () => apiClient.get<SystemStats>('/stats'),
};

// Search & Query
export const searchApi = {
  unifiedQuery: (request: QueryRequest) =>
    apiClient.post<QueryResponse>('/query/unified', request),
  
  simpleQuery: (query: string, nResults: number = 5) =>
    apiClient.get<any>(`/query/simple?query=${encodeURIComponent(query)}&n_results=${nResults}`),
};

// Case Management
export const casesApi = {
  getAll: (status?: string) => {
    const params = status ? `?status=${status}` : '';
    return apiClient.get<{ cases: Case[]; count: number }>(`/cases${params}`);
  },

  getById: (caseId: string) =>
    apiClient.get<Case>(`/cases/${caseId}`),

  create: (request: CreateCaseRequest) =>
    apiClient.post<CaseResponse>('/cases', request),

  delete: (caseId: string) =>
    apiClient.delete<{ message: string }>(`/cases/${caseId}`),

  analyze: (caseId: string, query: string) =>
    apiClient.post<any>(`/cases/${caseId}/analyze?query=${encodeURIComponent(query)}`),
};

// SAR Generation
export const sarApi = {
  generate: (caseId: string) =>
    apiClient.post<SARResponse>(`/cases/${caseId}/sar`),

  getReports: (caseId: string) =>
    apiClient.get<{ reports: any[]; count: number }>(`/cases/${caseId}/sar`),
};

// User Profile
export const userApi = {
  getProfile: () => apiClient.get<UserProfile>('/user/profile'),
};

