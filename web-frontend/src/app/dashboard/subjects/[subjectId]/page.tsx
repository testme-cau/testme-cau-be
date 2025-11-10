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
  const [uploadProgress, setUploadProgress] = useState<{ current: number; total: number } | undefined>();

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
            uploadProgress={uploadProgress}
          />

          {/* PDF List */}
          <PDFList
            subjectId={subjectId}
            initialPdfs={pdfs}
          />
        </div>
      </AppLayout>
    </ProtectedRoute>
  );
}
