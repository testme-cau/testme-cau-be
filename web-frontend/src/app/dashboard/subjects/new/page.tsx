"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ProtectedRoute } from "@/components/layouts/ProtectedRoute";
import { AppLayout } from "@/components/layouts/AppLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { createSubject } from "@/lib/api/subjects";
import { groupsApi } from "@/lib/api/groups";
import { SubjectCreateRequest, Group } from "@/types/api";
import { ArrowLeft, Plus } from "lucide-react";
import Link from "next/link";

const COLORS = [
  "#EF4444", // Red
  "#F59E0B", // Orange
  "#10B981", // Green
  "#3B82F6", // Blue
  "#8B5CF6", // Purple
  "#EC4899", // Pink
  "#6B7280", // Gray
];

export default function NewSubjectPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [groups, setGroups] = useState<Group[]>([]);
  const [loadingGroups, setLoadingGroups] = useState(true);
  const [formData, setFormData] = useState<SubjectCreateRequest>({
    name: "",
    description: "",
    group_id: undefined,
    color: COLORS[0],
  });

  useEffect(() => {
    loadGroups();
  }, []);

  const loadGroups = async () => {
    try {
      setLoadingGroups(true);
      const data = await groupsApi.getGroups();
      setGroups(data);
    } catch (error: any) {
      console.error("Failed to load groups:", error);
      toast({
        title: "그룹 로드 실패",
        description: "그룹을 불러올 수 없습니다",
        variant: "destructive",
      });
    } finally {
      setLoadingGroups(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Remove group_id if it's "__create_new__"
      const submitData = { ...formData };
      if (submitData.group_id === "__create_new__") {
        router.push("/dashboard/groups/new");
        return;
      }

      await createSubject(submitData);
      toast({
        title: "과목 생성 완료",
        description: "새 과목이 성공적으로 생성되었습니다.",
      });
      // Force page reload to show new subject
      window.location.href = "/dashboard";
    } catch (error: any) {
      toast({
        title: "과목 생성 실패",
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
        <div className="mx-auto max-w-2xl space-y-6">
          {/* Header */}
          <div>
            <Link href="/dashboard">
              <Button variant="ghost" className="mb-4">
                <ArrowLeft className="mr-2 h-4 w-4" />
                대시보드로 돌아가기
              </Button>
            </Link>
            <h1 className="text-3xl font-bold">새 과목 추가</h1>
            <p className="mt-2 text-gray-600">
              과목 정보를 입력하여 새로운 과목을 생성하세요
            </p>
          </div>

          {/* Form */}
          <Card>
            <form onSubmit={handleSubmit} className="space-y-6 p-6">
              {/* Name */}
              <div>
                <Label htmlFor="name">
                  과목명 <span className="text-red-500">*</span>
                </Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  placeholder="예: 데이터베이스"
                  required
                  maxLength={100}
                  disabled={loading}
                />
              </div>

              {/* Description */}
              <div>
                <Label htmlFor="description">설명</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                  placeholder="과목에 대한 간단한 설명을 입력하세요"
                  maxLength={500}
                  disabled={loading}
                  rows={4}
                />
              </div>

              {/* Group Selection */}
              <div>
                <Label htmlFor="group">그룹 (선택)</Label>
                <select
                  id="group"
                  value={formData.group_id || ""}
                  onChange={(e) =>
                    setFormData({ ...formData, group_id: e.target.value || undefined })
                  }
                  disabled={loading || loadingGroups}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="">그룹 없음</option>
                  {groups.map((group) => (
                    <option key={group.group_id} value={group.group_id}>
                      {group.name}
                    </option>
                  ))}
                  <option value="__create_new__">+ 새 그룹 생성</option>
                </select>
                {loadingGroups && (
                  <p className="text-sm text-gray-500 mt-1">그룹 로딩 중...</p>
                )}
              </div>

              {/* Color */}
              <div>
                <Label>색상</Label>
                <div className="mt-2 flex gap-2">
                  {COLORS.map((color) => (
                    <button
                      key={color}
                      type="button"
                      onClick={() => setFormData({ ...formData, color })}
                      className={`h-10 w-10 rounded-full transition-transform hover:scale-110 ${
                        formData.color === color
                          ? "ring-2 ring-offset-2 ring-primary"
                          : ""
                      }`}
                      style={{ backgroundColor: color }}
                      disabled={loading}
                    />
                  ))}
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-3">
                <Button type="submit" disabled={loading}>
                  {loading ? "생성 중..." : "과목 생성"}
                </Button>
                <Link href="/dashboard">
                  <Button type="button" variant="outline" disabled={loading}>
                    취소
                  </Button>
                </Link>
              </div>
            </form>
          </Card>
        </div>
      </AppLayout>
    </ProtectedRoute>
  );
}

