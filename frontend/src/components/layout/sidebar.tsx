'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  List,
  PlusCircle,
  User,
  Settings,
  Bell,
  CreditCard,
  BarChart3,
  Calendar,
  HelpCircle,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { useState } from 'react';

const sidebarLinks = [
  {
    title: 'Main',
    items: [
      { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
      { name: 'My Listings', href: '/dashboard/listings', icon: List },
      { name: 'Create Listing', href: '/dashboard/listings/new', icon: PlusCircle },
      { name: 'Calendar', href: '/dashboard/calendar', icon: Calendar },
    ],
  },
  {
    title: 'Account',
    items: [
      { name: 'Profile', href: '/dashboard/profile', icon: User },
      { name: 'Settings', href: '/dashboard/settings', icon: Settings },
      { name: 'Notifications', href: '/dashboard/notifications', icon: Bell },
    ],
  },
  {
    title: 'Business',
    items: [
      { name: 'Analytics', href: '/dashboard/analytics', icon: BarChart3 },
      { name: 'Billing', href: '/dashboard/billing', icon: CreditCard },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  const isActive = (href: string) => {
    if (href === '/dashboard') return pathname === href;
    return pathname.startsWith(href);
  };

  return (
    <aside
      className={cn(
        'sticky top-0 flex h-screen flex-col border-r bg-card transition-all duration-300',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      <div className="flex h-16 items-center border-b px-4">
        {!collapsed && (
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center">
              <span className="text-white font-bold text-lg">P</span>
            </div>
            <span className="font-bold">Dashboard</span>
          </Link>
        )}
        {collapsed && (
          <div className="mx-auto">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center">
              <span className="text-white font-bold text-lg">P</span>
            </div>
          </div>
        )}
      </div>

      <nav className="flex-1 overflow-y-auto p-4">
        {sidebarLinks.map((section) => (
          <div key={section.title} className="mb-6">
            {!collapsed && (
              <h3 className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                {section.title}
              </h3>
            )}
            <ul className="space-y-1">
              {section.items.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.href);

                return (
                  <li key={item.name}>
                    <Link
                      href={item.href}
                      className={cn(
                        'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                        active
                          ? 'bg-primary text-primary-foreground'
                          : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
                        collapsed && 'justify-center px-2'
                      )}
                      title={collapsed ? item.name : undefined}
                    >
                      <Icon className="h-5 w-5 shrink-0" />
                      {!collapsed && <span>{item.name}</span>}
                    </Link>
                  </li>
                );
              })}
            </ul>
            <Separator className="mt-4" />
          </div>
        ))}
      </nav>

      <div className="border-t p-4">
        <Link
          href="/dashboard/help"
          className={cn(
            'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground',
            collapsed && 'justify-center px-2'
          )}
          title={collapsed ? 'Help' : undefined}
        >
          <HelpCircle className="h-5 w-5 shrink-0" />
          {!collapsed && <span>Help & Support</span>}
        </Link>
      </div>

      <div className="border-t p-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setCollapsed(!collapsed)}
          className="w-full justify-center"
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <>
              <ChevronLeft className="h-4 w-4 mr-2" />
              Collapse
            </>
          )}
        </Button>
      </div>
    </aside>
  );
}