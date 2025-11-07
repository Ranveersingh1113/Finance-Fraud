/**
 * React Query hooks for user profile
 */

import { useQuery } from '@tanstack/react-query';
import { userApi } from '@/services/api';

// User profile
export function useUserProfile() {
  return useQuery({
    queryKey: ['user', 'profile'],
    queryFn: () => userApi.getProfile(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });
}


