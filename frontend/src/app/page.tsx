import Link from 'next/link';
import {
  Search,
  CheckCircle,
  Star,
  Shield,
  ArrowRight,
  Menu,
  MapPin,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Header } from '@/components/layout/header';
import { Footer } from '@/components/layout/footer';

const featuredCategories = [
  { name: 'Home Services', count: 1250, icon: '🏠' },
  { name: 'Professional Services', count: 890, icon: '💼' },
  { name: 'Events & Entertainment', count: 654, icon: '🎉' },
  { name: 'Health & Wellness', count: 432, icon: '💪' },
  { name: 'Technology', count: 321, icon: '💻' },
  { name: 'Education', count: 287, icon: '📚' },
];

const featuredListings = [
  {
    id: '1',
    title: 'Elite Home Cleaning Services',
    category: 'Home Services',
    rating: 4.9,
    reviews: 247,
    price: '$89',
    location: 'San Francisco, CA',
    image: 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=400&h=300&fit=crop',
  },
  {
    id: '2',
    title: 'Professional Photography Studio',
    category: 'Events',
    rating: 4.8,
    reviews: 189,
    price: '$250',
    location: 'Los Angeles, CA',
    image: 'https://images.unsplash.com/photo-1554048612-b6a482bc67e5?w=400&h=300&fit=crop',
  },
  {
    id: '3',
    title: 'Expert Plumbing Solutions',
    category: 'Home Services',
    rating: 4.7,
    reviews: 312,
    price: '$120',
    location: 'New York, NY',
    image: 'https://images.unsplash.com/photo-1585704032915-c3400ca199e7?w=400&h=300&fit=crop',
  },
  {
    id: '4',
    title: 'Premium Catering Services',
    category: 'Events',
    rating: 4.9,
    reviews: 156,
    price: '$45/person',
    location: 'Chicago, IL',
    image: 'https://images.unsplash.com/photo-1555244162-803834f70033?w=400&h=300&fit=crop',
  },
];

const trustBadges = [
  {
    icon: Shield,
    title: 'Verified Providers',
    description: 'All service providers are background-checked',
  },
  {
    icon: CheckCircle,
    title: 'Satisfaction Guaranteed',
    description: '100% satisfaction guarantee on all bookings',
  },
  {
    icon: Star,
    title: 'Top Rated',
    description: 'Only the highest-rated professionals make the cut',
  },
];

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 py-20 lg:py-32">
          <div className="container mx-auto px-4">
            <div className="max-w-3xl mx-auto text-center">
              <Badge variant="default" className="mb-4 bg-amber-500">
                #1 Rated Service Directory
              </Badge>
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 tracking-tight">
                Find the Perfect{' '}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-500 to-orange-600">
                  Service Provider
                </span>{' '}
                Near You
              </h1>
              <p className="text-lg md:text-xl text-muted-foreground mb-8">
                Connect with thousands of verified professionals offering
                home services, professional services, events, wellness, and
                more. Quality assured, satisfaction guaranteed.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center max-w-xl mx-auto">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    type="search"
                    placeholder="What service are you looking for?"
                    className="pl-10 h-12 text-base"
                  />
                </div>
                <Button size="lg" className="h-12 px-8">
                  Search
                </Button>
              </div>

              <div className="flex flex-wrap justify-center gap-2 mt-4 text-sm text-muted-foreground">
                <span>Popular:</span>
                <Link href="/listings?category=home-services" className="hover:text-primary">
                  Home Cleaning
                </Link>
                <span>•</span>
                <Link href="/listings?category=professional" className="hover:text-primary">
                  Photography
                </Link>
                <span>•</span>
                <Link href="/listings?category=events" className="hover:text-primary">
                  Catering
                </Link>
                <span>•</span>
                <Link href="/listings?category=wellness" className="hover:text-primary">
                  Personal Training
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Categories Section */}
        <section className="py-16 md:py-24">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold mb-4">Browse Categories</h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                Explore our wide range of service categories to find exactly
                what you need
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {featuredCategories.map((category) => (
                <Link
                  key={category.name}
                  href={`/listings?category=${category.name.toLowerCase().replace(/\s+/g, '-')}`}
                >
                  <div className="flex flex-col items-center p-6 rounded-lg border bg-card hover:border-primary/50 hover:shadow-md transition-all text-center cursor-pointer">
                    <span className="text-4xl mb-3">{category.icon}</span>
                    <h3 className="font-semibold text-sm mb-1">{category.name}</h3>
                    <p className="text-xs text-muted-foreground">
                      {category.count} providers
                    </p>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </section>

        {/* Featured Listings */}
        <section className="py-16 md:py-24 bg-muted/50">
          <div className="container mx-auto px-4">
            <div className="flex items-center justify-between mb-12">
              <div>
                <h2 className="text-3xl font-bold mb-2">Featured Providers</h2>
                <p className="text-muted-foreground">
                  Top-rated service providers you can trust
                </p>
              </div>
              <Button variant="outline" asChild>
                <Link href="/listings">
                  View All
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {featuredListings.map((listing) => (
                <Link
                  key={listing.id}
                  href={`/listings/${listing.id}`}
                  className="group"
                >
                  <div className="rounded-lg overflow-hidden border bg-card hover:shadow-lg transition-shadow">
                    <div className="aspect-[4/3] relative">
                      <img
                        src={listing.image}
                        alt={listing.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                      <Badge className="absolute top-3 left-3 bg-white/90 text-foreground">
                        Featured
                      </Badge>
                    </div>
                    <div className="p-4">
                      <p className="text-sm text-primary mb-1">{listing.category}</p>
                      <h3 className="font-semibold mb-2 line-clamp-1">
                        {listing.title}
                      </h3>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
                        <MapPin className="h-3 w-3" />
                        <span>{listing.location}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1">
                          <Star className="h-4 w-4 fill-amber-400 text-amber-400" />
                          <span className="font-medium">{listing.rating}</span>
                          <span className="text-muted-foreground text-sm">
                            ({listing.reviews})
                          </span>
                        </div>
                        <span className="font-semibold">{listing.price}</span>
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </section>

        {/* Trust Badges */}
        <section className="py-16 md:py-24">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold mb-4">
                Why Choose PremiumServices?
              </h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                We are committed to connecting you with the best service
                providers while ensuring quality and satisfaction
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              {trustBadges.map((badge) => {
                const Icon = badge.icon;
                return (
                  <div
                    key={badge.title}
                    className="flex flex-col items-center text-center p-6"
                  >
                    <div className="h-16 w-16 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center mb-4">
                      <Icon className="h-8 w-8 text-amber-600 dark:text-amber-400" />
                    </div>
                    <h3 className="text-xl font-semibold mb-2">{badge.title}</h3>
                    <p className="text-muted-foreground">{badge.description}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-16 md:py-24 bg-gradient-to-br from-amber-500 to-orange-600 text-white">
          <div className="container mx-auto px-4 text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Are You a Service Provider?
            </h2>
            <p className="text-lg opacity-90 mb-8 max-w-2xl mx-auto">
              Join our network of verified professionals and grow your
              business. Get access to thousands of potential customers.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                size="lg"
                variant="secondary"
                asChild
                className="text-amber-600"
              >
                <Link href="/register?role=provider">Start Free Trial</Link>
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="bg-white/10 border-white/20 text-white hover:bg-white/20"
                asChild
              >
                <Link href="/contact">Contact Sales</Link>
              </Button>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}