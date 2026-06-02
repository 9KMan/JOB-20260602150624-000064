import { z } from 'zod';

export const listingSchema = z.object({
  title: z
    .string()
    .min(1, 'Title is required')
    .min(5, 'Title must be at least 5 characters')
    .max(200, 'Title must be less than 200 characters'),
  shortDescription: z
    .string()
    .min(1, 'Short description is required')
    .min(20, 'Short description must be at least 20 characters')
    .max(300, 'Short description must be less than 300 characters'),
  description: z
    .string()
    .min(1, 'Description is required')
    .min(100, 'Description must be at least 100 characters'),
  price: z.number().min(0, 'Price must be a positive number').optional(),
  priceType: z.enum(['fixed', 'hourly', 'starting_at', 'quote']),
  categoryId: z.string().min(1, 'Category is required'),
  locationId: z.string().optional(),
  images: z
    .array(
      z.object({
        url: z.string().url('Invalid image URL'),
        alt: z.string().optional().default(''),
      })
    )
    .min(1, 'At least one image is required')
    .max(10, 'Maximum 10 images allowed'),
  featured: z.boolean().optional().default(false),
  premium: z.boolean().optional().default(false),
  status: z
    .enum(['draft', 'pending', 'active', 'rejected', 'archived'])
    .optional()
    .default('draft'),
});

export const listingUpdateSchema = listingSchema.partial();

export const listingSearchSchema = z.object({
  query: z.string().optional(),
  category: z.string().optional(),
  location: z.string().optional(),
  priceMin: z.coerce.number().min(0).optional(),
  priceMax: z.coerce.number().min(0).optional(),
  rating: z.coerce.number().min(1).max(5).optional(),
  sortBy: z
    .enum(['relevance', 'price_low', 'price_high', 'rating', 'newest'])
    .optional()
    .default('relevance'),
  page: z.coerce.number().min(1).optional().default(1),
  pageSize: z.coerce.number().min(1).max(100).optional().default(20),
});

export const reviewSchema = z.object({
  rating: z.number().min(1, 'Rating is required').max(5, 'Rating must be between 1 and 5'),
  title: z
    .string()
    .min(1, 'Review title is required')
    .min(5, 'Title must be at least 5 characters')
    .max(200, 'Title must be less than 200 characters'),
  content: z
    .string()
    .min(1, 'Review content is required')
    .min(20, 'Review must be at least 20 characters')
    .max(2000, 'Review must be less than 2000 characters'),
  listingId: z.string().min(1, 'Listing ID is required'),
});

export const bookingSchema = z.object({
  listingId: z.string().min(1, 'Listing ID is required'),
  startDate: z.string().min(1, 'Start date is required'),
  endDate: z.string().min(1, 'End date is required'),
  notes: z.string().max(1000, 'Notes must be less than 1000 characters').optional(),
});

export const inquirySchema = z.object({
  listingId: z.string().min(1, 'Listing ID is required'),
  message: z
    .string()
    .min(1, 'Message is required')
    .min(10, 'Message must be at least 10 characters')
    .max(2000, 'Message must be less than 2000 characters'),
});

export type CreateListingInput = z.infer<typeof listingSchema>;
export type UpdateListingInput = z.infer<typeof listingUpdateSchema>;
export type ListingSearchInput = z.infer<typeof listingSearchSchema>;
export type CreateReviewInput = z.infer<typeof reviewSchema>;
export type CreateBookingInput = z.infer<typeof bookingSchema>;
export type CreateInquiryInput = z.infer<typeof inquirySchema>;