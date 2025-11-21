import { GradingJob } from "@/types/api";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  AlertCircle,
  CheckCircle,
  Loader2,
  Timer,
  XCircle,
  BookOpenCheck,
} from "lucide-react";
import { ComponentType } from "react";

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

function formatProgress(value?: number) {
  if (value == null) return 0;
  return Math.min(100, Math.max(0, Math.round(value)));
}

function formatEstimatedTime(seconds?: number) {
  if (!seconds || seconds <= 0) return "예상 시간 계산 중";
  if (seconds < 60) return "1분 미만";
  const minutes = Math.ceil(seconds / 60);
  return `${minutes}분 내외`;
}

export function GradingJobList({ jobs, loading }: GradingJobListProps) {
  const activeJobs = jobs.filter(
    (job) => job.status === "pending" || job.status === "processing"
  );

  if (!loading && activeJobs.length === 0) {
    return null;
  }

  return (
    <Card className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">채점 진행 상황</h2>
          <p className="text-sm text-gray-500 mt-1">
            채점이 완료될 때까지 기다리지 않아도 돼요. 진행률을 확인하고 다른 작업을 이어가세요.
          </p>
        </div>
        {loading && <Loader2 className="animate-spin h-4 w-4 text-emerald-600" />}
      </div>

      {activeJobs.length === 0 && (
        <p className="text-sm text-gray-500">현재 채점 중인 시험이 없습니다.</p>
      )}

      <div className="space-y-4">
        {activeJobs.map((job) => {
          const status = statusConfig[job.status];
          const StatusIcon = status.icon;
          const progress = formatProgress(job.progress_percentage);

          return (
            <div
              key={job.job_id}
              className="border rounded-lg p-4 hover:border-blue-200 transition-colors"
            >
              <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <StatusIcon className="h-4 w-4 text-blue-600" />
                    <Badge className={status.color}>{status.label}</Badge>
                    <span className="text-sm text-gray-500">
                      예상 남은 시간 {formatEstimatedTime(job.estimated_duration_seconds)}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <BookOpenCheck className="h-4 w-4 text-gray-400" />
                    <span>
                      {job.total_questions}문제 채점 중 · 시험 #{job.exam_id.slice(-6)}
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-4">
                <div className="flex items-center justify-between text-xs text-gray-500 mb-2">
                  <span>진행률</span>
                  <span>{progress}%</span>
                </div>
                <div className="h-2 rounded-full bg-gray-100">
                  <div
                    className="h-2 rounded-full bg-blue-500 transition-all"
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

