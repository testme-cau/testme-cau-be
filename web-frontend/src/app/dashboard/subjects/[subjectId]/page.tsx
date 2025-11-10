"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ProtectedRoute } from "@/components/layouts/ProtectedRoute";
import { AppLayout } from "@/components/layouts/AppLayout";
import { Button } from "@/components/ui/button";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { useToast } from "@/hooks/use-toast";
import { getSubject, updateSubject } from "@/lib/api/subjects";
import { getPDFs, uploadPDF } from "@/lib/api/pdfs";
import { generateExam } from "@/lib/api/exams";
import { groupsApi } from "@/lib/api/groups";
import { Subject, PDF, Group } from "@/types/api";
import { SubjectHeader } from "@/components/subjects/SubjectHeader";
import { SubjectGroupSelector } from "@/components/subjects/SubjectGroupSelector";
import { PDFUploadZone } from "@/components/subjects/PDFUploadZone";
import { PDFList } from "@/components/subjects/PDFList";
import { ClipboardList, CheckSquare, X } from "lucide-react";

export default function SubjectDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const subjectId = params.subjectId as string;

  const [subject, setSubject] = useState<Subject | null>(null);
  const [pdfs, setPdfs] = useState<PDF[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [updatingGroup, setUpdatingGroup] = useState(false);
  
  // Multi-select state
  const [selectionMode, setSelectionMode] = useState(false);
  const [selectedPdfIds, setSelectedPdfIds] = useState<string[]>([]);
  const [generatingExam, setGeneratingExam] = useState(false);

  useEffect(() => {
    loadData();
  }, [subjectId]);

  const loadData = async () => {
    try {
      const [subjectData, pdfsData, groupsData] = await Promise.all([
        getSubject(subjectId),
        getPDFs(subjectId),
        groupsApi.getGroups(),
      ]);
      setSubject(subjectData);
      setPdfs(pdfsData || []);
      setGroups(groupsData || []);
    } catch (error: any) {
      toast({
        title: "데이터 로드 실패",
        description: error.message,
        variant: "destructive",
      });
      setPdfs([]);
      setGroups([]);
    } finally {
      setLoading(false);
    }
  };

  const handleGroupChange = async (groupId: string) => {
    if (!subject) return;
    
    setUpdatingGroup(true);
    try {
      await updateSubject(subjectId, {
        name: subject.name,
        description: subject.description,
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

  const handleFileUpload = async (file: File) => {
    setUploading(true);
    try {
      await uploadPDF(subjectId, file);
      toast({
        title: "업로드 완료",
        description: "PDF가 성공적으로 업로드되었습니다.",
      });
      await loadData();
    } catch (error: any) {
      toast({
        title: "업로드 실패",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setUploading(false);
    }
  };

  const handleToggleSelectionMode = () => {
    setSelectionMode(!selectionMode);
    setSelectedPdfIds([]);
  };

  const handlePdfSelect = (pdfId: string, selected: boolean) => {
    if (selected) {
      setSelectedPdfIds((prev) => [...prev, pdfId]);
    } else {
      setSelectedPdfIds((prev) => prev.filter((id) => id !== pdfId));
    }
  };

  const handleSelectAll = () => {
    if (selectedPdfIds.length === pdfs.length) {
      setSelectedPdfIds([]);
    } else {
      setSelectedPdfIds(pdfs.map((pdf) => pdf.file_id));
    }
  };

  const handleGenerateExamFromSelected = async () => {
    if (selectedPdfIds.length === 0) {
      toast({
        title: "PDF 선택 필요",
        description: "시험을 생성하려면 하나 이상의 PDF를 선택해야 합니다.",
        variant: "destructive",
      });
      return;
    }

    setGeneratingExam(true);
    try {
      const exam = await generateExam(subjectId, {
        pdf_ids: selectedPdfIds,
        num_questions: 10,
        difficulty: "medium",
        ai_provider: "gpt",
      });
      toast({
        title: "시험 생성 완료",
        description: `${selectedPdfIds.length}개 PDF로부터 시험이 생성되었습니다.`,
      });
      router.push(`/dashboard/subjects/${subjectId}/exams/${exam.exam_id}`);
    } catch (error: any) {
      toast({
        title: "시험 생성 실패",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setGeneratingExam(false);
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
          <SubjectHeader
            subject={subject}
            subjectId={subjectId}
          />

          {/* Group Selector */}
          <SubjectGroupSelector
            currentGroupId={subject.group_id}
            groups={groups}
            loading={updatingGroup}
            onChange={handleGroupChange}
          />

          {/* Upload Section */}
          <PDFUploadZone
            onFileUpload={handleFileUpload}
            uploading={uploading}
          />

          {/* Multi-select Controls */}
          {pdfs.length > 0 && (
            <div className="flex items-center justify-between rounded-lg border bg-white p-4">
              <div className="flex items-center gap-3">
                <Button
                  variant={selectionMode ? "default" : "outline"}
                  onClick={handleToggleSelectionMode}
                  size="sm"
                >
                  {selectionMode ? (
                    <>
                      <X className="mr-2 h-4 w-4" />
                      선택 취소
                    </>
                  ) : (
                    <>
                      <CheckSquare className="mr-2 h-4 w-4" />
                      다중 선택
                    </>
                  )}
                </Button>
                
                {selectionMode && (
                  <>
                    <Button
                      variant="outline"
                      onClick={handleSelectAll}
                      size="sm"
                    >
                      {selectedPdfIds.length === pdfs.length ? "전체 해제" : "전체 선택"}
                    </Button>
                    
                    {selectedPdfIds.length > 0 && (
                      <span className="text-sm text-gray-600">
                        {selectedPdfIds.length}개 선택됨
                      </span>
                    )}
                  </>
                )}
              </div>

              {selectionMode && selectedPdfIds.length > 0 && (
                <Button
                  onClick={handleGenerateExamFromSelected}
                  disabled={generatingExam}
                >
                  <ClipboardList className="mr-2 h-4 w-4" />
                  선택한 PDF로 시험 생성
                </Button>
              )}
            </div>
          )}

          {/* PDF List */}
          <PDFList
            subjectId={subjectId}
            initialPdfs={pdfs}
            selectionMode={selectionMode}
            selectedPdfIds={selectedPdfIds}
            onPdfSelect={handlePdfSelect}
          />
        </div>
      </AppLayout>
    </ProtectedRoute>
  );
}
