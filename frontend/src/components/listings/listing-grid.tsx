'use client';

import { ListingCard } from './listing-card';
import { Skeleton } from './skeleton';
import type { Listing } from '@/types';

interface ListingGridProps {
  listings: Listing[];
  isLoading?: boolean;
  onFavorite?: (id: string) => void;
  favoritedIds?: Set<string>;
}

export function ListingGrid({
  listings,
  isLoading = false,
  onFavorite,
  favoritedIds = new Set(),
}: ListingGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <ListingCardSkeleton key={i} />
        ))}
      </div>
    );
  }

  if (listings.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="h-16 w-16 rounded-full bg-muted flex items-center justify-center mb-4">
          <svg
            className="h-8 w-8 text-muted-foreground"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
            />
          </svg>
        </div>
        <h3 className="text-lg font-semibold mb-2">No listings found</h3>
        <p className="text-muted-foreground max-w-md">
          We couldn&apos;t find any listings matching your criteria. Try adjusting
          your filters or search terms.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {listings.map((listing) => (
        <ListingCard
          key={listing.id}
          listing={listing}
          onFavorite={onFavorite}
          isFavorited={favoritedIds.has(listing.id)}
        />
      ))}
    </div>
  );
}

function ListingCardSkeleton() {
  return (
    <div className="rounded-lg border bg-card overflow-hidden">
      <div className="aspect-[4/3] bg-muted animate-pulse" />
      <div className="p-4 space-y-3">
        <div className="h-4 w-20 bg-muted animate-pulse rounded" />
        <div className="h-6 w-full bg-muted animate-pulse rounded" />
        <div className="h-4 w-full bg-muted animate-pulse rounded" />
        <div className="h-4 w-2/3 bg-muted animate-pulse rounded" />
        <div className="flex items-center gap-2 pt-2">
          <div className="h-4 w-16 bg-muted animate-pulse rounded" />
          <div className="h-4 w-24 bg-muted animate-pulse rounded" />
        </div>
      </div>
    </div>
  );
}