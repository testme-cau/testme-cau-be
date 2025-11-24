import { 
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  signOut as firebaseSignOut,
  User
} from 'firebase/auth';
import { auth } from './firebase';

/**
 * Sign in with email and password
 */
export async function signInWithEmail(email: string, password: string) {
  try {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    return { user: userCredential.user, error: null };
  } catch (error: any) {
    return { user: null, error: error.message };
  }
}

/**
 * Sign up with email and password
 */
export async function signUpWithEmail(email: string, password: string) {
  try {
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    return { user: userCredential.user, error: null };
  } catch (error: any) {
    return { user: null, error: error.message };
  }
}

/**
 * Sign in with Google
 */
export async function signInWithGoogle() {
  try {
    const provider = new GoogleAuthProvider();
    const userCredential = await signInWithPopup(auth, provider);
    return { user: userCredential.user, error: null };
  } catch (error: any) {
    return { user: null, error: error.message };
  }
}

/**
 * Sign out
 */
export async function signOut() {
  const isDev = process.env.NODE_ENV === 'development';
  const hasFirebaseConfig = Boolean(process.env.NEXT_PUBLIC_FIREBASE_API_KEY);
  const forceDevAuth = process.env.NEXT_PUBLIC_FORCE_DEV_AUTH === 'true';
  const shouldUseMockAuth = (isDev && !hasFirebaseConfig) || forceDevAuth;
  const devSessionActive =
    typeof window !== 'undefined' &&
    sessionStorage.getItem('dev-logged-in') === 'true';

  try {
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem('dev-logged-in');
    }

    if (shouldUseMockAuth || (isDev && devSessionActive)) {
      console.log('[signOut] Mock auth mode - session cleared');
      return { error: null };
    }

    await firebaseSignOut(auth);
    return { error: null };
  } catch (error: any) {
    console.error('[signOut] Failed:', error);
    return { error: error.message };
  }
}

/**
 * Get Firebase ID token for API requests
 */
export async function getIdToken(user: User | null): Promise<string | null> {
  if (!user) return null;
  try {
    const token = await user.getIdToken();
    return token;
  } catch (error) {
    console.error('Failed to get ID token:', error);
    return null;
  }
}

/**
 * Development mode login - bypasses Firebase Auth
 * Only available when NODE_ENV is development
 */
export async function devLogin() {
  const isDev = process.env.NODE_ENV === 'development';
  
  if (!isDev) {
    return { user: null, error: 'Dev login only available in development mode' };
  }

  try {
    // sessionStorage에 개발 모드 로그인 플래그 설정
    console.log('[devLogin] Setting dev-logged-in flag');
    sessionStorage.setItem('dev-logged-in', 'true');
    
    // Mock user 생성
    const mockUser = {
      uid: 'dev-user-123',
      email: 'test@testme.dev',
      displayName: 'Test User',
      emailVerified: true,
    };
    
    return { user: mockUser as any, error: null };
  } catch (error: any) {
    return { user: null, error: error.message };
  }
}

