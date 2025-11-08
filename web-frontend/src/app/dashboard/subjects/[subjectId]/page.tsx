"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ProtectedRoute } from "@/components/layouts/ProtectedRoute";
import { AppLayout } from "@/components/layouts/AppLayout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { useToast } from "@/hooks/use-toast";
import { getSubject, deleteSubject, updateSubject } from "@/lib/api/subjects";
import { getPDFs, uploadPDF, deletePDF, downloadPDF } from "@/lib/api/pdfs";
import { groupsApi } from "@/lib/api/groups";
import { Subject, PDF, Group } from "@/types/api";
import {
  ArrowLeft,
  Upload,
  FileText,
  Download,
  Trash2,
  Settings,
  ClipboardList,
  Folder,
} from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

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
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [pdfToDelete, setPdfToDelete] = useState<PDF | null>(null);
  const [updatingGroup, setUpdatingGroup] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

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
      // 에러 발생 시에도 빈 배열로 설정
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

  const validateAndUploadFile = async (file: File) => {
    if (file.type !== "application/pdf") {
      toast({
        title: "파일 형식 오류",
        description: "PDF 파일만 업로드 가능합니다.",
        variant: "destructive",
      });
      return;
    }

    if (file.size > 16 * 1024 * 1024) {
      toast({
        title: "파일 크기 초과",
        description: "파일 크기는 16MB를 초과할 수 없습니다.",
        variant: "destructive",
      });
      return;
    }

    setUploading(true);
    try {
      await uploadPDF(subjectId, file);
      toast({
        title: "업로드 완료",
        description: "PDF가 성공적으로 업로드되었습니다.",
      });
      loadData();
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

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    await validateAndUploadFile(file);
    e.target.value = "";
  };

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      await validateAndUploadFile(files[0]);
    }
  };

  const handleDeletePDF = async () => {
    if (!pdfToDelete) return;

    try {
      await deletePDF(subjectId, pdfToDelete.file_id);
      toast({
        title: "삭제 완료",
        description: "PDF가 삭제되었습니다.",
      });
      setPdfs((pdfs || []).filter((p) => p.file_id !== pdfToDelete.file_id));
    } catch (error: any) {
      toast({
        title: "삭제 실패",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setDeleteDialogOpen(false);
      setPdfToDelete(null);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
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
          <div>
            <Link href="/dashboard">
              <Button variant="ghost" className="mb-4">
                <ArrowLeft className="mr-2 h-4 w-4" />
                대시보드로 돌아가기
              </Button>
            </Link>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <div
                    className="h-4 w-4 rounded"
                    style={{ backgroundColor: subject.color || "#6B7280" }}
                  />
                  <h1 className="text-3xl font-bold">{subject.name}</h1>
                </div>
                {subject.description && (
                  <p className="mt-2 text-gray-600">{subject.description}</p>
                )}
                
                {/* Group Selection */}
                <div className="mt-4 flex items-center gap-3">
                  <Folder className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium text-gray-700">그룹:</span>
                  <Select
                    value={subject.group_id || "none"}
                    onValueChange={handleGroupChange}
                    disabled={updatingGroup}
                  >
                    <SelectTrigger className="w-[200px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">그룹 없음</SelectItem>
                      {groups.map((group) => (
                        <SelectItem key={group.group_id} value={group.group_id}>
                          {group.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {updatingGroup && (
                    <LoadingSpinner size="sm" />
                  )}
                </div>
              </div>
              <div className="flex gap-2">
                <Link href={`/dashboard/subjects/${subjectId}/exams`}>
                  <Button variant="outline">
                    <ClipboardList className="mr-2 h-4 w-4" />
                    시험 목록
                  </Button>
                </Link>
              </div>
            </div>
          </div>

          {/* Upload Section */}
          <Card className="p-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold">PDF 자료</h2>
                  <p className="mt-1 text-sm text-gray-600">
                    강의 자료를 업로드하여 시험을 생성하세요
                  </p>
                </div>
              </div>

              {/* Drag and Drop Area */}
              <div
                onDragEnter={handleDragEnter}
                onDragLeave={handleDragLeave}
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                onClick={() => document.getElementById('pdf-upload')?.click()}
                className={`
                  relative border-2 border-dashed rounded-lg p-12 
                  text-center cursor-pointer transition-colors
                  ${isDragging 
                    ? 'border-emerald-500 bg-emerald-50' 
                    : 'border-gray-300 hover:border-gray-400 bg-gray-50'
                  }
                  ${uploading ? 'opacity-50 cursor-not-allowed' : ''}
                `}
              >
                <input
                  type="file"
                  id="pdf-upload"
                  accept=".pdf"
                  onChange={handleFileUpload}
                  className="hidden"
                  disabled={uploading}
                />
                
                <div className="flex flex-col items-center justify-center gap-4">
                  {uploading ? (
                    <>
                      <LoadingSpinner size="lg" />
                      <p className="text-lg font-medium text-gray-700">
                        업로드 중...
                      </p>
                    </>
                  ) : (
                    <>
                      <Upload className={`h-12 w-12 ${isDragging ? 'text-emerald-500' : 'text-gray-400'}`} />
                      <div>
                        <p className="text-lg font-medium text-gray-700">
                          {isDragging ? 'PDF 파일을 여기에 놓으세요' : 'PDF 파일을 드래그하거나 클릭하여 업로드'}
                        </p>
                        <p className="mt-1 text-sm text-gray-500">
                          최대 16MB까지 업로드 가능
                        </p>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>
          </Card>

          {/* PDF List */}
          {!pdfs || pdfs.length === 0 ? (
            <EmptyState
              icon={<FileText className="h-12 w-12" />}
              title="업로드된 PDF가 없습니다"
              description="PDF 자료를 업로드하여 시작하세요"
            />
          ) : (
            <div className="space-y-3">
              {pdfs.map((pdf) => (
                <Card key={pdf.file_id} className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <FileText className="h-8 w-8 text-gray-400" />
                      <div>
                        <h3 className="font-medium">{pdf.original_filename}</h3>
                        <p className="text-sm text-gray-500">
                          {formatFileSize(pdf.size)} •{" "}
                          {new Date(pdf.uploaded_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Link
                        href={`/dashboard/subjects/${subjectId}/pdfs/${pdf.file_id}/generate-exam`}
                      >
                        <Button size="sm">
                          <ClipboardList className="mr-2 h-4 w-4" />
                          시험 생성
                        </Button>
                      </Link>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => downloadPDF(subjectId, pdf.file_id)}
                      >
                        <Download className="h-4 w-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          setPdfToDelete(pdf);
                          setDeleteDialogOpen(true);
                        }}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Delete Confirm Dialog */}
        <ConfirmDialog
          open={deleteDialogOpen}
          onOpenChange={setDeleteDialogOpen}
          onConfirm={handleDeletePDF}
          title="PDF 삭제"
          description="이 PDF를 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다."
          confirmText="삭제"
          variant="destructive"
        />
      </AppLayout>
    </ProtectedRoute>
  );
}

