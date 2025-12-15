"use client";

export const dynamic = "force-dynamic";

import { Suspense, useCallback, useEffect, useState } from "react";
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
import { useAuth } from "@/hooks/useAuth";
import { getSubjects, deleteSubject } from "@/lib/api/subjects";
import { Subject } from "@/types/api";
import { Plus, BookOpen, FileText, ClipboardList, Trash2 } from "lucide-react";
import { useTranslations } from "next-intl";

export default function DashboardPage() {
  return (
    <Suspense fallback={<div className="p-6"><LoadingSpinner size="lg" /></div>}>
      <DashboardPageContent />
    </Suspense>
  );
}

function DashboardPageContent() {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [subjectToDelete, setSubjectToDelete] = useState<Subject | null>(null);
  const [deleting, setDeleting] = useState(false);
  const { toast } = useToast();
  const searchParams = useSearchParams();
  const selectedGroup = searchParams.get("group");
  const t = useTranslations("dashboard");
  const commonT = useTranslations("common");
  const { user, loading: authLoading } = useAuth();

  const loadData = useCallback(async () => {
    try {
      const subjectsData = await getSubjects();
      // Filter out subjects with empty subject_id
      const validSubjects = subjectsData.filter(s => s.subject_id && s.subject_id.trim() !== '');
      setSubjects(validSubjects);
    } catch (error: any) {
      toast({
        title: t("loadFailureTitle"),
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  }, [toast, t]);

  useEffect(() => {
    if (authLoading || !user) return;
    loadData();
  }, [authLoading, user, loadData]);

  const loadSubjects = async () => {
    try {
      const data = await getSubjects();
      // Filter out subjects with empty subject_id
      const validSubjects = data.filter(s => s.subject_id && s.subject_id.trim() !== '');
      setSubjects(validSubjects);
    } catch (error: any) {
      toast({
        title: t("subjectLoadFailureTitle"),
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
        title: t("deleteSuccessTitle"),
        description: t("deleteSuccessDescription", {
          name: subjectToDelete.name,
        }),
      });
      // Reload subjects
      await loadSubjects();
    } catch (error: any) {
      toast({
        title: t("deleteFailureTitle"),
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
              <h1 className="text-3xl font-bold">{t("headerTitle")}</h1>
              <p className="mt-2 text-gray-600">{t("headerSubtitle")}</p>
            </div>
            <Link href="/dashboard/subjects/new">
              <Button className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white shadow-md hover:shadow-lg transition-all">
                <Plus className="mr-2 h-4 w-4" />
                {t("addSubjectButton")}
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
              title={selectedGroup ? t("emptyTitleGroup") : t("emptyTitle")}
              description={
                selectedGroup
                  ? t("emptyDescriptionGroup")
                  : t("emptyDescription")
              }
              action={
                <Link href="/dashboard/subjects/new">
                  <Button className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white shadow-md hover:shadow-lg transition-all">
                    <Plus className="mr-2 h-4 w-4" />
                    {t("emptyAction")}
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
                    aria-label={t("deleteActionLabel")}
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
                          <span className="text-gray-600">
                            {commonT("pdfCount", { count: subject.pdf_count || 0 })}
                          </span>
                        </div>
                        <div className="flex items-center gap-1">
                          <ClipboardList className="h-4 w-4 text-gray-400" />
                          <span className="text-gray-600">
                            {commonT("examCount", { count: subject.exam_count || 0 })}
                          </span>
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
          title={t("deleteDialogTitle")}
          description={t("deleteDialogDescription", {
            name: subjectToDelete?.name ?? "",
          })}
          onConfirm={handleDeleteConfirm}
          confirmText={commonT("delete")}
          cancelText={commonT("cancel")}
          variant="destructive"
          loading={deleting}
        />
      </AppLayout>
    </ProtectedRoute>
  );
}

