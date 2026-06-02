export interface User {
  id: string;
  name: string | null;
  email: string;
  emailVerified: Date | null;
  image: string | null;
  role: 'user' | 'admin' | 'provider';
  createdAt: Date;
  updatedAt: Date;
}

export interface Listing {
  id: string;
  title: string;
  slug: string;
  description: string;
  shortDescription: string;
  price: number;
  priceType: 'fixed' | 'hourly' | 'starting_at' | 'quote';
  category: Category;
  categoryId: string;
  images: ListingImage[];
  featured: boolean;
  premium: boolean;
  status: 'draft' | 'pending' | 'active' | 'rejected' | 'archived';
  userId: string;
  user?: User;
  location?: Location;
  locationId?: string;
  reviews?: Review[];
  averageRating?: number;
  reviewCount?: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface ListingImage {
  id: string;
  url: string;
  alt: string;
  order: number;
  listingId: string;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  description: string;
  icon: string;
  parentId: string | null;
  children?: Category[];
  listingCount?: number;
  createdAt: Date;
}

export interface Location {
  id: string;
  name: string;
  slug: string;
  type: 'city' | 'state' | 'country';
  parentId: string | null;
  listings?: Listing[];
  createdAt: Date;
}

export interface Review {
  id: string;
  rating: number;
  title: string;
  content: string;
  listingId: string;
  userId: string;
  user?: User;
  helpful: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface Booking {
  id: string;
  listingId: string;
  listing?: Listing;
  userId: string;
  user?: User;
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled' | 'refunded';
  startDate: Date;
  endDate: Date;
  totalPrice: number;
  notes: string | null;
  createdAt: Date;
  updatedAt: Date;
}

export interface Message {
  id: string;
  conversationId: string;
  senderId: string;
  sender?: User;
  content: string;
  read: boolean;
  createdAt: Date;
}

export interface Conversation {
  id: string;
  participants: User[];
  lastMessage?: Message;
  listingId: string;
  listing?: Listing;
  createdAt: Date;
  updatedAt: Date;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  meta?: {
    page?: number;
    pageSize?: number;
    total?: number;
    totalPages?: number;
  };
}

export interface ApiError {
  message: string;
  code?: string;
  statusCode: number;
  errors?: Record<string, string[]>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface SearchFilters {
  query?: string;
  category?: string;
  location?: string;
  priceMin?: number;
  priceMax?: number;
  rating?: number;
  sortBy?: 'relevance' | 'price_low' | 'price_high' | 'rating' | 'newest';
}

export interface DashboardStats {
  totalListings: number;
  activeListings: number;
  totalReviews: number;
  averageRating: number;
  totalBookings: number;
  pendingBookings: number;
  totalEarnings: number;
  thisMonthEarnings: number;
  profileViews: number;
  conversionRate: number;
}

export interface RecentActivity {
  id: string;
  type: 'review' | 'booking' | 'inquiry' | 'listing_update' | 'payment';
  title: string;
  description: string;
  timestamp: Date;
  read: boolean;
}

export interface AuthSession {
  user: User;
  expires: string;
}