'use client';

import { useState } from 'react';
import Link from 'next/link';
import { PlusCircle, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { ListingCard } from '@/components/listings/listing-card';
import type { Listing } from '@/types';

const mockListings: Listing[] = [
  {
    id: '1',
    title: 'Elite Home Cleaning Services',
    slug: 'elite-home-cleaning',
    description: 'Professional home cleaning...',
    shortDescription: 'Top-rated home cleaning service in the Bay Area',
    price: 89,
    priceType: 'fixed',
    category: { id: '1', name: 'Home Services', slug: 'home-services', description: '', icon: '' },
    images: [{ id: '1', url: 'https://picsum.photos/400/300', alt: '', order: 0, listingId: '1' }],
    featured: true,
    premium: true,
    status: 'active',
    userId: '1',
    averageRating: 4.9,
    reviewCount: 247,
    createdAt: new Date(),
    updatedAt: new Date(),
  },
  {
    id: '2',
    title: 'Professional Photography',
    slug: 'professional-photography',
    description: 'Capturing moments...',
    shortDescription: 'Wedding and event photography services',
    price: 250,
    priceType: 'hourly',
    category: { id: '2', name: 'Events', slug: 'events', description: '', icon: '' },
    images: [{ id: '2', url: 'https://picsum.photos/400/301', alt: '', order: 0, listingId: '2' }],
    featured: false,
    premium: false,
    status: 'active',
    userId: '1',
    averageRating: 4.8,
    reviewCount: 189,
    createdAt: new Date(),
    updatedAt: new Date(),
  },
  {
    id: '3',
    title: 'Expert Plumbing Services',
    slug: 'expert-plumbing',
    description: 'All plumbing needs...',
    shortDescription: '24/7 emergency plumbing repairs',
    price: 120,
    priceType: 'fixed',
    category: { id: '1', name: 'Home Services', slug: 'home-services', description: '', icon: '' },
    images: [{ id: '3', url: 'https://picsum.photos/400/302', alt: '', order: 0, listingId: '3' }],
    featured: false,
    premium: false,
    status: 'pending',
    userId: '1',
    createdAt: new Date(),
    updatedAt: new Date(),
  },
];

export default function ListingsPage() {
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('grid');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const filteredListings = mockListings.filter((listing) => {
    if (statusFilter === 'all') return true;
    return listing.status === statusFilter;
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">My Listings</h1>
          <p className="text-muted-foreground">
            Manage your service listings
          </p>
        </div>
        <Button asChild>
          <Link href="/dashboard/listings/new">
            <PlusCircle className="mr-2 h-4 w-4" />
            Create Listing
          </Link>
        </Button>
      </div>

      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input placeholder="Search listings..." className="pl-10" />
        </div>
        <div className="flex gap-2">
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[150px]">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="active">Active</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="draft">Draft</SelectItem>
              <SelectItem value="archived">Archived</SelectItem>
            </SelectContent>
          </Select>
          <div className="flex border rounded-md">
            <Button
              variant={viewMode === 'grid' ? 'secondary' : 'ghost'}
              size="sm"
              className="rounded-r-none"
              onClick={() => setViewMode('grid')}
            >
              Grid
            </Button>
            <Button
              variant={viewMode === 'table' ? 'secondary' : 'ghost'}
              size="sm"
              className="rounded-l-none"
              onClick={() => setViewMode('table')}
            >
              Table
            </Button>
          </div>
        </div>
      </div>

      {viewMode === 'grid' ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredListings.map((listing) => (
            <ListingCard key={listing.id} listing={listing} />
          ))}
        </div>
      ) : (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Listing</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Price</TableHead>
                <TableHead>Rating</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredListings.map((listing) => (
                <TableRow key={listing.id}>
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <img
                        src={listing.images[0]?.url}
                        alt={listing.title}
                        className="h-10 w-10 rounded-lg object-cover"
                      />
                      <div>
                        <p className="font-medium">{listing.title}</p>
                        <p className="text-sm text-muted-foreground">
                          {listing.shortDescription.slice(0, 40)}...
                        </p>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>{listing.category?.name}</TableCell>
                  <TableCell>
                    <Badge
                      variant={
                        listing.status === 'active'
                          ? 'success'
                          : listing.status === 'pending'
                          ? 'warning'
                          : 'secondary'
                      }
                    >
                      {listing.status}
                    </Badge>
                  </TableCell>
                  <TableCell>${listing.price}</TableCell>
                  <TableCell>
                    {listing.averageRating ? (
                      <span className="flex items-center gap-1">
                        ★ {listing.averageRating}
                        <span className="text-muted-foreground">
                          ({listing.reviewCount})
                        </span>
                      </span>
                    ) : (
                      '-'
                    )}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="sm" asChild>
                      <Link href={`/dashboard/listings/${listing.id}`}>
                        Edit
                      </Link>
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}