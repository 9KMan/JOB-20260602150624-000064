'use client';

import { useSession } from 'next-auth/react';
import { StatsCard } from '@/components/dashboard/stats-card';
import { RecentActivityList } from '@/components/dashboard/recent-activity';
import { QuickActions } from '@/components/dashboard/quick-actions';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { DollarSign, Eye, List, Star, Users } from 'lucide-react';
import type { RecentActivity } from '@/types';

const mockActivities: RecentActivity[] = [
  {
    id: '1',
    type: 'booking',
    title: 'New Booking Received',
    description: 'Someone booked "Elite Home Cleaning" for tomorrow',
    createdAt: new Date(Date.now() - 1000 * 60 * 30),
    read: false,
  },
  {
    id: '2',
    type: 'review',
    title: 'New Review',
    description: 'You received a 5-star review from John D.',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2),
    read: false,
  },
  {
    id: '3',
    type: 'inquiry',
    title: 'New Inquiry',
    description: 'Sarah M. asked about your photography services',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 5),
    read: true,
  },
  {
    id: '4',
    type: 'payment',
    title: 'Payment Received',
    description: 'You earned $250 for completed service',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24),
    read: true,
  },
];

export default function DashboardPage() {
  const { data: session } = useSession();

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold mb-2">
          Welcome back, {session?.user?.name?.split(' ')[0] || 'User'}
        </h1>
        <p className="text-muted-foreground">
          Here&apos;s what&apos;s happening with your business today.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Earnings"
          value="$12,450"
          description="This month"
          change={12.5}
          icon={DollarSign}
          trend="up"
        />
        <StatsCard
          title="Active Listings"
          value="8"
          description="2 pending review"
          icon={List}
        />
        <StatsCard
          title="Profile Views"
          value="1,234"
          description="This month"
          change={5.2}
          icon={Eye}
          trend="up"
        />
        <StatsCard
          title="Average Rating"
          value="4.8"
          description="Based on 156 reviews"
          change={0.2}
          icon={Star}
          trend="up"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Earnings Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                <div className="text-center">
                  <div className="h-12 w-12 rounded-full bg-muted mx-auto mb-4 flex items-center justify-center">
                    <DollarSign className="h-6 w-6" />
                  </div>
                  <p>Chart visualization would go here</p>
                  <p className="text-sm">Using recharts for rendering</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div>
          <QuickActions />
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <RecentActivityList activities={mockActivities} />

        <Card>
          <CardHeader>
            <CardTitle>Upcoming Bookings</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center gap-4 p-4 rounded-lg border">
                <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                  <Users className="h-5 w-5 text-primary" />
                </div>
                <div className="flex-1">
                  <p className="font-medium">Home Cleaning</p>
                  <p className="text-sm text-muted-foreground">
                    Tomorrow at 10:00 AM
                  </p>
                </div>
                <span className="text-sm font-medium">$89</span>
              </div>
              <div className="flex items-center gap-4 p-4 rounded-lg border">
                <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                  <Users className="h-5 w-5 text-primary" />
                </div>
                <div className="flex-1">
                  <p className="font-medium">Photography Session</p>
                  <p className="text-sm text-muted-foreground">
                    Jun 15 at 2:00 PM
                  </p>
                </div>
                <span className="text-sm font-medium">$250</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}