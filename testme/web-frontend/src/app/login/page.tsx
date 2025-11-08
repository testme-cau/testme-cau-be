"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { useAuth } from "@/hooks/useAuth";
import { signInWithGoogle, devLogin, signOut } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { Logo } from "@/components/ui/logo";
import { Brain, Zap, Target, ArrowRight, Code, LogOut } from "lucide-react";

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const { toast } = useToast();
  const isDev = process.env.NODE_ENV === 'development';

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

  const handleDevLogin = async () => {
    console.log('[handleDevLogin] 개발자 모드 활성화');
    setLoading(true);
    
    try {
      await devLogin();
      // 페이지 리로드하여 useAuth가 새로운 상태를 반영하도록
      window.location.href = '/dashboard';
    } catch (error) {
      console.error('[handleDevLogin] Error:', error);
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    setLoading(true);
    try {
      await signOut();
      // 페이지 리로드하여 useAuth가 새로운 상태를 반영하도록
      window.location.reload();
    } catch (error) {
      console.error('[handleLogout] Error:', error);
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

  // 이미 로그인된 경우 대시보드로 이동 버튼 표시
  if (user) {
    return (
      <div className="flex h-screen items-center justify-center bg-gradient-to-br from-emerald-50 via-green-50 to-teal-50">
        <div className="text-center p-8 bg-white/80 backdrop-blur-md rounded-3xl shadow-2xl max-w-md">
          <Logo size="xl" />
          <h2 className="mt-6 text-2xl font-bold text-gray-900">
            이미 로그인되어 있습니다
          </h2>
          <p className="mt-2 text-gray-600">
            {user.email}
          </p>
          <div className="mt-6 space-y-3">
            <Button
              size="lg"
              className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white shadow-md hover:shadow-lg transition-all"
              onClick={() => {
                console.log('[LoginPage] 대시보드 이동 버튼 클릭');
                window.location.href = '/dashboard';
              }}
              disabled={loading}
            >
              {loading ? (
                <LoadingSpinner size="sm" className="mr-2" />
              ) : (
                <>
                  대시보드로 이동
                  <ArrowRight className="ml-2 w-4 h-4" />
                </>
              )}
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="w-full border-2 hover:bg-red-50 hover:border-red-500 hover:text-red-600 transition-colors"
              onClick={handleLogout}
              disabled={loading}
            >
              {loading ? (
                <LoadingSpinner size="sm" className="mr-2" />
              ) : (
                <>
                  <LogOut className="mr-2 w-4 h-4" />
                  로그아웃
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-emerald-50 via-green-50 to-teal-50">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-secondary-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
        <div className="absolute top-40 left-40 w-80 h-80 bg-accent-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
      </div>

      <div className="relative z-10 w-full max-w-6xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Side - Features */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="hidden lg:block space-y-8"
          >
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-secondary-600">
                  test.me
                </span>
                와 함께
                <br />
                효율적인 학습을 시작하세요
              </h1>
              <p className="text-lg text-gray-600">
                AI가 만들어주는 맞춤형 시험으로 학습 효과를 극대화하세요
              </p>
            </div>

            <div className="space-y-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2, duration: 0.5 }}
                className="flex items-start gap-4 p-4 bg-white/60 backdrop-blur-sm rounded-xl shadow-md"
              >
                <div className="flex-shrink-0 w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                  <Brain className="w-6 h-6 text-primary-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">능동적 회상</h3>
                  <p className="text-sm text-gray-600">
                    시험을 통한 학습으로 기억에 확실하게 각인됩니다
                  </p>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3, duration: 0.5 }}
                className="flex items-start gap-4 p-4 bg-white/60 backdrop-blur-sm rounded-xl shadow-md"
              >
                <div className="flex-shrink-0 w-12 h-12 bg-secondary-100 rounded-lg flex items-center justify-center">
                  <Zap className="w-6 h-6 text-secondary-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">AI 자동 생성</h3>
                  <p className="text-sm text-gray-600">
                    PDF 업로드만으로 자동으로 시험 문제가 생성됩니다
                  </p>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4, duration: 0.5 }}
                className="flex items-start gap-4 p-4 bg-white/60 backdrop-blur-sm rounded-xl shadow-md"
              >
                <div className="flex-shrink-0 w-12 h-12 bg-accent-100 rounded-lg flex items-center justify-center">
                  <Target className="w-6 h-6 text-accent-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">즉시 피드백</h3>
                  <p className="text-sm text-gray-600">
                    틀린 부분을 바로 확인하고 다시 학습할 수 있습니다
                  </p>
                </div>
              </motion.div>
            </div>

            <div className="flex items-center gap-4 text-sm text-gray-500">
              <div className="flex -space-x-2">
                <div className="w-8 h-8 rounded-full bg-primary-200 border-2 border-white"></div>
                <div className="w-8 h-8 rounded-full bg-secondary-200 border-2 border-white"></div>
                <div className="w-8 h-8 rounded-full bg-accent-200 border-2 border-white"></div>
                <div className="w-8 h-8 rounded-full bg-primary-300 border-2 border-white flex items-center justify-center text-xs font-medium">
                  +
                </div>
              </div>
              <p>
                <span className="font-semibold text-gray-700">1,000명+</span>이 이미 사용 중
              </p>
            </div>
          </motion.div>

          {/* Right Side - Login Card */}
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="w-full max-w-md mx-auto"
          >
            <div className="bg-white/80 backdrop-blur-md rounded-3xl shadow-2xl p-8 sm:p-12 border border-white/20">
              <div className="text-center mb-8">
                <motion.div
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: 0.2, duration: 0.5 }}
                >
                  <Logo size="xl" />
                </motion.div>
                <motion.h2
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3, duration: 0.5 }}
                  className="mt-6 text-3xl font-extrabold text-gray-900"
                >
                  시작하기
                </motion.h2>
                <motion.p
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4, duration: 0.5 }}
                  className="mt-2 text-sm text-gray-600"
                >
                  Google 계정으로 간편하게 시작하세요
                </motion.p>
              </div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5, duration: 0.5 }}
              >
                <Button
                  type="button"
                  size="lg"
                  className="w-full h-16 text-base font-medium rounded-2xl bg-white hover:bg-gray-50 text-gray-700 border-2 border-gray-300 shadow-md hover:shadow-xl transition-all group"
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
                  <span className="flex items-center">
                    Google로 시작하기
                    <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </span>
                </Button>

                {/* 개발 모드 전용 로그인 버튼 */}
                {isDev && (
                  <Button
                    type="button"
                    size="lg"
                    id="dev-login-button"
                    className="w-full h-14 text-base font-medium rounded-2xl bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white shadow-md hover:shadow-xl transition-all group mt-4"
                    onClick={handleDevLogin}
                    disabled={loading}
                  >
                    {loading ? (
                      <LoadingSpinner size="sm" className="mr-3" />
                    ) : (
                      <Code className="mr-3 h-5 w-5" />
                    )}
                    <span className="flex items-center">
                      개발자 로그인 (테스트용)
                      <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </span>
                  </Button>
                )}

                <div className="mt-6 text-center">
                  <p className="text-xs text-gray-500">
                    로그인하시면{" "}
                    <span className="text-primary-600 hover:underline cursor-pointer">
                      이용약관
                    </span>{" "}
                    및{" "}
                    <span className="text-primary-600 hover:underline cursor-pointer">
                      개인정보처리방침
                    </span>
                    에 동의하게 됩니다
                  </p>
                </div>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </div>

      <style jsx>{`
        @keyframes blob {
          0% {
            transform: translate(0px, 0px) scale(1);
          }
          33% {
            transform: translate(30px, -50px) scale(1.1);
          }
          66% {
            transform: translate(-20px, 20px) scale(0.9);
          }
          100% {
            transform: translate(0px, 0px) scale(1);
          }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  );
}

