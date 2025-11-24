"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ShieldAlert, ArrowRight, LogOut } from "lucide-react";

import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/hooks/use-toast";
import { fetchBetaStatus, requestWaitlistAccess } from "@/lib/api/system";
import type { BetaStatusResponse } from "@/types/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { Logo } from "@/components/ui/logo";
import { signOut } from "@/lib/auth";

export default function WaitlistPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, loading } = useAuth();
  const { toast } = useToast();

  const [betaStatus, setBetaStatus] = useState<BetaStatusResponse | null>(null);
  const [waitlistEmail, setWaitlistEmail] = useState("");
  const [waitlistNote, setWaitlistNote] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const allowedEmails =
    betaStatus?.allowed_emails?.map((email) => email.toLowerCase()) ?? [];
  const isClosedBeta = betaStatus?.status === "closed_beta";
  const isAllowedUser =
    isClosedBeta &&
    !!(user?.email && allowedEmails.includes(user.email.toLowerCase()));

  useEffect(() => {
    fetchBetaStatus()
      .then(setBetaStatus)
      .catch(() => {
        toast({
          title: "상태 확인 실패",
          description: "클로즈베타 상태를 불러올 수 없습니다.",
          variant: "destructive",
        });
      });
  }, [toast]);

  useEffect(() => {
    if (user?.email) {
      setWaitlistEmail(user.email);
    }
  }, [user]);

  useEffect(() => {
    if (!loading && user && isAllowedUser) {
      router.replace("/dashboard");
    }
  }, [loading, user, isAllowedUser, router]);

  const handleWaitlistSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!waitlistEmail.trim()) {
      toast({
        title: "이메일을 입력해주세요",
        description: "초대 요청을 위해 이메일 주소가 필요합니다.",
        variant: "destructive",
      });
      return;
    }

    setSubmitting(true);
    try {
      const response = await requestWaitlistAccess({
        email: waitlistEmail,
        note: waitlistNote || undefined,
      });
      toast({
        title: "신청 완료",
        description:
          response.message ||
          (response.already_allowed
            ? "이미 허용된 이메일입니다. 다시 로그인해보세요."
            : "승인 대기 목록에 등록되었습니다."),
      });
      if (!response.already_allowed) {
        setWaitlistNote("");
      }
    } catch (error: any) {
      toast({
        title: "신청 실패",
        description: error?.message || "대기열 신청 중 오류가 발생했습니다.",
        variant: "destructive",
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleLogout = async () => {
    await signOut();
    router.replace("/login");
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-brand-gradient">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-brand-gradient flex items-center justify-center px-4 py-12">
      <div className="max-w-5xl w-full grid lg:grid-cols-2 gap-8">
        <div className="bg-white/90 backdrop-blur-md rounded-3xl shadow-xl p-10 border border-white/30">
          <Logo size="xl" />
          <h1 className="mt-6 text-3xl font-bold text-gray-900 leading-snug">
            test.me는 현재 클로즈베타 단계입니다.
          </h1>
          <p className="mt-4 text-gray-600">
            초대받은 이메일만 서비스에 접근할 수 있습니다. 초대가 필요한 경우 아래
            폼으로 요청을 남겨주세요.
          </p>
          <div className="mt-6 space-y-4 text-sm text-gray-600">
            <div className="flex items-center gap-3 p-3 rounded-2xl bg-amber-50 border border-amber-100 text-amber-900">
              <ShieldAlert className="w-5 h-5" />
              <span>
                {user?.email
                  ? `${user.email} 계정은 아직 허용되지 않았습니다.`
                  : "로그인되지 않은 상태입니다."}
              </span>
            </div>
            {searchParams?.get("reason") === "beta" && (
              <p className="text-amber-700">
                최근 요청이 거부되어 이 페이지로 이동했습니다. 초대 요청을 남기거나
                다른 계정으로 다시 시도해주세요.
              </p>
            )}
          </div>
          <div className="mt-6 flex flex-col gap-3">
            <Button
              variant="outline"
              className="justify-between"
              onClick={handleLogout}
            >
              <span>다른 계정으로 로그인</span>
              <LogOut className="w-4 h-4" />
            </Button>
            <Button
              className="justify-between"
              onClick={() => router.push("/")}
              variant="secondary"
            >
              <span>홈으로 돌아가기</span>
              <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        </div>

        <div className="bg-white rounded-3xl shadow-2xl p-10 border border-gray-100">
          <h2 className="text-2xl font-semibold text-gray-900">
            초대 요청하기
          </h2>
          <p className="mt-2 text-sm text-gray-500">
            간단한 소개와 함께 초대 요청을 남겨주세요. 허용되면 이메일로 안내드립니다.
          </p>

          <form className="mt-6 space-y-4" onSubmit={handleWaitlistSubmit}>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">
                이메일 주소
              </label>
              <Input
                type="email"
                value={waitlistEmail}
                onChange={(e) => setWaitlistEmail(e.target.value)}
                placeholder="email@example.com"
                className="h-12"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">
                간단한 소개나 참고 메시지 (선택)
              </label>
              <Textarea
                value={waitlistNote}
                onChange={(e) => setWaitlistNote(e.target.value)}
                rows={4}
                placeholder="학교/수업 정보나 사용 목적 등을 남겨주시면 더 빠르게 검토할 수 있어요."
              />
            </div>

            <Button
              type="submit"
              disabled={submitting}
              className="w-full h-12 text-base"
            >
              {submitting ? (
                <>
                  <LoadingSpinner size="sm" className="mr-2" />
                  요청 보내는 중...
                </>
              ) : (
                <>클로즈베타 초대 요청</>
              )}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}

