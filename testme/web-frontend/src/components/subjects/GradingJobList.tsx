import { GradingJob } from "@/types/api";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import {
  AlertCircle,
  CheckCircle,
  Loader2,
  Timer,
  XCircle,
  BookOpenCheck,
  Sparkles,
} from "lucide-react";
import { ComponentType, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface GradingJobListProps {
  jobs: GradingJob[];
  loading?: boolean;
}

const statusConfig: Record<
  GradingJob["status"],
  { label: string; color: string; icon: ComponentType<any> }
> = {
  pending: { label: "대기 중", color: "bg-amber-100 text-amber-800", icon: Timer },
  processing: {
    label: "채점 중",
    color: "bg-blue-100 text-blue-800",
    icon: Loader2,
  },
  completed: {
    label: "완료됨",
    color: "bg-emerald-100 text-emerald-800",
    icon: CheckCircle,
  },
  failed: { label: "실패", color: "bg-rose-100 text-rose-800", icon: AlertCircle },
  cancelled: { label: "취소됨", color: "bg-gray-100 text-gray-700", icon: XCircle },
};

const statusAccent: Record<GradingJob["status"], string> = {
  pending: "from-amber-400/80 via-orange-400/70 to-yellow-300/60",
  processing: "from-blue-400/90 via-sky-400/80 to-indigo-300/70",
  completed: "from-emerald-400/80 via-teal-400/70 to-cyan-300/60",
  failed: "from-rose-500/80 via-pink-500/70 to-orange-400/70",
  cancelled: "from-gray-400/80 via-slate-400/70 to-zinc-300/60",
};

function formatProgress(value?: number) {
  if (value == null) return 0;
  return Math.min(100, Math.max(0, Math.round(value)));
}

function formatEstimatedTime(seconds?: number) {
  if (seconds == null || seconds <= 0) return "계산 중";
  if (seconds < 60) return "1분 미만";
  const minutes = Math.ceil(seconds / 60);
  return `${minutes}분`;
}

function formatEstimatedSummary(seconds?: number) {
  if (seconds == null || seconds <= 0) return "예상 시간 계산 중";
  if (seconds < 60) return "1분 미만";
  const minutes = Math.ceil(seconds / 60);
  return `${minutes}분 내외`;
}

function formatProvider(provider?: string) {
  switch (provider) {
    case "gpt":
      return "GPT";
    case "gemini":
      return "Gemini";
    default:
      return "기본 AI";
  }
}

function formatExamLabel(examId?: string) {
  if (!examId) return "시험 정보 없음";
  return `시험 #${examId.slice(-6)}`;
}

function formatSubmissionLabel(submissionId?: string) {
  if (!submissionId) return "제출 정보 없음";
  return `제출 #${submissionId.slice(-6)}`;
}

export function GradingJobList({ jobs, loading }: GradingJobListProps) {
  const activeJobs = useMemo(
    () => jobs.filter((job) => job.status === "pending" || job.status === "processing"),
    [jobs]
  );

  const averageProgress = useMemo(() => {
    if (!activeJobs.length) return 0;
    const sum = activeJobs.reduce((acc, job) => acc + formatProgress(job.progress_percentage), 0);
    return Math.round(sum / activeJobs.length);
  }, [activeJobs]);

  const totalQuestions = useMemo(
    () => activeJobs.reduce((acc, job) => acc + (job.total_questions || 0), 0),
    [activeJobs]
  );

  const avgEstimatedSeconds = useMemo(() => {
    if (!activeJobs.length) return undefined;
    const total = activeJobs.reduce(
      (acc, job) => acc + (job.estimated_duration_seconds || 0),
      0
    );
    return total ? Math.round(total / activeJobs.length) : undefined;
  }, [activeJobs]);

  if (!loading && activeJobs.length === 0) {
    return null;
  }

  return (
    <section className="space-y-5">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{
          opacity: 1,
          y: 0,
          backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"],
        }}
        transition={{
          duration: 0.35,
          backgroundPosition: { duration: 12, repeat: Infinity, ease: "linear" },
        }}
        className="relative overflow-hidden rounded-3xl p-6 text-white shadow-2xl"
        style={{
          backgroundImage: "linear-gradient(120deg, #2563eb 0%, #0891b2 45%, #10b981 100%)",
          backgroundSize: "200% 200%",
        }}
      >
        <div className="absolute inset-0 pointer-events-none">
          <div className="glow-orb left-1/3 top-4 h-40 w-40 bg-white/30 blur-3xl" />
          <div className="glow-orb right-8 bottom-0 h-56 w-56 bg-sky-300/40 blur-3xl" />
        </div>
        <div className="relative flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="inline-flex items-center gap-2 rounded-full bg-white/20 px-3 py-1 text-xs uppercase tracking-wider text-white/90">
              <Sparkles className="h-3.5 w-3.5" />
              실시간 채점 진행
            </p>
            <h2 className="mt-3 text-3xl font-semibold leading-tight">AI가 채점 중이에요</h2>
            <p className="mt-2 text-sm text-white/80">
              제출 답안을 분석해 모범답안과 맞춤형 피드백을 작성하고 있어요.
            </p>
          </div>
          <div className="grid w-full gap-4 text-center text-white/90 sm:grid-cols-3 md:w-auto">
            {[
              {
                label: "진행 중",
                value: loading && !activeJobs.length ? "…" : activeJobs.length,
              },
              {
                label: "평균 진행률",
                value: `${averageProgress}%`,
              },
              {
                label: "총 채점 문항",
                value: totalQuestions || "–",
              },
            ].map((stat, index) => (
              <motion.div
                key={stat.label}
                className="rounded-2xl border border-white/40 bg-white/20 px-4 py-4 text-white backdrop-blur-xl shadow-[0_20px_45px_rgba(15,23,42,0.3)]"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0, scale: [1, 1.03, 1] }}
                transition={{
                  delay: index * 0.1 + 0.2,
                  duration: 0.4,
                  scale: { duration: 3.2, repeat: Infinity, ease: "easeInOut", delay: index * 0.3 },
                }}
              >
                <p className="text-xs uppercase tracking-wide text-white/80">{stat.label}</p>
                <p className="text-3xl font-semibold">{stat.value}</p>
              </motion.div>
            ))}
          </div>
        </div>
        {loading && (
          <div className="pulse-ring absolute right-6 top-6 rounded-full bg-white/20 p-2">
            <LoadingSpinner size="sm" className="border-white/80" />
          </div>
        )}
      </motion.div>

      <Card className="border-none bg-white/80 p-0 shadow-none">
        <div className="flex flex-col gap-2 px-2 pt-2 sm:flex-row sm:items-center sm:justify-between sm:px-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">채점 대기열</h3>
            <p className="text-sm text-gray-500">
              {formatProvider(activeJobs[0]?.ai_provider)} 엔진 · 평균 남은 시간 {formatEstimatedSummary(avgEstimatedSeconds)}
            </p>
          </div>
        </div>

        <div className="relative mt-4 overflow-hidden">
          <div className="flex gap-4 overflow-x-auto pb-4 pl-2 pr-6 sm:pl-4 snap-x snap-mandatory">
            {loading && activeJobs.length === 0
              ? Array.from({ length: 2 }).map((_, index) => (
                  <div
                    key={`skeleton-${index}`}
                    className="min-w-[320px] snap-start rounded-2xl border border-gray-100 bg-gray-50/70 p-5 shadow-sm animate-pulse"
                  >
                    <div className="h-4 w-24 rounded bg-gray-200" />
                    <div className="mt-3 h-6 w-40 rounded bg-gray-200" />
                    <div className="mt-6 h-2 w-full rounded-full bg-gray-200" />
                    <div className="mt-2 h-2 w-3/4 rounded-full bg-gray-200" />
                  </div>
                ))
              : (
                <AnimatePresence initial={false}>
                  {activeJobs.map((job, index) => {
                    const status = statusConfig[job.status];
                    const StatusIcon = status.icon;
                    const progress = formatProgress(job.progress_percentage);
                    const accent = statusAccent[job.status] || "from-slate-300 to-slate-400";

                    return (
                      <motion.article
                        layout
                        initial={{ opacity: 0, y: 24 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -24 }}
                        transition={{ duration: 0.35 }}
                        key={job.job_id}
                        className="group relative min-w-[320px] snap-start rounded-2xl border border-gray-100 bg-white p-5 shadow-[0_15px_45px_rgba(15,23,42,0.08)]"
                      >
                        <div className={`absolute inset-x-4 top-2 h-1 rounded-full bg-gradient-to-r ${accent}`} />
                        <div className="flex flex-col gap-4">
                          <div className="flex items-start justify-between gap-3">
                            <div className="space-y-1">
                              <div className="flex items-center gap-2">
                                <motion.span
                                  className={`flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br ${accent}`}
                                  animate={{ scale: [1, 1.12, 1], rotate: [0, 2, -2, 0] }}
                                  transition={{
                                    duration: 3,
                                    repeat: Infinity,
                                    ease: "easeInOut",
                                    delay: index * 0.2,
                                  }}
                                >
                                  <StatusIcon className="h-4 w-4 text-white" />
                                </motion.span>
                                <Badge className={`${status.color} text-xs font-semibold`}>
                                  {status.label}
                                </Badge>
                              </div>
                              <p className="text-sm text-gray-500">
                                {formatExamLabel(job.exam_id)} · {job.total_questions}문항 채점 중
                              </p>
                              <div className="flex items-center gap-2 text-sm text-gray-700">
                                <BookOpenCheck className="h-4 w-4 text-gray-400" />
                                <span className="truncate">
                                  {formatSubmissionLabel(job.submission_id)} · 예상 {formatEstimatedTime(job.estimated_duration_seconds)}
                                </span>
                              </div>
                            </div>
                          </div>

                          <div>
                            <div className="flex items-center justify-between text-xs text-gray-500">
                              <span>진행률</span>
                              <span className="font-semibold text-gray-900">{progress}%</span>
                            </div>
                            <div className="mt-2 h-2.5 rounded-full bg-gray-100">
                              <motion.div
                                className={`h-full rounded-full bg-gradient-to-r ${accent} shadow-[0_0_12px_rgba(59,130,246,0.45)]`}
                                animate={{
                                  width: `${progress}%`,
                                  backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"],
                                }}
                                transition={{
                                  width: { duration: 0.6, ease: "easeInOut" },
                                  backgroundPosition: { duration: 2.8, repeat: Infinity, ease: "linear" },
                                }}
                              />
                            </div>
                          </div>

                          {job.error_message && (
                            <p className="flex items-center gap-2 text-sm text-rose-600">
                              <AlertCircle className="h-4 w-4" />
                              {job.error_message}
                            </p>
                          )}
                        </div>
                      </motion.article>
                    );
                  })}
                </AnimatePresence>
              )}
          </div>
        </div>
      </Card>
    </section>
  );
}

