'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiGet, apiPost, apiPut, apiPatch, apiDelete } from '@/lib/api';
import type { Listing, ListingSearchInput, ApiResponse, PaginatedResponse } from '@/types';

interface UseListingsOptions {
  page?: number;
  pageSize?: number;
  category?: string;
  location?: string;
  search?: string;
}

export function useListings(options: UseListingsOptions = {}) {
  const { page = 1, pageSize = 20, category, location, search } = options;

  return useQuery({
    queryKey: ['listings', { page, pageSize, category, location, search }],
    queryFn: async () => {
      const params = new URLSearchParams();
      params.append('page', page.toString());
      params.append('pageSize', pageSize.toString());
      if (category) params.append('category', category);
      if (location) params.append('location', location);
      if (search) params.append('search', search);

      return apiGet<PaginatedResponse<Listing>>(`/listings?${params.toString()}`);
    },
    staleTime: 1000 * 60 * 5,
  });
}

export function useFeaturedListings() {
  return useQuery({
    queryKey: ['listings', 'featured'],
    queryFn: () => apiGet<Listing[]>('/listings/featured'),
    staleTime: 1000 * 60 * 5,
  });
}

export function useListing(id: string) {
  return useQuery({
    queryKey: ['listing', id],
    queryFn: () => apiGet<Listing>(`/listings/${id}`),
    enabled: !!id,
  });
}

export function useCreateListing() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<Listing>) => apiPost<Listing>('/listings', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['listings'] });
    },
  });
}

export function useUpdateListing() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Listing> }) =>
      apiPut<Listing>(`/listings/${id}`, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['listing', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['listings'] });
    },
  });
}

export function useDeleteListing() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => apiDelete<void>(`/listings/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['listings'] });
    },
  });
}

export function useSearchListings(searchInput: ListingSearchInput) {
  return useQuery({
    queryKey: ['listings', 'search', searchInput],
    queryFn: () => apiPost<PaginatedResponse<Listing>>('/listings/search', searchInput),
    enabled: !!searchInput.query || !!searchInput.category || !!searchInput.location,
  });
}

export function useUserListings() {
  return useQuery({
    queryKey: ['listings', 'my-listings'],
    queryFn: () => apiGet<Listing[]>('/listings/user/me'),
    staleTime: 1000 * 60 * 2,
  });
}