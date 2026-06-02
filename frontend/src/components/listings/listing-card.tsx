'use client';

import Image from 'next/image';
import Link from 'next/link';
import { MapPin, Star, Heart } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { cn, formatCurrency } from '@/lib/utils';
import type { Listing } from '@/types';

interface ListingCardProps {
  listing: Listing;
  variant?: 'default' | 'compact';
  onFavorite?: (id: string) => void;
  isFavorited?: boolean;
}

export function ListingCard({
  listing,
  variant = 'default',
  onFavorite,
  isFavorited = false,
}: ListingCardProps) {
  const {
    title,
    slug,
    shortDescription,
    price,
    priceType,
    images,
    category,
    location,
    averageRating,
    reviewCount,
    premium,
    featured,
  } = listing;

  const mainImage = images?.[0]?.url || 'https://picsum.photos/seed/listing/400/300';
  const priceDisplay =
    priceType === 'quote'
      ? 'Quote'
      : priceType === 'starting_at'
      ? `From ${formatCurrency(price ?? 0)}`
      : formatCurrency(price ?? 0);

  if (variant === 'compact') {
    return (
      <Link href={`/listings/${slug || listing.id}`}>
        <Card className="overflow-hidden hover:shadow-lg transition-shadow">
          <div className="flex gap-4 p-4">
            <div className="relative h-20 w-20 shrink-0 overflow-hidden rounded-lg">
              <Image
                src={mainImage}
                alt={title}
                fill
                className="object-cover"
              />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold truncate">{title}</h3>
              <p className="text-sm text-muted-foreground truncate">
                {category?.name}
              </p>
              <div className="flex items-center gap-2 mt-1">
                {averageRating && (
                  <span className="flex items-center gap-1 text-sm">
                    <Star className="h-3 w-3 fill-amber-400 text-amber-400" />
                    {averageRating.toFixed(1)}
                  </span>
                )}
                <span className="text-sm font-medium">{priceDisplay}</span>
              </div>
            </div>
          </div>
        </Card>
      </Link>
    );
  }

  return (
    <Card className="overflow-hidden hover:shadow-lg transition-all duration-300 group">
      <div className="relative aspect-[4/3] overflow-hidden">
        <Image
          src={mainImage}
          alt={title}
          fill
          className="object-cover group-hover:scale-105 transition-transform duration-500"
        />
        <div className="absolute top-3 left-3 flex gap-2">
          {featured && (
            <Badge variant="default" className="bg-blue-500">
              Featured
            </Badge>
          )}
          {premium && <Badge variant="premium">Premium</Badge>}
        </div>
        <Button
          variant="ghost"
          size="icon"
          className="absolute top-3 right-3 bg-white/80 hover:bg-white/90"
          onClick={(e) => {
            e.preventDefault();
            onFavorite?.(listing.id);
          }}
        >
          <Heart
            className={cn(
              'h-5 w-5',
              isFavorited
                ? 'fill-red-500 text-red-500'
                : 'text-muted-foreground'
            )}
          />
        </Button>
      </div>

      <CardContent className="p-4">
        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
          <span className="text-primary font-medium">{category?.name}</span>
          {location && (
            <>
              <span>•</span>
              <span className="flex items-center gap-1">
                <MapPin className="h-3 w-3" />
                {location.name}
              </span>
            </>
          )}
        </div>

        <Link href={`/listings/${slug || listing.id}`}>
          <h3 className="font-semibold text-lg mb-2 line-clamp-1 hover:text-primary transition-colors">
            {title}
          </h3>
        </Link>

        <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
          {shortDescription}
        </p>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {averageRating && (
              <span className="flex items-center gap-1 text-sm">
                <Star className="h-4 w-4 fill-amber-400 text-amber-400" />
                <span className="font-medium">{averageRating.toFixed(1)}</span>
                <span className="text-muted-foreground">
                  ({reviewCount} reviews)
                </span>
              </span>
            )}
          </div>
        </div>

        <div className="mt-3 pt-3 border-t">
          <span className="text-lg font-bold">{priceDisplay}</span>
          {priceType === 'hourly' && (
            <span className="text-sm text-muted-foreground">/hour</span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}