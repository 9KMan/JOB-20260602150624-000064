'use client';

import Link from 'next/link';
import { LoginForm } from '@/components/auth/login-form';

export default function LoginPage() {
  return (
    <div className="w-full max-w-md">
      <div className="flex justify-center mb-8">
        <div className="flex items-center gap-3">
          <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-lg">
            <span className="text-white font-bold text-xl">P</span>
          </div>
          <span className="font-bold text-2xl">PremiumServices</span>
        </div>
      </div>

      <div className="bg-card rounded-xl shadow-xl border p-8">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold">Welcome back</h1>
          <p className="text-muted-foreground mt-1">
            Sign in to your account to continue
          </p>
        </div>

        <LoginForm />

        <div className="mt-6 text-center text-sm">
          <span className="text-muted-foreground">
            Don&apos;t have an account?{' '}
          </span>
          <Link href="/register" className="text-primary hover:underline">
            Sign up
          </Link>
        </div>
      </div>

      <p className="text-center text-xs text-muted-foreground mt-6">
        By signing in, you agree to our{' '}
        <Link href="/terms" className="hover:underline">
          Terms of Service
        </Link>{' '}
        and{' '}
        <Link href="/privacy" className="hover:underline">
          Privacy Policy
        </Link>
        .
      </p>
    </div>
  );
}