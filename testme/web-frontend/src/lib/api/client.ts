import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { auth } from '@/lib/firebase';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add Firebase ID token
apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    const user = auth.currentUser;
    if (user) {
      try {
        const token = await user.getIdToken();
        config.headers.Authorization = `Bearer ${token}`;
      } catch (error) {
        console.error('Failed to get ID token:', error);
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error
      const { status, data } = error.response;
      
      if (status === 401) {
        // 개발 모드에서는 401 리다이렉트 비활성화
        const isDev = process.env.NODE_ENV === 'development';
        
        if (!isDev && typeof window !== 'undefined') {
          // 프로덕션에서만 로그인 페이지로 리다이렉트
          window.location.href = '/login';
        } else if (isDev) {
          console.log('[API Client] 401 error in development mode - redirect disabled');
        }
      }
      
      // Return error message from server
      return Promise.reject(new Error(data.message || data.error || 'An error occurred'));
    } else if (error.request) {
      // Request made but no response
      return Promise.reject(new Error('No response from server'));
    } else {
      // Something else happened
      return Promise.reject(error);
    }
  }
);

export default apiClient;

