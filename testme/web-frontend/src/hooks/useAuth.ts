import { useEffect, useState } from 'react';
import { User, onAuthStateChanged } from 'firebase/auth';
import { auth } from '@/lib/firebase';
import { getIdToken } from '@/lib/auth';

const DEV_AUTH_TOKEN =
  process.env.NEXT_PUBLIC_DEV_AUTH_TOKEN || 'dev-token-123';
const FORCE_DEV_AUTH =
  process.env.NEXT_PUBLIC_FORCE_DEV_AUTH === 'true';

// Mock user for development
const createMockUser = (): Partial<User> => ({
  uid: 'dev-user-123',
  email: 'test@testme.dev',
  displayName: 'Test User',
  emailVerified: true,
  getIdToken: async () => DEV_AUTH_TOKEN,
} as Partial<User>);

export function useAuth() {
  // SSR 시에는 항상 loading: true (hydration mismatch 방지)
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [idToken, setIdToken] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);
  const isDevelopment = process.env.NODE_ENV === 'development';
  const hasFirebaseConfig = Boolean(process.env.NEXT_PUBLIC_FIREBASE_API_KEY);
  const baseMockCondition = isDevelopment && !hasFirebaseConfig;
  const shouldUseMockAuth = baseMockCondition || FORCE_DEV_AUTH;

  useEffect(() => {
    // 클라이언트 마운트 표시
    setMounted(true);

    console.log('[useAuth] Mounted, NODE_ENV:', process.env.NODE_ENV, 'hasFirebaseConfig:', hasFirebaseConfig);
    
    const devLoggedIn =
      typeof window !== 'undefined' &&
      sessionStorage.getItem('dev-logged-in') === 'true';
    const useDevBypass = (isDevelopment && devLoggedIn) || FORCE_DEV_AUTH;

    if (shouldUseMockAuth || useDevBypass) {
      console.log('[useAuth] Development mock mode - using mock user (devLoggedIn:', devLoggedIn, ', shouldUseMockAuth:', shouldUseMockAuth, ')');
      if (useDevBypass) {
        const mockUser = createMockUser() as User;
        setUser(mockUser);
        setIdToken(DEV_AUTH_TOKEN);
      } else {
        setUser(null);
        setIdToken(null);
      }
      setLoading(false);
      return;
    }

    // Firebase Auth 사용 (프로덕션 또는 실제 설정이 있는 개발환경)
    console.log('[useAuth] Using Firebase Auth listener');
    
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      console.log('[useAuth] Auth state changed:', user?.email || 'No user');
      setUser(user);
      if (user) {
        const token = await getIdToken(user);
        setIdToken(token);
      } else {
        setIdToken(null);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  return {
    user,
    loading,
    idToken,
    isAuthenticated: !!user,
  };
}

