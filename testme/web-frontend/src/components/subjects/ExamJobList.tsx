import { ExamJob, PDF } from "@/types/api";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import {
  Loader2,
  AlertCircle,
  CheckCircle,
  XCircle,
  Timer,
  FileText,
} from "lucide-react";
import { useMemo, ComponentType } from "react";

interface ExamJobListProps {
  jobs: ExamJob[];
  pdfs: PDF[];
  loading?: boolean;
  onCancel?: (jobId: string) => Promise<void> | void;
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
  if (!value) return "기본";
  if (value === "gpt") return "GPT";
  if (value === "gemini") return "Gemini";
  return value;
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

  if (!loading && activeJobs.length === 0) {
    return null;
  }

  return (
    <Card className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">생성 중인 시험</h2>
          <p className="text-sm text-gray-500 mt-1">
            AI가 PDF를 분석하여 시험을 준비하는 동안 상태를 확인할 수 있어요.
          </p>
        </div>
        {loading && <LoadingSpinner size="sm" />}
      </div>

      {activeJobs.length === 0 && (
        <p className="text-sm text-gray-500">현재 생성 중인 시험이 없습니다.</p>
      )}

      <div className="space-y-4">
        {activeJobs.map((job) => {
          const status = statusConfig[job.status];
          const StatusIcon = status.icon;
          const progress = Math.min(
            100,
            Math.max(0, Math.round(job.progress_percentage ?? 0))
          );
          const canCancel = onCancel && (job.status === "pending" || job.status === "processing");

          return (
            <div
              key={job.job_id}
              className="border rounded-lg p-4 hover:border-emerald-200 transition-colors"
            >
              <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <StatusIcon className="h-4 w-4 text-emerald-600" />
                    <Badge className={status.color}>{status.label}</Badge>
                    <span className="text-sm text-gray-500">
                      {formatProvider(job.ai_provider)} · {formatDifficulty(job.difficulty)} ·{" "}
                      {job.num_questions}문제
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <FileText className="h-4 w-4 text-gray-400" />
                    <span>{formatPdfSummary(job, pdfMap)}</span>
                  </div>
                </div>

                {canCancel && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onCancel?.(job.job_id)}
                  >
                    작업 취소
                  </Button>
                )}
              </div>

              <div className="mt-4">
                <div className="flex items-center justify-between text-xs text-gray-500 mb-2">
                  <span>진행률</span>
                  <span>{progress}%</span>
                </div>
                <div className="h-2 rounded-full bg-gray-100">
                  <div
                    className="h-2 rounded-full bg-emerald-500 transition-all"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>

              {job.error_message && (
                <p className="mt-3 text-sm text-rose-600 flex items-center gap-2">
                  <AlertCircle className="h-4 w-4" />
                  {job.error_message}
                </p>
              )}
            </div>
          );
        })}
      </div>
    </Card>
  );
}

