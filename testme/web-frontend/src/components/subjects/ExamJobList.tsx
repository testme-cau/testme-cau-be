import { ExamJob, PDF } from "@/types/api";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Loader2,
  AlertCircle,
  CheckCircle,
  XCircle,
  Timer,
  FileText,
} from "lucide-react";
import { useMemo, ComponentType } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface ExamJobListProps {
  jobs: ExamJob[];
  pdfs: PDF[];
  loading?: boolean;
  onCancel?: (job: ExamJob) => Promise<void> | void;
}

const statusConfig: Record<
  ExamJob["status"],
  { label: string; color: string; icon: ComponentType<any> }
> = {
  pending: { label: "대기 중", color: "bg-amber-100 text-amber-800", icon: Timer },
  processing: {
    label: "생성 중",
    color: "bg-emerald-100 text-emerald-800",
    icon: Loader2,
  },
  completed: {
    label: "완료됨",
    color: "bg-blue-100 text-blue-800",
    icon: CheckCircle,
  },
  failed: { label: "실패", color: "bg-rose-100 text-rose-800", icon: AlertCircle },
  cancelled: { label: "취소됨", color: "bg-gray-100 text-gray-700", icon: XCircle },
};

const statusAccent: Record<ExamJob["status"], string> = {
  pending: "from-amber-400/80 via-orange-400/70 to-yellow-300/60",
  processing: "from-emerald-400/90 via-teal-400/80 to-cyan-300/70",
  completed: "from-sky-400/80 via-blue-400/70 to-indigo-300/60",
  failed: "from-rose-500/80 via-pink-500/70 to-orange-400/70",
  cancelled: "from-gray-400/80 via-slate-400/70 to-zinc-300/60",
};

function formatPdfSummary(job: ExamJob, pdfMap: Record<string, string>) {
  if (!job.pdf_ids || job.pdf_ids.length === 0) return "PDF 미지정";
  const names = job.pdf_ids
    .map((id) => pdfMap[id] || "알 수 없는 PDF")
    .filter(Boolean);
  if (names.length === 0) {
    return `${job.pdf_ids.length}개의 PDF`;
  }
  if (names.length === 1) return names[0];
  return `${names[0]} 외 ${names.length - 1}개`;
}

function formatDifficulty(value: ExamJob["difficulty"]) {
  switch (value) {
    case "easy":
      return "쉬움";
    case "medium":
      return "보통";
    case "hard":
      return "어려움";
    default:
      return value;
  }
}

function formatProvider(value?: string) {
  if (!value) return "기본 모델";
  if (value === "gpt") return "OpenAI GPT";
  if (value === "gemini") return "Google Gemini";
  return value;
}

function formatModelLabel(job: ExamJob) {
  if (job.ai_model && job.ai_model.trim().length > 0) {
    return job.ai_model;
  }
  return formatProvider(job.ai_provider);
}

export function ExamJobList({ jobs, pdfs, loading, onCancel }: ExamJobListProps) {
  const pdfMap = useMemo(() => {
    const map: Record<string, string> = {};
    pdfs.forEach((pdf) => {
      map[pdf.file_id] = pdf.original_filename;
    });
    return map;
  }, [pdfs]);

  const activeJobs = useMemo(
    () => jobs.filter((job) => job.status === "pending" || job.status === "processing"),
    [jobs]
  );

  const averageProgress = useMemo(() => {
    if (!activeJobs.length) return 0;
    const sum = activeJobs.reduce(
      (acc, job) => acc + (typeof job.progress_percentage === "number" ? job.progress_percentage : 0),
      0
    );
    return Math.round(sum / activeJobs.length);
  }, [activeJobs]);

  const totalQuestions = useMemo(
    () => activeJobs.reduce((acc, job) => acc + (job.num_questions || 0), 0),
    [activeJobs]
  );

  const totalPdfsInQueue = useMemo(
    () => activeJobs.reduce((acc, job) => acc + (job.pdf_ids?.length || 0), 0),
    [activeJobs]
  );

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
          backgroundImage: "linear-gradient(120deg, #059669 0%, #0d9488 45%, #0ea5e9 100%)",
          backgroundSize: "200% 200%",
        }}
      >
        <div className="absolute inset-0 pointer-events-none">
          <div className="glow-orb left-1/4 top-0 h-40 w-40 bg-white/40" />
          <div className="glow-orb right-8 bottom-0 h-56 w-56 bg-emerald-300/60" />
        </div>
        <div className="relative flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-3xl font-semibold leading-tight">시험 생성 중</h2>
            <p className="mt-3 text-sm text-white/80">시험을 준비 중이에요. 잠시만 기다려 주세요.</p>
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
                label: "총 문항 수",
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
      </motion.div>

      <Card className="border-none bg-white/80 p-0 shadow-none">
        <div className="flex flex-col gap-2 px-2 pt-2 sm:flex-row sm:items-center sm:justify-between sm:px-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">실시간 대기열</h3>
            <p className="text-sm text-gray-500">PDF {totalPdfsInQueue}개 처리 중</p>
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
                    const progress = Math.min(
                      100,
                      Math.max(0, Math.round(typeof job.progress_percentage === "number" ? job.progress_percentage : 0))
                    );
                    const canCancel = onCancel && (job.status === "pending" || job.status === "processing");
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
                                {formatModelLabel(job)} · {formatDifficulty(job.difficulty)} · {job.num_questions}문항
                              </p>
                              <div className="flex items-center gap-2 text-sm text-gray-700">
                                <FileText className="h-4 w-4 text-gray-400" />
                                <span className="truncate">{formatPdfSummary(job, pdfMap)}</span>
                              </div>
                            </div>
                            {canCancel && (
                              <Button
                                variant="outline"
                                size="sm"
                                className="border-gray-200 text-gray-700 hover:border-rose-200 hover:text-rose-600"
                                onClick={() => onCancel?.(job)}
                              >
                                작업 취소
                              </Button>
                            )}
                          </div>

                          <div>
                            <div className="flex items-center justify-between text-xs text-gray-500">
                              <span>진행률</span>
                              <span className="font-semibold text-gray-900">{progress}%</span>
                            </div>
                            <div className="mt-2 h-2.5 rounded-full bg-gray-100">
                              <motion.div
                                className={`h-full rounded-full bg-gradient-to-r ${accent} shadow-[0_0_12px_rgba(16,185,129,0.45)]`}
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

