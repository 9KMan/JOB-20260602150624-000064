import Link from 'next/link';
import { PlusCircle, List, BarChart3, MessageSquare, Settings } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const quickActions = [
  {
    title: 'Create Listing',
    description: 'Add a new service to your portfolio',
    icon: PlusCircle,
    href: '/dashboard/listings/new',
    color: 'text-amber-500',
    bgColor: 'bg-amber-500/10',
  },
  {
    title: 'View Listings',
    description: 'Manage your existing listings',
    icon: List,
    href: '/dashboard/listings',
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
  },
  {
    title: 'Analytics',
    description: 'View your performance metrics',
    icon: BarChart3,
    href: '/dashboard/analytics',
    color: 'text-purple-500',
    bgColor: 'bg-purple-500/10',
  },
  {
    title: 'Messages',
    description: 'Check your inbox and replies',
    icon: MessageSquare,
    href: '/dashboard/messages',
    color: 'text-green-500',
    bgColor: 'bg-green-500/10',
  },
  {
    title: 'Settings',
    description: 'Update your account preferences',
    icon: Settings,
    href: '/dashboard/settings',
    color: 'text-gray-500',
    bgColor: 'bg-gray-500/10',
  },
];

export function QuickActions() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
        <CardDescription>Common tasks and shortcuts</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-3">
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <Link key={action.title} href={action.href}>
                <Button
                  variant="outline"
                  className="w-full justify-start h-auto py-3"
                >
                  <div className={`h-10 w-10 rounded-lg ${action.bgColor} flex items-center justify-center mr-3`}>
                    <Icon className={`h-5 w-5 ${action.color}`} />
                  </div>
                  <div className="text-left">
                    <p className="font-medium text-sm">{action.title}</p>
                    <p className="text-xs text-muted-foreground">
                      {action.description}
                    </p>
                  </div>
                </Button>
              </Link>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}