"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ProtectedRoute } from "@/components/layouts/ProtectedRoute";
import { AppLayout } from "@/components/layouts/AppLayout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { useToast } from "@/hooks/use-toast";
import { getExam } from "@/lib/api/exams";
import { Exam, AnswerSubmission } from "@/types/api";
import { ArrowLeft, Clock, AlertCircle, CheckCircle } from "lucide-react";

export default function ExamPage() {
  const params = useParams();
  const { toast } = useToast();
  const subjectId = params.subjectId as string;
  const examId = params.examId as string;

  const [exam, setExam] = useState<Exam | null>(null);
  const [loading, setLoading] = useState(true);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    loadExam();
    loadSavedAnswers();
  }, [examId]);

  useEffect(() => {
    // Auto-save answers to localStorage
    if (exam) {
      localStorage.setItem(`exam_${examId}_answers`, JSON.stringify(answers));
    }
  }, [answers, examId, exam]);

  const loadExam = async () => {
    try {
      const data = await getExam(subjectId, examId);
      setExam(data);
    } catch (error: any) {
      toast({
        title: "시험 로드 실패",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const loadSavedAnswers = () => {
    const saved = localStorage.getItem(`exam_${examId}_answers`);
    if (saved) {
      try {
        setAnswers(JSON.parse(saved));
      } catch (error) {
        console.error("Failed to load saved answers:", error);
      }
    }
  };

  const handleAnswerChange = (questionId: number, answer: string) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: answer,
    }));
  };

  const handleSubmit = () => {
    if (!exam) return;

    const unanswered = exam.questions.filter((q) => !answers[q.id]);
    if (unanswered.length > 0) {
      toast({
        title: "미답변 문제 있음",
        description: `${unanswered.length}개의 문제가 아직 답변되지 않았습니다.`,
        variant: "destructive",
      });
      return;
    }

    // For now, just mark as submitted
    // In the future, this would call submitExam() API
    setSubmitted(true);
    localStorage.removeItem(`exam_${examId}_answers`);
    toast({
      title: "제출 완료",
      description: "답안이 성공적으로 제출되었습니다.",
    });
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

  if (!exam) {
    return (
      <ProtectedRoute>
        <AppLayout>
          <div className="text-center">
            <h2 className="text-2xl font-bold">시험을 찾을 수 없습니다</h2>
            <Link href={`/dashboard/subjects/${subjectId}/exams`}>
              <Button className="mt-4">시험 목록으로 돌아가기</Button>
            </Link>
          </div>
        </AppLayout>
      </ProtectedRoute>
    );
  }

  if (submitted) {
    return (
      <ProtectedRoute>
        <AppLayout>
          <div className="mx-auto max-w-2xl text-center">
            <Card className="p-12">
              <CheckCircle className="mx-auto h-16 w-16 text-green-500" />
              <h2 className="mt-4 text-2xl font-bold">제출 완료!</h2>
              <p className="mt-2 text-gray-600">
                답안이 성공적으로 제출되었습니다.
              </p>
              <p className="mt-1 text-sm text-gray-500">
                (채점 기능은 백엔드 API 구현 후 추가됩니다)
              </p>
              <div className="mt-6 flex justify-center gap-3">
                <Link href={`/dashboard/subjects/${subjectId}/exams`}>
                  <Button>시험 목록</Button>
                </Link>
                <Link href={`/dashboard/subjects/${subjectId}`}>
                  <Button variant="outline">과목 페이지</Button>
                </Link>
              </div>
            </Card>
          </div>
        </AppLayout>
      </ProtectedRoute>
    );
  }

  const answeredCount = Object.keys(answers).length;
  const progress = (answeredCount / exam.questions.length) * 100;

  return (
    <ProtectedRoute>
      <AppLayout>
        <div className="mx-auto max-w-4xl space-y-6">
          {/* Header */}
          <div>
            <Link href={`/dashboard/subjects/${subjectId}/exams`}>
              <Button variant="ghost" className="mb-4">
                <ArrowLeft className="mr-2 h-4 w-4" />
                시험 목록으로
              </Button>
            </Link>
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold">시험</h1>
                <div className="mt-2 flex items-center gap-4 text-sm text-gray-600">
                  <span>{exam.num_questions}문제</span>
                  <span>•</span>
                  <span>{exam.total_points}점</span>
                  <span>•</span>
                  <div className="flex items-center gap-1">
                    <Clock className="h-4 w-4" />
                    {exam.estimated_time}분
                  </div>
                </div>
              </div>
              <Badge>
                {answeredCount} / {exam.questions.length} 답변
              </Badge>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="h-2 overflow-hidden rounded-full bg-gray-200">
            <div
              className="h-full bg-primary transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* Auto-save indicator */}
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <AlertCircle className="h-4 w-4" />
            <span>답안이 자동으로 저장됩니다</span>
          </div>

          {/* Questions */}
          <div className="space-y-6">
            {exam.questions.map((question, index) => (
              <Card key={question.id} className="p-6">
                <div className="space-y-4">
                  {/* Question Header */}
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <Badge variant="outline">문제 {index + 1}</Badge>
                        <Badge>{question.points}점</Badge>
                      </div>
                      <p className="mt-3 text-lg font-medium">
                        {question.question}
                      </p>
                    </div>
                  </div>

                  {/* Answer Input */}
                  {question.type === "multiple_choice" && question.options ? (
                    <div className="space-y-2">
                      {question.options.map((option, optionIndex) => (
                        <label
                          key={optionIndex}
                          className="flex cursor-pointer items-center gap-3 rounded-lg border p-4 transition-colors hover:bg-gray-50"
                        >
                          <input
                            type="radio"
                            name={`question_${question.id}`}
                            value={option}
                            checked={answers[question.id] === option}
                            onChange={(e) =>
                              handleAnswerChange(question.id, e.target.value)
                            }
                            className="h-4 w-4"
                          />
                          <span>{option}</span>
                        </label>
                      ))}
                    </div>
                  ) : (
                    <div>
                      <Label htmlFor={`question_${question.id}`}>
                        답안을 작성하세요
                      </Label>
                      <Textarea
                        id={`question_${question.id}`}
                        value={answers[question.id] || ""}
                        onChange={(e) =>
                          handleAnswerChange(question.id, e.target.value)
                        }
                        placeholder="여기에 답안을 작성하세요..."
                        rows={6}
                        className="mt-2"
                      />
                    </div>
                  )}
                </div>
              </Card>
            ))}
          </div>

          {/* Submit Section */}
          <Card className="sticky bottom-4 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold">
                  {answeredCount === exam.questions.length
                    ? "모든 문제에 답변했습니다!"
                    : `${exam.questions.length - answeredCount}개의 문제가 남았습니다`}
                </p>
                <p className="text-sm text-gray-600">
                  제출 전에 답안을 다시 한 번 확인하세요
                </p>
              </div>
              <Button
                size="lg"
                onClick={handleSubmit}
                disabled={submitting || answeredCount === 0}
              >
                {submitting ? "제출 중..." : "답안 제출"}
              </Button>
            </div>
          </Card>
        </div>
      </AppLayout>
    </ProtectedRoute>
  );
}

