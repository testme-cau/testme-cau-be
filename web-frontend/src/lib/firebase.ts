import { initializeApp, getApps, type FirebaseApp } from 'firebase/app';
import { getAuth, type Auth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
  measurementId: process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID,
};

const hasFirebaseConfig = Boolean(firebaseConfig.apiKey);

let firebaseApp: FirebaseApp | null = null;

if (hasFirebaseConfig) {
  firebaseApp = getApps().length ? getApps()[0] : initializeApp(firebaseConfig);
} else if (process.env.NODE_ENV !== 'production') {
  console.warn(
    '[firebase] NEXT_PUBLIC_FIREBASE_API_KEY is missing. Falling back to mock auth mode.'
  );
}

export const app = firebaseApp;
export const auth: Auth =
  (firebaseApp ? getAuth(firebaseApp) : null) as Auth;

