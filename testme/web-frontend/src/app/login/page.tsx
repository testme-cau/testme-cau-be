"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { signInWithGoogle } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { Logo } from "@/components/ui/logo";

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const { toast } = useToast();

  useEffect(() => {
    if (!authLoading && user) {
      router.push("/dashboard");
    }
  }, [user, authLoading, router]);

  const handleGoogleLogin = async () => {
    setLoading(true);
    try {
      const { user, error } = await signInWithGoogle();
      if (error) {
        toast({
          title: "인증 실패",
          description: error,
          variant: "destructive",
        });
      } else if (user) {
        toast({
          title: "환영합니다!",
          description: "test.me에 오신 것을 환영합니다.",
        });
        router.push("/dashboard");
      }
    } catch (error) {
      toast({
        title: "인증 실패",
        description: "알 수 없는 오류가 발생했습니다.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  if (authLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (user) {
    return null;
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <Logo size="xl" />
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            시작하기
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Google 계정으로 간편하게 시작하세요
          </p>
        </div>

        <div className="mt-12">
          <Button
            type="button"
            size="lg"
            className="w-full h-16 text-base font-medium rounded-2xl bg-white hover:bg-gray-50 text-gray-700 border-2 border-gray-300 shadow-md hover:shadow-lg transition-all"
            onClick={handleGoogleLogin}
            disabled={loading}
          >
            {loading ? (
              <LoadingSpinner size="sm" className="mr-3" />
            ) : (
              <svg className="mr-3 h-6 w-6" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
            )}
            <span>Google로 시작하기</span>
          </Button>
        </div>
      </div>
    </div>
  );
}

