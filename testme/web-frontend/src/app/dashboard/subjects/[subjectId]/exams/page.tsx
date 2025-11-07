"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ProtectedRoute } from "@/components/layouts/ProtectedRoute";
import { AppLayout } from "@/components/layouts/AppLayout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { useToast } from "@/hooks/use-toast";
import { getExams } from "@/lib/api/exams";
import { getSubject } from "@/lib/api/subjects";
import { Exam, Subject } from "@/types/api";
import { ArrowLeft, ClipboardList, Clock, Target, Sparkles } from "lucide-react";

export default function ExamsListPage() {
  const params = useParams();
  const { toast } = useToast();
  const subjectId = params.subjectId as string;

  const [subject, setSubject] = useState<Subject | null>(null);
  const [exams, setExams] = useState<Exam[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [subjectId]);

  const loadData = async () => {
    try {
      const [subjectData, examsData] = await Promise.all([
        getSubject(subjectId),
        getExams(subjectId),
      ]);
      setSubject(subjectData);
      setExams(examsData);
    } catch (error: any) {
      toast({
        title: "데이터 로드 실패",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case "easy":
        return "bg-green-100 text-green-800";
      case "medium":
        return "bg-yellow-100 text-yellow-800";
      case "hard":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getDifficultyText = (difficulty: string) => {
    switch (difficulty) {
      case "easy":
        return "쉬움";
      case "medium":
        return "보통";
      case "hard":
        return "어려움";
      default:
        return difficulty;
    }
  };

  if (loading) {
    return (
      <ProtectedRoute>
        <AppLayout>
          <div className="flex items-center justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        </AppLayout>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <AppLayout>
        <div className="space-y-6">
          {/* Header */}
          <div>
            <Link href={`/dashboard/subjects/${subjectId}`}>
              <Button variant="ghost" className="mb-4">
                <ArrowLeft className="mr-2 h-4 w-4" />
                과목으로 돌아가기
              </Button>
            </Link>
            <div className="flex items-center gap-3">
              {subject && (
                <div
                  className="h-4 w-4 rounded"
                  style={{ backgroundColor: subject.color || "#6B7280" }}
                />
              )}
              <h1 className="text-3xl font-bold">
                {subject?.name} - 시험 목록
              </h1>
            </div>
            <p className="mt-2 text-gray-600">
              생성된 시험 목록입니다. 시험을 선택하여 응시하세요.
            </p>
          </div>

          {/* Exams List */}
          {exams.length === 0 ? (
            <EmptyState
              icon={<ClipboardList className="h-12 w-12" />}
              title="생성된 시험이 없습니다"
              description="PDF를 업로드하고 시험을 생성하세요"
              action={
                <Link href={`/dashboard/subjects/${subjectId}`}>
                  <Button>과목 페이지로 이동</Button>
                </Link>
              }
            />
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {exams.map((exam) => (
                <Link
                  key={exam.exam_id}
                  href={`/dashboard/subjects/${subjectId}/exams/${exam.exam_id}`}
                >
                  <Card className="group cursor-pointer transition-all hover:shadow-lg">
                    <div className="p-6">
                      {/* Header */}
                      <div className="mb-4 flex items-start justify-between">
                        <div>
                          <h3 className="text-lg font-semibold group-hover:text-primary">
                            시험 #{exam.exam_id.slice(-6)}
                          </h3>
                          <p className="mt-1 text-sm text-gray-500">
                            {new Date(exam.created_at).toLocaleDateString()} 생성
                          </p>
                        </div>
                        {exam.ai_provider && (
                          <Badge variant="outline" className="flex items-center gap-1">
                            <Sparkles className="h-3 w-3" />
                            {exam.ai_provider.toUpperCase()}
                          </Badge>
                        )}
                      </div>

                      {/* Stats */}
                      <div className="space-y-2">
                        <div className="flex items-center gap-2 text-sm">
                          <ClipboardList className="h-4 w-4 text-gray-400" />
                          <span className="text-gray-600">
                            {exam.num_questions}문제
                          </span>
                          <span className="text-gray-400">•</span>
                          <span className="text-gray-600">
                            {exam.total_points}점
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                          <Clock className="h-4 w-4 text-gray-400" />
                          <span className="text-gray-600">
                            예상 시간: {exam.estimated_time}분
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                          <Target className="h-4 w-4 text-gray-400" />
                          <Badge className={getDifficultyColor(exam.difficulty)}>
                            {getDifficultyText(exam.difficulty)}
                          </Badge>
                        </div>
                      </div>

                      {/* CTA */}
                      <div className="mt-4 border-t pt-4">
                        <Button className="w-full" size="sm">
                          시험 보기
                        </Button>
                      </div>
                    </div>
                  </Card>
                </Link>
              ))}
            </div>
          )}
        </div>
      </AppLayout>
    </ProtectedRoute>
  );
}

