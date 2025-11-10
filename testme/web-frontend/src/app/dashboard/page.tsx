"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { ProtectedRoute } from "@/components/layouts/ProtectedRoute";
import { AppLayout } from "@/components/layouts/AppLayout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { useToast } from "@/hooks/use-toast";
import { getSubjects, deleteSubject } from "@/lib/api/subjects";
import { Subject } from "@/types/api";
import { Plus, BookOpen, FileText, ClipboardList, Trash2 } from "lucide-react";

export default function DashboardPage() {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [subjectToDelete, setSubjectToDelete] = useState<Subject | null>(null);
  const [deleting, setDeleting] = useState(false);
  const { toast } = useToast();
  const searchParams = useSearchParams();
  const selectedGroup = searchParams.get("group");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const subjectsData = await getSubjects();
      // Filter out subjects with empty subject_id
      const validSubjects = subjectsData.filter(s => s.subject_id && s.subject_id.trim() !== '');
      setSubjects(validSubjects);
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

  const loadSubjects = async () => {
    try {
      const data = await getSubjects();
      // Filter out subjects with empty subject_id
      const validSubjects = data.filter(s => s.subject_id && s.subject_id.trim() !== '');
      setSubjects(validSubjects);
    } catch (error: any) {
      toast({
        title: "과목 로드 실패",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  // Filter subjects by selected group from URL
  const filteredSubjects = !selectedGroup
    ? subjects // 모든 과목
    : selectedGroup === "none"
    ? subjects.filter((s) => !s.group_id) // 그룹 없음
    : subjects.filter((s) => s.group_id === selectedGroup); // 특정 그룹

  const handleDeleteClick = (subject: Subject, e: React.MouseEvent) => {
    e.preventDefault(); // Prevent navigation
    e.stopPropagation();
    setSubjectToDelete(subject);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!subjectToDelete) return;

    setDeleting(true);
    try {
      await deleteSubject(subjectToDelete.subject_id);
      toast({
        title: "과목 삭제 완료",
        description: `${subjectToDelete.name} 과목이 삭제되었습니다.`,
      });
      // Reload subjects
      await loadSubjects();
    } catch (error: any) {
      toast({
        title: "과목 삭제 실패",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setDeleting(false);
      setDeleteDialogOpen(false);
      setSubjectToDelete(null);
    }
  };

  return (
    <ProtectedRoute>
      <AppLayout>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">대시보드</h1>
              <p className="mt-2 text-gray-600">
                과목을 선택하여 PDF를 업로드하고 시험을 생성하세요
              </p>
            </div>
            <Link href="/dashboard/subjects/new">
              <Button className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white shadow-md hover:shadow-lg transition-all">
                <Plus className="mr-2 h-4 w-4" />
                새 과목 추가
              </Button>
            </Link>
          </div>

          {/* Subjects Grid */}
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <LoadingSpinner size="lg" />
            </div>
          ) : filteredSubjects.length === 0 ? (
            <EmptyState
              icon={<BookOpen className="h-12 w-12 text-emerald-600" />}
              title={selectedGroup ? "이 그룹에 과목이 없습니다" : "과목이 없습니다"}
              description={
                selectedGroup
                  ? "다른 그룹을 선택하거나 새 과목을 추가하세요"
                  : "첫 과목을 추가하여 시작하세요"
              }
              action={
                <Link href="/dashboard/subjects/new">
                  <Button className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white shadow-md hover:shadow-lg transition-all">
                    <Plus className="mr-2 h-4 w-4" />
                    과목 추가
                  </Button>
                </Link>
              }
            />
          ) : (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {filteredSubjects.map((subject) => (
                <Card
                  key={subject.subject_id}
                  className="group relative cursor-pointer transition-all hover:shadow-lg hover:shadow-emerald-100 hover:border-emerald-300"
                >
                  {/* Delete Button */}
                  <button
                    onClick={(e) => handleDeleteClick(subject, e)}
                    className="absolute top-4 right-4 z-10 p-2 rounded-lg bg-white hover:bg-red-50 text-gray-400 hover:text-red-600 shadow-sm transition-all opacity-0 group-hover:opacity-100"
                    aria-label="과목 삭제"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>

                  <Link href={`/dashboard/subjects/${subject.subject_id}`}>
                    <div className="p-6">
                      {/* Color Bar */}
                      <div
                        className="mb-4 h-2 w-full rounded"
                        style={{
                          backgroundColor: subject.color || "#059669",
                        }}
                      />

                      {/* Subject Info */}
                      <h3 className="text-xl font-semibold transition-colors group-hover:text-emerald-600">
                        {subject.name}
                      </h3>
                      {subject.description && (
                        <p className="mt-2 text-sm text-gray-600 line-clamp-2">
                          {subject.description}
                        </p>
                      )}

                      {/* Meta Info */}
                      <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
                        {subject.semester && (
                          <span>{subject.semester}</span>
                        )}
                        {subject.year && <span>{subject.year}</span>}
                      </div>

                      {/* Stats */}
                      <div className="mt-4 flex items-center gap-4 border-t pt-4 text-sm">
                        <div className="flex items-center gap-1">
                          <FileText className="h-4 w-4 text-gray-400" />
                          <span className="text-gray-600">{subject.pdf_count || 0} PDFs</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <ClipboardList className="h-4 w-4 text-gray-400" />
                          <span className="text-gray-600">{subject.exam_count || 0} 시험</span>
                        </div>
                      </div>
                    </div>
                  </Link>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Delete Confirmation Dialog */}
        <ConfirmDialog
          open={deleteDialogOpen}
          onOpenChange={setDeleteDialogOpen}
          title="과목 삭제"
          description={`정말로 "${subjectToDelete?.name}" 과목을 삭제하시겠습니까? 이 과목에 속한 모든 PDF와 시험도 함께 삭제됩니다.`}
          onConfirm={handleDeleteConfirm}
          confirmText="삭제"
          cancelText="취소"
          variant="destructive"
          loading={deleting}
        />
      </AppLayout>
    </ProtectedRoute>
  );
}

