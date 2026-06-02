import type { NextAuthConfig } from 'next-auth';
import Credentials from 'next-auth/providers/credentials';
import Google from 'next-auth/providers/google';
import GitHub from 'next-auth/providers/github';
import { z } from 'zod';

const credentialsSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

export const authConfig: NextAuthConfig = {
  pages: {
    signIn: '/login',
    signOut: '/login',
    error: '/login',
    verifyRequest: '/login?verify=1',
  },
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID || '',
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || '',
    }),
    GitHub({
      clientId: process.env.GITHUB_CLIENT_ID || '',
      clientSecret: process.env.GITHUB_CLIENT_SECRET || '',
    }),
    Credentials({
      name: 'credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        const parsed = credentialsSchema.safeParse(credentials);

        if (!parsed.success) {
          return null;
        }

        const { email, password } = parsed.data;

        // In production, validate against your database
        // This is a mock implementation
        const mockUser = {
          id: '1',
          name: 'Demo User',
          email: email,
          image: null,
          role: 'user' as const,
        };

        // Simulate password verification delay
        await new Promise((resolve) => setTimeout(resolve, 500));

        // Mock validation - in production, verify against hashed password
        if (password.length < 8) {
          return null;
        }

        return mockUser;
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        token.role = (user as { role?: string }).role || 'user';
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string;
        session.user.role = token.role as string;
      }
      return session;
    },
    authorized({ auth, request: { nextUrl } }) {
      const isLoggedIn = !!auth?.user;
      const isOnDashboard = nextUrl.pathname.startsWith('/dashboard');
      const isOnAuth = nextUrl.pathname.startsWith('/login') ||
                       nextUrl.pathname.startsWith('/register');
      const isOnApi = nextUrl.pathname.startsWith('/api');

      if (isOnDashboard || nextUrl.pathname.startsWith('/settings')) {
        if (isLoggedIn) return true;
        return false;
      }

      if (isOnAuth) {
        if (isLoggedIn) {
          return Response.redirect(new URL('/dashboard', nextUrl));
        }
        return true;
      }

      if (isOnApi) {
        return true;
      }

      return true;
    },
  },
  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  trustHost: true,
  secret: process.env.NEXTAUTH_SECRET,
};