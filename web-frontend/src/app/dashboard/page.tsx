"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ProtectedRoute } from "@/components/layouts/ProtectedRoute";
import { AppLayout } from "@/components/layouts/AppLayout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { useToast } from "@/hooks/use-toast";
import { getSubjects } from "@/lib/api/subjects";
import { Subject } from "@/types/api";
import { Plus, BookOpen, FileText, ClipboardList } from "lucide-react";

export default function DashboardPage() {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    loadSubjects();
  }, []);

  const loadSubjects = async () => {
    try {
      const data = await getSubjects();
      setSubjects(data);
    } catch (error: any) {
      toast({
        title: "과목 로드 실패",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
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
          ) : subjects.length === 0 ? (
            <EmptyState
              icon={<BookOpen className="h-12 w-12 text-emerald-600" />}
              title="과목이 없습니다"
              description="첫 과목을 추가하여 시작하세요"
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
              {subjects.map((subject) => (
                <Link
                  key={subject.subject_id}
                  href={`/dashboard/subjects/${subject.subject_id}`}
                >
                  <Card className="group cursor-pointer transition-all hover:shadow-lg hover:shadow-emerald-100 hover:border-emerald-300">
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

                      {/* Stats (placeholder for now) */}
                      <div className="mt-4 flex items-center gap-4 border-t pt-4 text-sm">
                        <div className="flex items-center gap-1">
                          <FileText className="h-4 w-4 text-gray-400" />
                          <span className="text-gray-600">0 PDFs</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <ClipboardList className="h-4 w-4 text-gray-400" />
                          <span className="text-gray-600">0 시험</span>
                        </div>
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

