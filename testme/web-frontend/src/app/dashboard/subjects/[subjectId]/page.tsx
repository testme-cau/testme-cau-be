"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { ProtectedRoute } from "@/components/layouts/ProtectedRoute";
import { AppLayout } from "@/components/layouts/AppLayout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { EmptyState } from "@/components/ui/empty-state";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { useToast } from "@/hooks/use-toast";
import { getSubject, updateSubject } from "@/lib/api/subjects";
import { getPDFs, uploadPDF } from "@/lib/api/pdfs";
import {
  getExams,
  deleteExam,
  getExamJobs,
  cancelExamJob,
  getGradingJobs,
} from "@/lib/api/exams";
import { groupsApi } from "@/lib/api/groups";
import { Subject, PDF, Group, Exam, ExamJob, GradingJob } from "@/types/api";
import { SubjectHeader } from "@/components/subjects/SubjectHeader";
import { SubjectGroupSelector } from "@/components/subjects/SubjectGroupSelector";
import { PDFUploadZone } from "@/components/subjects/PDFUploadZone";
import { PDFList } from "@/components/subjects/PDFList";
import { ArrowLeft, ClipboardList, Clock, Target, Trash2, FileText, Plus } from "lucide-react";
import { ExamJobList } from "@/components/subjects/ExamJobList";
import { GradingJobList } from "@/components/subjects/GradingJobList";

export default function SubjectDetailPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const { toast } = useToast();
  const subjectId = params.subjectId as string;

  const [activeTab, setActiveTab] = useState<"exams" | "pdfs">("exams");
  const [subject, setSubject] = useState<Subject | null>(null);
  const [pdfs, setPdfs] = useState<PDF[]>([]);
  const [exams, setExams] = useState<Exam[]>([]);
  const [examJobs, setExamJobs] = useState<ExamJob[]>([]);
  const [examJobsLoading, setExamJobsLoading] = useState(false);
  const [gradingJobs, setGradingJobs] = useState<GradingJob[]>([]);
  const [gradingJobsLoading, setGradingJobsLoading] = useState(false);
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [updatingGroup, setUpdatingGroup] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<{ current: number; total: number } | undefined>();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [examToDelete, setExamToDelete] = useState<Exam | null>(null);
  const [deleting, setDeleting] = useState(false);

  const prevExamJobCount = useRef(0);
  const prevGradingJobCount = useRef(0);

  const refreshExams = useCallback(async () => {
    if (!subjectId) return;
    const data = await getExams(subjectId);
    setExams(data || []);
  }, [subjectId, readLocalExamJobs]);

  const storageKey = `pendingExamJobs:${subjectId}`;

  const readLocalExamJobs = useCallback((): ExamJob[] => {
    try {
      const raw = sessionStorage.getItem(storageKey);
      if (!raw) return [];
      const parsed = JSON.parse(raw);
      if (!Array.isArray(parsed)) return [];
      return parsed.filter(
        (job) => job && (job.status === "pending" || job.status === "processing")
      );
    } catch {
      return [];
    }
  }, [storageKey]);

  const writeLocalExamJobs = useCallback(
    (jobs: ExamJob[]) => {
      try {
        if (!jobs.length) {
          sessionStorage.removeItem(storageKey);
          return;
        }
        sessionStorage.setItem(storageKey, JSON.stringify(jobs));
      } catch (error) {
        console.warn("Failed to persist local exam jobs:", error);
      }
    },
    [storageKey]
  );

  const fetchExamJobs = useCallback(async () => {
    if (!subjectId) return;
    setExamJobsLoading(true);
    try {
      const jobs = await getExamJobs(subjectId);
      const activeJobs =
        jobs?.filter((job) => job.status === "pending" || job.status === "processing") || [];
      if (prevExamJobCount.current > 0 && activeJobs.length < prevExamJobCount.current) {
        try {
          await refreshExams();
        } catch (error: any) {
          toast({
            title: "시험 목록 갱신 실패",
            description: error.message,
            variant: "destructive",
          });
        }
      }
      prevExamJobCount.current = activeJobs.length;
      const localJobs = readLocalExamJobs();
      const serverIds = new Set(activeJobs.map((job) => job.job_id));
      const remainingLocal = localJobs.filter((job) => !serverIds.has(job.job_id));
      if (remainingLocal.length !== localJobs.length) {
        writeLocalExamJobs(remainingLocal);
      }
      setExamJobs([...activeJobs, ...remainingLocal]);
    } catch (error: any) {
      toast({
        title: "생성 작업 로드 실패",
        description: error.message,
        variant: "destructive",
      });
      const localJobs = readLocalExamJobs();
      if (localJobs.length) {
        setExamJobs(localJobs);
      }
    } finally {
      setExamJobsLoading(false);
    }
  }, [subjectId, toast, refreshExams, readLocalExamJobs, writeLocalExamJobs]);

  const fetchGradingJobs = useCallback(async () => {
    if (!subjectId) return;
    setGradingJobsLoading(true);
    try {
      const jobs = await getGradingJobs(subjectId);
      const activeJobs =
        jobs?.filter((job) => job.status === "pending" || job.status === "processing") || [];
      if (prevGradingJobCount.current > 0 && activeJobs.length < prevGradingJobCount.current) {
        try {
          await refreshExams();
        } catch (error: any) {
          toast({
            title: "시험 목록 갱신 실패",
            description: error.message,
            variant: "destructive",
          });
        }
      }
      prevGradingJobCount.current = activeJobs.length;
      setGradingJobs(activeJobs);
    } catch (error: any) {
      toast({
        title: "채점 작업 로드 실패",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setGradingJobsLoading(false);
    }
  }, [subjectId, toast, refreshExams]);

  const loadData = useCallback(async () => {
    if (!subjectId) return;
    try {
      const [subjectData, pdfsData, groupsData] = await Promise.all([
        getSubject(subjectId),
        getPDFs(subjectId),
        groupsApi.getGroups(),
      ]);
      setSubject(subjectData);
      setPdfs(pdfsData || []);
      setGroups(groupsData || []);
      await Promise.all([refreshExams(), fetchExamJobs(), fetchGradingJobs()]);
    } catch (error: any) {
      toast({
        title: "데이터 로드 실패",
        description: error.message,
        variant: "destructive",
      });
      setPdfs([]);
      setExams([]);
      setGroups([]);
      setExamJobs([]);
      setGradingJobs([]);
    } finally {
      setLoading(false);
    }
  }, [subjectId, toast, fetchExamJobs, fetchGradingJobs, refreshExams]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    const tabParam = searchParams?.get("tab");
    if (tabParam === "pdfs" || tabParam === "exams") {
      setActiveTab(tabParam);
    }
  }, [searchParams]);

  useEffect(() => {
    if (!subjectId) return;
    fetchExamJobs();
    fetchGradingJobs();
  }, [subjectId, fetchExamJobs, fetchGradingJobs]);

  useEffect(() => {
    prevExamJobCount.current = 0;
    prevGradingJobCount.current = 0;
    setExamJobs(readLocalExamJobs());
  }, [subjectId]);

  const activeExamJobs = useMemo(
    () => examJobs.filter((job) => job.status === "pending" || job.status === "processing"),
    [examJobs]
  );

  useEffect(() => {
    if (!activeExamJobs.length) return;
    const interval = setInterval(() => {
      fetchExamJobs();
    }, 5000);
    return () => clearInterval(interval);
  }, [activeExamJobs.length, fetchExamJobs]);

  const activeGradingJobs = useMemo(
    () => gradingJobs.filter((job) => job.status === "pending" || job.status === "processing"),
    [gradingJobs]
  );

  useEffect(() => {
    if (!activeGradingJobs.length) return;
    const interval = setInterval(() => {
      fetchGradingJobs();
    }, 5000);
    return () => clearInterval(interval);
  }, [activeGradingJobs.length, fetchGradingJobs]);

  const showExamJobSection = examJobsLoading || examJobs.length > 0;
  const showGradingJobSection = gradingJobsLoading || gradingJobs.length > 0;

  const handleGroupChange = async (groupId: string) => {
    if (!subject) return;
    
    setUpdatingGroup(true);
    try {
      await updateSubject(subjectId, {
        name: subject.name,
        description: subject.description || undefined,
        group_id: groupId === "none" ? undefined : groupId,
      });
      
      setSubject({
        ...subject,
        group_id: groupId === "none" ? undefined : groupId,
      });
      
      toast({
        title: "그룹 변경 완료",
        description: "과목의 그룹이 변경되었습니다.",
      });
    } catch (error: any) {
      toast({
        title: "그룹 변경 실패",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setUpdatingGroup(false);
    }
  };

  const handleCancelExamJob = async (jobId: string) => {
    if (!subjectId) return;
    try {
      await cancelExamJob(subjectId, jobId);
      toast({
        title: "작업 취소됨",
        description: "시험 생성 작업이 취소되었습니다.",
      });
      fetchExamJobs();
    } catch (error: any) {
      toast({
        title: "작업 취소 실패",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  const handleFileUpload = async (files: File[]) => {
    if (files.length === 0) return;

    setUploading(true);
    setUploadProgress({ current: 0, total: files.length });

    let successCount = 0;
    let failCount = 0;
    const errors: string[] = [];

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      try {
        await uploadPDF(subjectId, file);
        successCount++;
        setUploadProgress({ current: i + 1, total: files.length });
      } catch (error: any) {
        failCount++;
        errors.push(`${file.name}: ${error.message}`);
      }
    }

    // 결과 토스트
    if (successCount > 0 && failCount === 0) {
      toast({
        title: "업로드 완료",
        description: `${successCount}개의 PDF가 성공적으로 업로드되었습니다.`,
      });
    } else if (successCount > 0 && failCount > 0) {
      toast({
        title: "일부 업로드 실패",
        description: `${successCount}개 성공, ${failCount}개 실패`,
        variant: "destructive",
      });
    } else {
      toast({
        title: "업로드 실패",
        description: errors[0] || "파일 업로드에 실패했습니다.",
        variant: "destructive",
      });
    }

    setUploading(false);
    setUploadProgress(undefined);
    await loadData();
  };

  // Exam helper functions
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

  // Calculate exam counts per PDF
  const examCountsByPdf = pdfs.reduce((acc, pdf) => {
    const count = exams.filter((exam) => {
      const pdfIds = (exam as any).pdf_ids || [(exam as any).pdf_id];
      return pdfIds.includes(pdf.file_id);
    }).length;
    acc[pdf.file_id] = count;
    return acc;
  }, {} as Record<string, number>);


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

  if (!subject) {
    return (
      <ProtectedRoute>
        <AppLayout>
          <div className="text-center">
            <h2 className="text-2xl font-bold">과목을 찾을 수 없습니다</h2>
            <Link href="/dashboard">
              <Button className="mt-4">대시보드로 돌아가기</Button>
            </Link>
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
            <Link href="/dashboard">
              <Button variant="ghost" className="mb-4">
                <ArrowLeft className="mr-2 h-4 w-4" />
                대시보드로 돌아가기
              </Button>
            </Link>
            <div className="flex items-center gap-3">
              {subject && (
                <div
                  className="h-4 w-4 rounded"
                  style={{ backgroundColor: subject.color || "#6B7280" }}
                />
              )}
              <h1 className="text-3xl font-bold">{subject?.name}</h1>
            </div>
          </div>

          {/* Group Selector */}
          <SubjectGroupSelector
            currentGroupId={subject.group_id || undefined}
            groups={groups}
            loading={updatingGroup}
            onChange={handleGroupChange}
          />

          {/* Tabs */}
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab("exams")}
                className={`whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium transition-colors ${
                  activeTab === "exams"
                    ? "border-emerald-600 text-emerald-600"
                    : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700"
                }`}
              >
                <div className="flex items-center gap-2">
                  <ClipboardList className="h-4 w-4" />
                  <span>시험 목록</span>
                  <Badge className="ml-1 bg-gray-100 text-gray-700">
                    {exams.length}
                  </Badge>
                </div>
              </button>
              <button
                onClick={() => setActiveTab("pdfs")}
                className={`whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium transition-colors ${
                  activeTab === "pdfs"
                    ? "border-emerald-600 text-emerald-600"
                    : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700"
                }`}
              >
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4" />
                  <span>PDF 자료</span>
                  <Badge className="ml-1 bg-gray-100 text-gray-700">
                    {pdfs.length}
                  </Badge>
                </div>
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          {activeTab === "exams" ? (
            <div className="space-y-4">
              {/* Header with Create Button */}
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold">시험 목록</h2>
                  <p className="mt-1 text-sm text-gray-600">
                    생성된 시험 목록입니다. 시험을 선택하여 응시하세요.
                  </p>
                </div>
                <Link href={`/dashboard/subjects/${subjectId}/exams/new`}>
                  <Button className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white shadow-md hover:shadow-lg transition-all">
                    <Plus className="mr-2 h-4 w-4" />
                    시험 생성
                  </Button>
                </Link>
              </div>
              
              {showExamJobSection && (
                <ExamJobList
                  jobs={examJobs}
                  pdfs={pdfs}
                  loading={examJobsLoading}
                  onCancel={handleCancelExamJob}
                />
              )}

              {showGradingJobSection && (
                <GradingJobList jobs={gradingJobs} loading={gradingJobsLoading} />
              )}

              {/* Exams List */}
              {exams.length === 0 ? (
                <EmptyState
                  icon={<ClipboardList className="h-12 w-12" />}
                  title="생성된 시험이 없습니다"
                  description="PDF를 업로드하고 시험을 생성하세요"
                  action={
                    <Button onClick={() => setActiveTab("pdfs")}>
                      PDF 업로드하기
                    </Button>
                  }
                />
              ) : (
                <div className="grid gap-4 md:grid-cols-2">
                  {exams.map((exam) => {
                    // Get PDF names for this exam
                    const examPdfIds = (exam as any).pdf_ids || [(exam as any).pdf_id];
                    const examPdfs = pdfs.filter((pdf) => examPdfIds.includes(pdf.file_id));
                    
                    return (
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
                              {/* PDF badges */}
                              {examPdfs.length > 0 && (
                                <div className="mt-2 flex flex-wrap gap-1">
                                  {examPdfs.map((pdf) => (
                                    <Badge
                                      key={pdf.file_id}
                                      className="bg-gray-100 text-gray-700 text-xs"
                                    >
                                      📄 {pdf.original_filename.length > 20 
                                        ? pdf.original_filename.substring(0, 20) + '...' 
                                        : pdf.original_filename}
                                    </Badge>
                                  ))}
                                </div>
                              )}
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

                          {/* Details */}
                          <div className="mb-4 flex flex-wrap gap-3 text-sm text-gray-600">
                            <div className="flex items-center gap-1">
                              <Target className="h-4 w-4" />
                              <span>{exam.questions?.length || 0}문제</span>
                              <span>•</span>
                              <span>{exam.total_points || 0}점</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Clock className="h-4 w-4" />
                              <span>예상 시간: {exam.estimated_time || 0}분</span>
                            </div>
                            <Badge className={getDifficultyColor(exam.difficulty)}>
                              {getDifficultyText(exam.difficulty)}
                            </Badge>
                          </div>

                          {/* Action Button */}
                          <Link href={`/dashboard/subjects/${subjectId}/exams/${exam.exam_id}`}>
                            <Button className="w-full" size="sm">
                              {getButtonText(exam)}
                            </Button>
                          </Link>
                        </div>
                      </Card>
                    );
                  })}
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-6">
              {/* PDF Upload Section */}
              <div>
                <h2 className="text-2xl font-bold">PDF 자료</h2>
                <p className="mt-2 text-gray-600">
                  강의 자료를 업로드하여 시험을 생성하세요
                </p>
              </div>

              <PDFUploadZone
                onFileUpload={handleFileUpload}
                uploading={uploading}
                uploadProgress={uploadProgress}
              />

              {/* PDF List */}
              <PDFList
                subjectId={subjectId}
                initialPdfs={pdfs}
                examCounts={examCountsByPdf}
              />
            </div>
          )}
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
        />
      </AppLayout>
    </ProtectedRoute>
  );
}
