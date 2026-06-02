import { NextResponse } from 'next/server';
import type { Listing } from '@/types';

const mockListing: Listing = {
  id: '1',
  title: 'Elite Home Cleaning Services',
  slug: 'elite-home-cleaning',
  description: 'Professional home cleaning with eco-friendly products. Our team of trained professionals provides top-quality cleaning services for homes of all sizes. We use only environmentally friendly cleaning products that are safe for your family and pets.',
  shortDescription: 'Top-rated home cleaning service in the Bay Area',
  price: 89,
  priceType: 'fixed',
  category: { id: '1', name: 'Home Services', slug: 'home-services', description: '', icon: '' },
  images: [
    { id: '1', url: 'https://picsum.photos/800/600', alt: 'Clean home interior', order: 0, listingId: '1' },
    { id: '2', url: 'https://picsum.photos/800/601', alt: 'Professional cleaning', order: 1, listingId: '1' },
    { id: '3', url: 'https://picsum.photos/800/602', alt: 'Happy customer', order: 2, listingId: '1' },
  ],
  featured: true,
  premium: true,
  status: 'active',
  userId: '1',
  user: {
    id: '1',
    name: 'John Smith',
    email: 'john@example.com',
    image: 'https://picsum.photos/100/100',
    role: 'provider',
    emailVerified: new Date(),
    createdAt: new Date(),
    updatedAt: new Date(),
  },
  location: {
    id: '1',
    name: 'San Francisco, CA',
    slug: 'san-francisco-ca',
    type: 'city',
    parentId: null,
    createdAt: new Date(),
  },
  averageRating: 4.9,
  reviewCount: 247,
  createdAt: new Date(),
  updatedAt: new Date(),
};

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  const id = params.id;

  if (id === mockListing.id || id === mockListing.slug) {
    return NextResponse.json(mockListing);
  }

  return NextResponse.json(
    { message: 'Listing not found' },
    { status: 404 }
  );
}

export async function PUT(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json();
    const updatedListing: Listing = {
      ...mockListing,
      ...body,
      id: params.id,
      updatedAt: new Date(),
    };
    return NextResponse.json(updatedListing);
  } catch {
    return NextResponse.json(
      { message: 'Invalid request body' },
      { status: 400 }
    );
  }
}

export async function DELETE(
  request: Request,
  { params }: { params: { id: string } }
) {
  return NextResponse.json(
    { message: 'Listing deleted successfully' },
    { status: 200 }
  );
}