import { create } from 'zustand';
import { User } from 'firebase/auth';

interface AuthState {
  user: User | null;
  idToken: string | null;
  setUser: (user: User | null) => void;
  setIdToken: (token: string | null) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  idToken: null,
  setUser: (user) => set({ user }),
  setIdToken: (token) => set({ idToken: token }),
}));

