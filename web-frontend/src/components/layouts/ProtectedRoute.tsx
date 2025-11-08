"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { LoadingPage } from "@/components/ui/loading-spinner";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const isDevelopment = process.env.NODE_ENV === 'development';

  console.log('[ProtectedRoute] Checking auth - loading:', loading, 'user:', user?.email || 'none', 'isDev:', isDevelopment);

  useEffect(() => {
    // 로딩이 끝났고 사용자가 없으면 로그인 페이지로 리다이렉트
    if (!loading && !user) {
      console.log('[ProtectedRoute] No user detected - redirecting to login');
      router.push("/login");
    }
  }, [loading, user, router]);

  // 로딩 중이면 로딩 페이지 표시
  if (loading) {
    console.log('[ProtectedRoute] Loading...');
    return <LoadingPage />;
  }

  // 사용자가 없으면 null 반환 (리다이렉트 진행 중)
  if (!user) {
    console.log('[ProtectedRoute] No user - returning null (redirecting)');
    return null;
  }

  // 사용자가 있으면 children 렌더링
  console.log('[ProtectedRoute] User authenticated - rendering children');
  return <>{children}</>;
}

