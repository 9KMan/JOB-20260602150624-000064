import Link from 'next/link';
import { formatRelativeTime } from '@/lib/utils';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { RecentActivity } from '@/types';

interface RecentActivityProps {
  activities: RecentActivity[];
}

const activityTypeStyles = {
  review: { color: 'bg-yellow-500', label: 'Review' },
  booking: { color: 'bg-blue-500', label: 'Booking' },
  inquiry: { color: 'bg-purple-500', label: 'Inquiry' },
  listing_update: { color: 'bg-green-500', label: 'Update' },
  payment: { color: 'bg-emerald-500', label: 'Payment' },
};

export function RecentActivityList({ activities }: RecentActivityProps) {
  if (activities.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center mb-4">
              <svg
                className="h-6 w-6 text-muted-foreground"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <p className="text-sm text-muted-foreground">
              No recent activity yet
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Recent Activity</CardTitle>
        <Link
          href="/dashboard/activity"
          className="text-sm text-primary hover:underline"
        >
          View all
        </Link>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities.map((activity) => {
            const style = activityTypeStyles[activity.type] || activityTypeStyles.listing_update;

            return (
              <div
                key={activity.id}
                className="flex items-start gap-4 pb-4 border-b last:border-0 last:pb-0"
              >
                <div className={`h-2 w-2 mt-2 rounded-full ${style.color}`} />
                <div className="flex-1 space-y-1">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium">{activity.title}</p>
                    <span className="text-xs text-muted-foreground">
                      {formatRelativeTime(activity.createdAt)}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {activity.description}
                  </p>
                  <Badge variant="secondary" className="text-xs">
                    {style.label}
                  </Badge>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}