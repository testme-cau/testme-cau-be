"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { LoadingPage } from "@/components/ui/loading-spinner";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  // 개발 환경에서는 인증 체크 완전 비활성화
  const isDevelopment = process.env.NODE_ENV === 'development';
  
  console.log('[ProtectedRoute] NODE_ENV:', process.env.NODE_ENV, 'isDevelopment:', isDevelopment);
  
  if (isDevelopment) {
    console.log('[ProtectedRoute] Development mode - auth check disabled, rendering children');
    return <>{children}</>;
  }
  
  console.log('[ProtectedRoute] Production mode - checking auth');

  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // 로딩이 끝났고 사용자가 없으면 리다이렉트
    if (!loading && !user) {
      console.log('[ProtectedRoute] No user - redirecting to login');
      router.push("/login");
    }
  }, [loading, user, router]);

  // 로딩 중이면 로딩 페이지 표시
  if (loading) {
    return <LoadingPage />;
  }

  // 사용자가 없으면 null 반환 (리다이렉트 중)
  if (!user) {
    return null;
  }

  // 사용자가 있으면 children 렌더링
  return <>{children}</>;
}

