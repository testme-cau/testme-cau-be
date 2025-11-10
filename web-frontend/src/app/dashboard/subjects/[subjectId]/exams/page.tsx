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
import { getExams, deleteExam } from "@/lib/api/exams";
import { getSubject } from "@/lib/api/subjects";
import { Exam, Subject } from "@/types/api";
import { ArrowLeft, ClipboardList, Clock, Target, Trash2 } from "lucide-react";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";

export default function ExamsListPage() {
  const params = useParams();
  const { toast } = useToast();
  const subjectId = params.subjectId as string;

  const [subject, setSubject] = useState<Subject | null>(null);
  const [exams, setExams] = useState<Exam[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [examToDelete, setExamToDelete] = useState<Exam | null>(null);
  const [deleting, setDeleting] = useState(false);

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

  const getSubmissionStatusBadge = (exam: any) => {
    if (!exam.submission_status) {
      return (
        <Badge className="bg-green-100 text-green-800">
          미응시
        </Badge>
      );
    }
    
    switch (exam.submission_status) {
      case 'graded':
        return (
          <Badge className="bg-blue-100 text-blue-800">
            채점완료
          </Badge>
        );
      case 'grading':
      case 'pending':
        return (
          <Badge className="bg-yellow-100 text-yellow-800">
            채점중
          </Badge>
        );
      case 'failed':
        return (
          <Badge className="bg-red-100 text-red-800">
            채점실패
          </Badge>
        );
      default:
        return null;
    }
  };

  const getButtonText = (exam: any) => {
    if (!exam.submission_status) {
      return "시험 응시하기";
    }
    
    if (exam.submission_status === 'graded') {
      return "결과 보기";
    }
    
    if (exam.submission_status === 'grading' || exam.submission_status === 'pending') {
      return "채점 확인하기";
    }
    
    return "시험 보기";
  };

  const handleDeleteClick = (exam: Exam, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setExamToDelete(exam);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!examToDelete) return;

    setDeleting(true);
    try {
      await deleteExam(subjectId, examToDelete.exam_id);
      toast({
        title: "시험 삭제 완료",
        description: "시험이 성공적으로 삭제되었습니다.",
      });
      // Reload exams list
      await loadData();
    } catch (error: any) {
      toast({
        title: "시험 삭제 실패",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setDeleting(false);
      setDeleteDialogOpen(false);
      setExamToDelete(null);
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
            <>
              <div className="grid gap-4 md:grid-cols-2">
                {exams.map((exam) => (
                  <Card key={exam.exam_id} className="group transition-all hover:shadow-lg">
                    <div className="p-6">
                      {/* Header */}
                      <div className="mb-4 flex items-start justify-between">
                        <div className="flex-1">
                          <div className="mb-2 flex items-center gap-2">
                            {getSubmissionStatusBadge(exam)}
                          </div>
                          <h3 className="text-lg font-semibold">
                            {exam.title || `시험 #${exam.exam_id.slice(-6)}`}
                          </h3>
                          <p className="mt-1 text-sm text-gray-500">
                            {new Date(exam.created_at).toLocaleDateString()} 생성
                            {(exam as any).submission_status === 'graded' && (exam as any).score !== undefined && (
                              <span className="ml-2 font-semibold text-blue-600">
                                • {(exam as any).score}/{(exam as any).max_score}점
                              </span>
                            )}
                          </p>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0 text-gray-400 hover:text-red-600"
                          onClick={(e) => handleDeleteClick(exam, e)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
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
                        <Link href={`/dashboard/subjects/${subjectId}/exams/${exam.exam_id}`}>
                          <Button className="w-full" size="sm">
                            {getButtonText(exam)}
                          </Button>
                        </Link>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>

              {/* Delete Confirmation Dialog */}
              <ConfirmDialog
                open={deleteDialogOpen}
                onOpenChange={setDeleteDialogOpen}
                onConfirm={handleDeleteConfirm}
                title="시험 삭제"
                description={`"${examToDelete?.title || "이 시험"}"을(를) 정말 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.`}
                confirmText="삭제"
                cancelText="취소"
                variant="destructive"
                loading={deleting}
              />
            </>
          )}
        </div>
      </AppLayout>
    </ProtectedRoute>
  );
}

