import { useSession, signIn, signOut } from 'next-auth/react';
import { useRouter, usePathname } from 'next/navigation';
import { useCallback, useEffect } from 'react';

interface UseAuthReturn {
  user: { id: string; name: string; email: string; image?: string; role: string } | null;
  status: 'loading' | 'authenticated' | 'unauthenticated';
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string, remember?: boolean) => Promise<void>;
  logout: () => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  loginWithGitHub: () => Promise<void>;
}

export function useAuth(): UseAuthReturn {
  const { data: session, status } = useSession();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (status === 'unauthenticated' && pathname?.startsWith('/dashboard')) {
      router.push('/login');
    }
  }, [status, pathname, router]);

  const login = useCallback(
    async (email: string, password: string, remember = false) => {
      const result = await signIn('credentials', {
        email,
        password,
        redirect: false,
      });

      if (result?.error) {
        throw new Error(result.error);
      }

      router.push('/dashboard');
    },
    [router]
  );

  const logout = useCallback(async () => {
    await signOut({ redirect: false });
    router.push('/');
  }, [router]);

  const loginWithGoogle = useCallback(async () => {
    await signIn('google', { callbackUrl: '/dashboard' });
  }, []);

  const loginWithGitHub = useCallback(async () => {
    await signIn('github', { callbackUrl: '/dashboard' });
  }, []);

  return {
    user: session?.user as UseAuthReturn['user'],
    status,
    isAuthenticated: status === 'authenticated',
    isLoading: status === 'loading',
    login,
    logout,
    loginWithGoogle,
    loginWithGitHub,
  };
}