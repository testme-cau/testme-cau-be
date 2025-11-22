import { useEffect, useState } from 'react';
import { User, onAuthStateChanged } from 'firebase/auth';
import { auth } from '@/lib/firebase';
import { getIdToken } from '@/lib/auth';

// Mock user for development
const createMockUser = (): Partial<User> => ({
  uid: 'dev-user-123',
  email: 'test@testme.dev',
  displayName: 'Test User',
  emailVerified: true,
  getIdToken: async () => 'dev-token-123',
} as Partial<User>);

export function useAuth() {
  // SSR 시에는 항상 loading: true (hydration mismatch 방지)
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [idToken, setIdToken] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);
  const hasFirebaseConfig = Boolean(process.env.NEXT_PUBLIC_FIREBASE_API_KEY);
  const shouldUseMockAuth = process.env.NODE_ENV === 'development' && !hasFirebaseConfig;

  useEffect(() => {
    // 클라이언트 마운트 표시
    setMounted(true);

    console.log('[useAuth] Mounted, NODE_ENV:', process.env.NODE_ENV, 'hasFirebaseConfig:', hasFirebaseConfig);
    
    if (shouldUseMockAuth) {
      // 실제 Firebase 설정이 없는 개발환경에서는 기존처럼 세션 플래그를 사용한다.
      const devLoggedIn = typeof window !== 'undefined' && sessionStorage.getItem('dev-logged-in') === 'true';
      
      if (devLoggedIn) {
        console.log('[useAuth] Development mode - Restoring mock session');
        const mockUser = createMockUser() as User;
        setUser(mockUser);
        setIdToken('dev-token-123');
      } else {
        console.log('[useAuth] Development mode - No mock session, user logged out');
        setUser(null);
        setIdToken(null);
      }
      
      setLoading(false);
      return; // Firebase Auth 실행 안 함
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

