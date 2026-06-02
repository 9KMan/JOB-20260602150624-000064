'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, X, Home, Search, User, LogIn, LogOut, PlusCircle, List } from 'lucide-react';
import { useState } from 'react';
import { useSession, signOut } from 'next-auth/react';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { cn } from '@/lib/utils';

const mobileNavLinks = [
  { name: 'Home', href: '/', icon: Home },
  { name: 'Browse Services', href: '/listings', icon: Search },
  { name: 'My Listings', href: '/dashboard/listings', icon: List },
  { name: 'Create Listing', href: '/dashboard/listings/new', icon: PlusCircle },
  { name: 'Profile', href: '/dashboard/profile', icon: User },
];

export function MobileNav() {
  const pathname = usePathname();
  const { data: session } = useSession();
  const [open, setOpen] = useState(false);

  const isActive = (href: string) => {
    if (href === '/') return pathname === href;
    return pathname.startsWith(href);
  };

  return (
    <div className="md:hidden">
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetTrigger asChild>
          <Button variant="ghost" size="icon">
            <Menu className="h-5 w-5" />
            <span className="sr-only">Open menu</span>
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-80">
          <div className="flex flex-col gap-6 pt-6">
            <Link
              href="/"
              className="flex items-center gap-2 px-2"
              onClick={() => setOpen(false)}
            >
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center">
                <span className="text-white font-bold text-lg">P</span>
              </div>
              <span className="font-bold text-lg">PremiumServices</span>
            </Link>

            <nav className="flex flex-col gap-2">
              {mobileNavLinks.map((link) => {
                const Icon = link.icon;
                return (
                  <Link
                    key={link.name}
                    href={link.href}
                    onClick={() => setOpen(false)}
                    className={cn(
                      'flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium transition-colors',
                      isActive(link.href)
                        ? 'bg-primary text-primary-foreground'
                        : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                    )}
                  >
                    <Icon className="h-5 w-5" />
                    {link.name}
                  </Link>
                );
              })}
            </nav>

            <div className="border-t pt-4">
              {session?.user ? (
                <div className="flex flex-col gap-2">
                  <div className="flex items-center gap-3 px-3 py-2">
                    <Avatar className="h-10 w-10">
                      <AvatarImage src={session.user.image ?? ''} alt={session.user.name ?? ''} />
                      <AvatarFallback>
                        {session.user.name?.charAt(0) ?? 'U'}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <p className="text-sm font-medium">{session.user.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {session.user.email}
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    className="justify-start text-destructive"
                    onClick={() => signOut({ callbackUrl: '/' })}
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    Sign out
                  </Button>
                </div>
              ) : (
                <div className="flex flex-col gap-2">
                  <Button asChild onClick={() => setOpen(false)}>
                    <Link href="/login">
                      <LogIn className="mr-2 h-4 w-4" />
                      Sign in
                    </Link>
                  </Button>
                  <Button variant="outline" asChild onClick={() => setOpen(false)}>
                    <Link href="/register">Get Started</Link>
                  </Button>
                </div>
              )}
            </div>
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
}