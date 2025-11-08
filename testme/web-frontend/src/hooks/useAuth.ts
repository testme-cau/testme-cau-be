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

  useEffect(() => {
    // 클라이언트 마운트 표시
    setMounted(true);

    // 개발 모드 체크 (NODE_ENV만 확인)
    const isDev = process.env.NODE_ENV === 'development';
    
    console.log('[useAuth] Mounted, NODE_ENV:', process.env.NODE_ENV);
    
    if (isDev) {
      // 개발 모드: sessionStorage로 로그인 상태 확인
      const devLoggedIn = sessionStorage.getItem('dev-logged-in');
      
      if (devLoggedIn === 'true') {
        console.log('[useAuth] Development mode - Setting mock user (logged in)');
        const mockUser = createMockUser() as User;
        setUser(mockUser);
        setIdToken('dev-token-123');
      } else {
        console.log('[useAuth] Development mode - No dev login, user is null');
        setUser(null);
        setIdToken(null);
      }
      setLoading(false);
      return; // Firebase Auth 실행 안 함
    }

    // 프로덕션 모드: Firebase Auth 사용
    console.log('[useAuth] Production mode - Initializing Firebase Auth');
    
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

