"use client";

import { useState } from "react";
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
import { SubjectCreateRequest } from "@/types/api";
import { ArrowLeft } from "lucide-react";
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
  const [formData, setFormData] = useState<SubjectCreateRequest>({
    name: "",
    description: "",
    semester: "",
    year: new Date().getFullYear(),
    color: COLORS[0],
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await createSubject(formData);
      toast({
        title: "과목 생성 완료",
        description: "새 과목이 성공적으로 생성되었습니다.",
      });
      router.push("/dashboard");
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

              {/* Semester and Year */}
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label htmlFor="semester">학기</Label>
                  <Input
                    id="semester"
                    value={formData.semester}
                    onChange={(e) =>
                      setFormData({ ...formData, semester: e.target.value })
                    }
                    placeholder="예: 2025-1"
                    maxLength={20}
                    disabled={loading}
                  />
                </div>
                <div>
                  <Label htmlFor="year">년도</Label>
                  <Input
                    id="year"
                    type="number"
                    value={formData.year || ""}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        year: parseInt(e.target.value) || undefined,
                      })
                    }
                    placeholder="예: 2025"
                    min={2000}
                    max={2100}
                    disabled={loading}
                  />
                </div>
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

