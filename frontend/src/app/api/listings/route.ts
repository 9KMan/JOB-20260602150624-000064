import { NextResponse } from 'next/server';
import type { Listing } from '@/types';

const mockListings: Listing[] = [
  {
    id: '1',
    title: 'Elite Home Cleaning Services',
    slug: 'elite-home-cleaning',
    description: 'Professional home cleaning with eco-friendly products',
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
];

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const category = searchParams.get('category');
  const location = searchParams.get('location');
  const search = searchParams.get('search');
  const page = parseInt(searchParams.get('page') || '1');
  const pageSize = parseInt(searchParams.get('pageSize') || '20');

  let filteredListings = [...mockListings];

  if (category) {
    filteredListings = filteredListings.filter(
      (l) => l.category.slug === category || l.category.name.toLowerCase().includes(category.toLowerCase())
    );
  }

  if (search) {
    const searchLower = search.toLowerCase();
    filteredListings = filteredListings.filter(
      (l) =>
        l.title.toLowerCase().includes(searchLower) ||
        l.shortDescription.toLowerCase().includes(searchLower)
    );
  }

  const start = (page - 1) * pageSize;
  const end = start + pageSize;
  const paginatedListings = filteredListings.slice(start, end);

  return NextResponse.json({
    items: paginatedListings,
    total: filteredListings.length,
    page,
    pageSize,
    totalPages: Math.ceil(filteredListings.length / pageSize),
  });
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const newListing: Listing = {
      id: Math.random().toString(36).substring(7),
      ...body,
      status: 'pending',
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    return NextResponse.json(newListing, { status: 201 });
  } catch {
    return NextResponse.json(
      { message: 'Invalid request body' },
      { status: 400 }
    );
  }
}