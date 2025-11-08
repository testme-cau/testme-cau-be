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
  try {
    // 개발 모드 체크
    const isDev = process.env.NODE_ENV === 'development';
    
    if (isDev) {
      // 개발 모드: sessionStorage 초기화
      console.log('[signOut] Development mode - clearing session');
      sessionStorage.removeItem('dev-logged-in');
      return { error: null };
    }
    
    // 프로덕션 모드: Firebase 로그아웃
    await firebaseSignOut(auth);
    return { error: null };
  } catch (error: any) {
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

