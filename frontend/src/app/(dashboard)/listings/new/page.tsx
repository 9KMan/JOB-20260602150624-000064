'use client';

import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ListingForm } from '@/components/listings/listing-form';

export default function NewListingPage() {
  const handleSubmit = async (data: unknown) => {
    console.log('Creating listing:', data);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/dashboard/listings">
            <ArrowLeft className="h-5 w-5" />
          </Link>
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Create New Listing</h1>
          <p className="text-muted-foreground">
            Add a new service to your portfolio
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Listing Information</CardTitle>
        </CardHeader>
        <CardContent>
          <ListingForm onSubmit={handleSubmit} isLoading={false} />
        </CardContent>
      </Card>
    </div>
  );
}