"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
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
import { getExam, submitExam, getSubmission, getGradingJobs } from "@/lib/api/exams";
import { Exam, SubmissionResult } from "@/types/api";
import { ArrowLeft, Clock, AlertCircle, CheckCircle, Award, TrendingUp, ChevronDown, ChevronUp } from "lucide-react";
import { MathText } from "@/components/ui/math-text";

export default function ExamPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const subjectId = params.subjectId as string;
  const examId = params.examId as string;

  const [exam, setExam] = useState<Exam | null>(null);
  const [loading, setLoading] = useState(true);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [submissionResult, setSubmissionResult] = useState<SubmissionResult | null>(null);
  const [gradingStatus, setGradingStatus] = useState<'idle' | 'submitting' | 'grading' | 'completed' | 'failed'>('idle');
  const [gradingProgress, setGradingProgress] = useState<number | null>(null);
  const [gradingEstimate, setGradingEstimate] = useState<string | null>(null);
  const [expandedQuestions, setExpandedQuestions] = useState<Set<number>>(new Set());
  const [allQuestionsLoaded, setAllQuestionsLoaded] = useState(false);

  useEffect(() => {
    loadExam();
  }, [examId]);

  useEffect(() => {
    // Auto-save answers to localStorage (only if not submitted)
    if (exam && gradingStatus === 'idle') {
      localStorage.setItem(`exam_${examId}_answers`, JSON.stringify(answers));
    }
  }, [answers, examId, exam, gradingStatus]);

  // Poll for grading result if status is 'grading'
  useEffect(() => {
    if (gradingStatus === 'grading') {
      const pollInterval = setInterval(async () => {
        try {
          const result = await getSubmission(subjectId, examId);
          if (result.status === 'graded') {
            setSubmissionResult(result);
            setGradingStatus('completed');
            clearInterval(pollInterval);
            toast({
              title: "채점 완료",
              description: "답안이 성공적으로 채점되었습니다.",
            });
          } else if (result.status === 'failed') {
            setSubmissionResult(result);
            setGradingStatus('failed');
            clearInterval(pollInterval);
            toast({
              title: "채점 실패",
              description: result.error_message || "채점 중 오류가 발생했습니다.",
              variant: "destructive",
            });
          }
        } catch (error) {
          console.error("Failed to poll grading result:", error);
        }
      }, 3000); // Poll every 3 seconds

      return () => clearInterval(pollInterval);
    }
  }, [gradingStatus, subjectId, examId, toast]);

  // Fetch grading progress for UX display
  useEffect(() => {
    if (gradingStatus !== 'grading') {
      setGradingProgress(null);
      setGradingEstimate(null);
      return;
    }

    let cancelled = false;

    const fetchProgress = async () => {
      try {
        const jobs = await getGradingJobs(subjectId);
        const job = jobs.find((job) => job.exam_id === examId);
        if (!job || cancelled) return;

        const progress = job.progress_percentage ?? job.progress ?? null;
        if (progress !== null) {
          setGradingProgress(Math.max(0, Math.min(100, Math.round(progress))));
        }

        if (job.estimated_duration_seconds) {
          const minutes = Math.ceil(job.estimated_duration_seconds / 60);
          setGradingEstimate(`${minutes}분 내외 예상`);
        } else {
          setGradingEstimate(null);
        }
      } catch (error) {
        console.warn("Failed to fetch grading job progress:", error);
      }
    };

    fetchProgress();
    const interval = setInterval(fetchProgress, 4000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [gradingStatus, subjectId, examId]);

  const loadExam = async () => {
    try {
      const data = await getExam(subjectId, examId);
      setExam(data);
      
      // Check if there's already a submission for this exam
      try {
        const submission = await getSubmission(subjectId, examId);
        
        // Restore answers from submission
        if (submission.answers && Array.isArray(submission.answers)) {
          const restoredAnswers: Record<number, string> = {};
          submission.answers.forEach((answer: any) => {
            restoredAnswers[answer.question_id] = answer.answer;
          });
          setAnswers(restoredAnswers);
        }
        
        // If submission exists, show result based on status
        if (submission.status === 'graded') {
          setSubmissionResult(submission);
          setGradingStatus('completed');
          
          // Expand all questions initially when showing graded results
          if (submission.grading_result?.question_results) {
            const allQuestionIds = new Set(
              submission.grading_result.question_results.map((r: any) => r.question_id)
            );
            setExpandedQuestions(allQuestionIds);
            setAllQuestionsLoaded(true);
          }
        } else if (submission.status === 'grading' || submission.status === 'pending') {
          setSubmissionResult(submission);
          setGradingStatus('grading');
        } else if (submission.status === 'failed') {
          setSubmissionResult(submission);
          setGradingStatus('failed');
        }
      } catch (error: any) {
        // No submission found or error - this is fine, user hasn't taken the exam yet
        if (error.response?.status !== 404) {
          console.warn("Failed to check submission status:", error);
        }
        // Load saved answers from localStorage if no submission
        loadSavedAnswers();
      }
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

  const handleSubmit = async () => {
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

    setSubmitting(true);
    setGradingStatus('submitting');

    try {
      // Convert answers to the format expected by the API
      const answersArray = exam.questions.map((q) => ({
        question_id: q.id,
        answer: answers[q.id],
      }));

      await submitExam(subjectId, examId, answersArray);
      setGradingStatus('grading');
      localStorage.removeItem(`exam_${examId}_answers`);
      toast({
        title: "제출 완료",
        description: "채점이 백그라운드에서 진행됩니다. 진행 상황은 채점 진행 섹션에서 확인하세요.",
      });
      router.push(`/dashboard/subjects/${subjectId}?tab=exams`);
    } catch (error: any) {
      setGradingStatus('failed');
      toast({
        title: "제출 실패",
        description: error.message || "답안 제출 중 오류가 발생했습니다.",
        variant: "destructive",
      });
    } finally {
      setSubmitting(false);
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

  // Show grading status or result if submitted
  if (gradingStatus === 'grading') {
    return (
      <ProtectedRoute>
        <AppLayout>
          <div className="mx-auto max-w-3xl space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">시험 채점</p>
                <h1 className="text-3xl font-bold mt-1">채점 중...</h1>
              </div>
              <Link href={`/dashboard/subjects/${subjectId}?tab=exams`}>
                <Button variant="outline">시험 목록으로 돌아가기</Button>
              </Link>
            </div>

            <div className="rounded-2xl border border-gray-200 bg-white/80 shadow-sm p-6 md:p-8">
              <div className="flex flex-col gap-4 md:flex-row md:items-start md:gap-6">
                <div className="flex items-center md:items-start">
                  <div className="relative h-14 w-14">
                    <div className="absolute inset-0 rounded-full border-4 border-emerald-100" />
                    <div className="absolute inset-0 rounded-full border-4 border-t-emerald-500 animate-spin" />
                  </div>
                </div>
                <div className="space-y-2">
                  <p className="text-xl font-semibold text-gray-900">
                    AI가 답안을 채점하고 있어요
                  </p>
                  <p className="text-gray-600 leading-relaxed">
                    보통 1~2분이면 끝나요. 채점이 끝나면 자동으로 결과 페이지로 이동하니, 잠깐 다른 페이지를 둘러봐도 괜찮아요.
                  </p>
                  <ul className="text-sm text-gray-500 list-disc ml-5 space-y-1">
                    <li>문제 수나 난이도에 따라 시간이 조금 더 걸릴 수 있어요.</li>
                    <li>완료되면 알림과 함께 결과 화면으로 이동합니다.</li>
                  </ul>
                  {gradingProgress !== null && (
                    <div className="pt-2">
                      <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                        <span>현재 진행률</span>
                        <span>{gradingProgress}% 진행 중이에요</span>
                      </div>
                      <div className="h-2 rounded-full bg-gray-100">
                        <div
                          className="h-2 rounded-full bg-blue-500 transition-all"
                          style={{ width: `${gradingProgress}%` }}
                        />
                      </div>
                      {gradingEstimate && (
                        <p className="text-xs text-gray-400 mt-2">{gradingEstimate}</p>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </AppLayout>
      </ProtectedRoute>
    );
  }

  if (gradingStatus === 'completed' && submissionResult?.grading_result) {
    const { grading_result } = submissionResult;
    
    // Format dates for display
    const formatDateTime = (isoString: string) => {
      const date = new Date(isoString);
      return date.toLocaleString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    };
    
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
              <div className="space-y-2">
                <h1 className="text-3xl font-bold">채점 결과</h1>
                {exam && (
                  <p className="text-lg text-gray-600">{exam.title || '시험'}</p>
                )}
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  {submissionResult.submitted_at && (
                    <span>제출: {formatDateTime(submissionResult.submitted_at)}</span>
                  )}
                  {submissionResult.graded_at && (
                    <>
                      <span>•</span>
                      <span>채점: {formatDateTime(submissionResult.graded_at)}</span>
                    </>
                  )}
                </div>
              </div>
            </div>

            {/* Score Summary */}
            <Card className="p-8">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="rounded-full bg-emerald-100 p-4">
                    <Award className="h-8 w-8 text-emerald-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">총점</p>
                    <p className="text-4xl font-bold text-emerald-600">
                      {grading_result.total_score} / {grading_result.max_score}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600">정답률</p>
                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-emerald-600" />
                    <p className="text-3xl font-bold text-emerald-600">
                      {grading_result.percentage.toFixed(1)}%
                    </p>
                  </div>
                </div>
              </div>
            </Card>

            {/* Question Results */}
            <div className="space-y-6">
              {grading_result.question_results.map((result, index) => {
                const question = exam?.questions.find(
                  (q) => q.id === result.question_id
                );
                const myAnswer = answers[result.question_id];
                const scorePercentage = (result.score / result.max_points) * 100;
                const isExpanded = expandedQuestions.has(result.question_id);
                
                // Simple color coding based on score
                let scoreColor = "text-gray-900";
                if (scorePercentage === 100) {
                  scoreColor = "text-emerald-600";
                } else if (scorePercentage >= 80) {
                  scoreColor = "text-blue-600";
                } else if (scorePercentage >= 60) {
                  scoreColor = "text-amber-600";
                } else {
                  scoreColor = "text-rose-600";
                }

                const toggleExpand = () => {
                  const newExpanded = new Set(expandedQuestions);
                  if (isExpanded) {
                    newExpanded.delete(result.question_id);
                  } else {
                    newExpanded.add(result.question_id);
                  }
                  setExpandedQuestions(newExpanded);
                };

                return (
                  <div key={result.question_id} className="border-b border-gray-200 pb-6 last:border-0">
                    {/* Question Header */}
                    <div className="flex items-baseline justify-between mb-4">
                      <h3 className="text-xl font-bold text-gray-900">
                        문제 {index + 1}
                      </h3>
                      <span className={`text-lg font-semibold ${scoreColor}`}>
                        {result.score} / {result.max_points}점
                      </span>
                    </div>

                    {/* Question Text */}
                    <div className="mb-4">
                      <div className="text-base text-gray-800 leading-relaxed">
                        <MathText text={question?.question || ""} />
                      </div>
                    </div>

                    {/* My Answer */}
                    <div className="mb-4">
                      <div className="text-sm font-semibold text-gray-600 mb-2">
                        내 답변
                      </div>
                      <div className="pl-4 border-l-2 border-gray-300 text-gray-700">
                        <MathText text={myAnswer || ""} />
                      </div>
                    </div>

                    {/* Expandable Section - Model Answer & Feedback */}
                    <div className="mt-4">
                      <button
                        onClick={toggleExpand}
                        className="flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
                      >
                        {isExpanded ? (
                          <>
                            <ChevronUp className="h-4 w-4" />
                            <span>피드백 접기</span>
                          </>
                        ) : (
                          <>
                            <ChevronDown className="h-4 w-4" />
                            <span>모범답안 및 피드백 보기</span>
                          </>
                        )}
                      </button>

                      {isExpanded && (
                        <div className="mt-4 space-y-4">
                          {/* Model Answer */}
                          {result.model_answer && (
                            <div>
                              <div className="text-sm font-semibold text-emerald-700 mb-2">
                                모범답안
                              </div>
                              <div className="pl-4 border-l-2 border-emerald-500 text-gray-800">
                                <MathText text={result.model_answer} />
                              </div>
                            </div>
                          )}

                          {/* Feedback */}
                          <div>
                            <div className="text-sm font-semibold text-blue-700 mb-2">
                              피드백
                            </div>
                            <div className="pl-4 border-l-2 border-blue-500 text-gray-800">
                              <MathText text={result.feedback} />
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Action Buttons */}
            <div className="flex justify-center gap-3">
              <Link href={`/dashboard/subjects/${subjectId}/exams`}>
                <Button size="lg">시험 목록</Button>
              </Link>
              <Link href={`/dashboard/subjects/${subjectId}`}>
                <Button variant="outline" size="lg">
                  과목 페이지
                </Button>
              </Link>
            </div>
          </div>
        </AppLayout>
      </ProtectedRoute>
    );
  }

  if (gradingStatus === 'failed') {
    return (
      <ProtectedRoute>
        <AppLayout>
          <div className="mx-auto max-w-2xl text-center">
            <Card className="p-12">
              <AlertCircle className="mx-auto h-16 w-16 text-red-500" />
              <h2 className="mt-4 text-2xl font-bold">채점 실패</h2>
              <p className="mt-2 text-gray-600">
                {submissionResult?.error_message || "채점 중 오류가 발생했습니다."}
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
                <h1 className="text-3xl font-bold">{exam.title || '시험'}</h1>
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
                      <div className="mt-3 text-lg font-medium">
                        <MathText text={question.question} />
                      </div>
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

