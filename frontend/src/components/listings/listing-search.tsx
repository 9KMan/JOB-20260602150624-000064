'use client';

import { useState, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Search, SlidersHorizontal, X, MapPin, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet';
import { Checkbox } from '@/components/ui/checkbox';
import { cn } from '@/lib/utils';

const categories = [
  { value: 'home-services', label: 'Home Services' },
  { value: 'professional', label: 'Professional Services' },
  { value: 'events', label: 'Events' },
  { value: 'wellness', label: 'Wellness' },
  { value: 'technology', label: 'Technology' },
  { value: 'education', label: 'Education' },
];

const locations = [
  { value: 'san-francisco', label: 'San Francisco, CA' },
  { value: 'los-angeles', label: 'Los Angeles, CA' },
  { value: 'new-york', label: 'New York, NY' },
  { value: 'chicago', label: 'Chicago, IL' },
  { value: 'austin', label: 'Austin, TX' },
];

const sortOptions = [
  { value: 'relevance', label: 'Most Relevant' },
  { value: 'price_low', label: 'Price: Low to High' },
  { value: 'price_high', label: 'Price: High to Low' },
  { value: 'rating', label: 'Highest Rated' },
  { value: 'newest', label: 'Newest First' },
];

interface SearchFilters {
  query: string;
  category: string;
  location: string;
  priceMin: number;
  priceMax: number;
  rating: number;
  sortBy: string;
}

interface ListingSearchProps {
  onSearch?: (filters: SearchFilters) => void;
  initialFilters?: Partial<SearchFilters>;
}

export function ListingSearch({ onSearch, initialFilters }: ListingSearchProps) {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [searchInput, setSearchInput] = useState(
    initialFilters?.query || searchParams.get('q') || ''
  );
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<SearchFilters>({
    query: initialFilters?.query || '',
    category: initialFilters?.category || searchParams.get('category') || '',
    location: initialFilters?.location || searchParams.get('location') || '',
    priceMin: initialFilters?.priceMin || 0,
    priceMax: initialFilters?.priceMax || 1000,
    rating: initialFilters?.rating || 0,
    sortBy: initialFilters?.sortBy || 'relevance',
  });

  const activeFilterCount = [
    filters.category,
    filters.location,
    filters.priceMin > 0 || filters.priceMax < 1000,
    filters.rating > 0,
  ].filter(Boolean).length;

  const handleSearch = useCallback(() => {
    const params = new URLSearchParams();
    if (searchInput) params.set('q', searchInput);
    if (filters.category) params.set('category', filters.category);
    if (filters.location) params.set('location', filters.location);
    if (filters.priceMax < 1000) {
      params.set('priceMax', filters.priceMax.toString());
    }
    if (filters.rating > 0) {
      params.set('rating', filters.rating.toString());
    }
    if (filters.sortBy !== 'relevance') {
      params.set('sort', filters.sortBy);
    }

    router.push(`/listings?${params.toString()}`);
    onSearch?.(filters);
  }, [searchInput, filters, router, onSearch]);

  const clearFilters = () => {
    setFilters({
      query: '',
      category: '',
      location: '',
      priceMin: 0,
      priceMax: 1000,
      rating: 0,
      sortBy: 'relevance',
    });
    setSearchInput('');
    router.push('/listings');
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-4 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search services..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            className="pl-10"
          />
        </div>

        <div className="flex gap-2">
          <Select
            value={filters.sortBy}
            onValueChange={(value) =>
              setFilters((f) => ({ ...f, sortBy: value }))
            }
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              {sortOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Sheet open={showFilters} onOpenChange={setShowFilters}>
            <SheetTrigger asChild>
              <Button variant="outline" className="relative">
                <SlidersHorizontal className="mr-2 h-4 w-4" />
                Filters
                {activeFilterCount > 0 && (
                  <Badge
                    variant="default"
                    className="ml-2 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs"
                  >
                    {activeFilterCount}
                  </Badge>
                )}
              </Button>
            </SheetTrigger>
            <SheetContent className="w-full sm:max-w-lg">
              <SheetHeader>
                <SheetTitle>Filters</SheetTitle>
              </SheetHeader>
              <div className="py-6 space-y-6">
                <div className="space-y-2">
                  <Label>Category</Label>
                  <Select
                    value={filters.category}
                    onValueChange={(value) =>
                      setFilters((f) => ({ ...f, category: value }))
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="All categories" />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map((cat) => (
                        <SelectItem key={cat.value} value={cat.value}>
                          {cat.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Location</Label>
                  <Select
                    value={filters.location}
                    onValueChange={(value) =>
                      setFilters((f) => ({ ...f, location: value }))
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Any location" />
                    </SelectTrigger>
                    <SelectContent>
                      {locations.map((loc) => (
                        <SelectItem key={loc.value} value={loc.value}>
                          {loc.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Price Range</Label>
                  <Slider
                    min={0}
                    max={1000}
                    step={10}
                    value={[filters.priceMin, filters.priceMax]}
                    onValueChange={([min, max]) =>
                      setFilters((f) => ({
                        ...f,
                        priceMin: min,
                        priceMax: max,
                      }))
                    }
                  />
                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>${filters.priceMin}</span>
                    <span>${filters.priceMax}{filters.priceMax >= 1000 ? '+' : ''}</span>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Minimum Rating</Label>
                  <div className="flex gap-2">
                    {[0, 3, 4, 4.5].map((rating) => (
                      <Button
                        key={rating}
                        variant={filters.rating === rating ? 'default' : 'outline'}
                        size="sm"
                        onClick={() =>
                          setFilters((f) => ({ ...f, rating }))
                        }
                      >
                        {rating === 0 ? 'Any' : `${rating}+`}
                      </Button>
                    ))}
                  </div>
                </div>

                <div className="flex gap-2 pt-4 border-t">
                  <Button
                    variant="outline"
                    onClick={clearFilters}
                    className="flex-1"
                  >
                    Clear All
                  </Button>
                  <Button onClick={handleSearch} className="flex-1">
                    Apply Filters
                  </Button>
                </div>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>

      {activeFilterCount > 0 && (
        <div className="flex flex-wrap gap-2">
          {filters.category && (
            <Badge variant="secondary" className="gap-1">
              {categories.find((c) => c.value === filters.category)?.label}
              <X
                className="h-3 w-3 cursor-pointer"
                onClick={() =>
                  setFilters((f) => ({ ...f, category: '' }))
                }
              />
            </Badge>
          )}
          {filters.location && (
            <Badge variant="secondary" className="gap-1">
              {locations.find((l) => l.value === filters.location)?.label}
              <X
                className="h-3 w-3 cursor-pointer"
                onClick={() =>
                  setFilters((f) => ({ ...f, location: '' }))
                }
              />
            </Badge>
          )}
          {(filters.priceMin > 0 || filters.priceMax < 1000) && (
            <Badge variant="secondary" className="gap-1">
              ${filters.priceMin} - ${filters.priceMax}
              <X
                className="h-3 w-3 cursor-pointer"
                onClick={() =>
                  setFilters((f) => ({
                    ...f,
                    priceMin: 0,
                    priceMax: 1000,
                  }))
                }
              />
            </Badge>
          )}
          {filters.rating > 0 && (
            <Badge variant="secondary" className="gap-1">
              {filters.rating}+ stars
              <X
                className="h-3 w-3 cursor-pointer"
                onClick={() => setFilters((f) => ({ ...f, rating: 0 }))}
              />
            </Badge>
          )}
        </div>
      )}
    </div>
  );
}