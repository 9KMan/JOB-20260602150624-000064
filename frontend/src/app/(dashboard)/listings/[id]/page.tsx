'use client';

import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Edit, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { ListingForm } from '@/components/listings/listing-form';

export default function ListingDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const handleSubmit = async (data: unknown) => {
    console.log('Updating listing:', id, data);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/dashboard/listings">
              <ArrowLeft className="h-5 w-5" />
            </Link>
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Edit Listing</h1>
            <p className="text-muted-foreground">
              Update your listing details
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="destructive" size="sm">
            <Trash2 className="mr-2 h-4 w-4" />
            Delete
          </Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Listing Details</CardTitle>
            </CardHeader>
            <CardContent>
              <ListingForm
                onSubmit={handleSubmit}
                isLoading={false}
              />
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Listing Status</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Status</span>
                <Badge variant="warning">Pending Review</Badge>
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Featured</span>
                <Badge variant="secondary">No</Badge>
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Premium</span>
                <Badge variant="secondary">No</Badge>
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Views</span>
                <span className="font-medium">1,234</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Bookings</span>
                <span className="font-medium">48</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button variant="outline" className="w-full justify-start" asChild>
                <Link href={`/listings/${id}`} target="_blank">
                  View Public Page
                </Link>
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <Edit className="mr-2 h-4 w-4" />
                Duplicate Listing
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}