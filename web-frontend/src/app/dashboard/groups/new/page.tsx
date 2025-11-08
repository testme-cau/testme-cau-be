"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { groupsApi } from "@/lib/api/groups";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { toast } from "@/hooks/use-toast";
import { ArrowLeft, Folder } from "lucide-react";

const PRESET_COLORS = [
  { name: "에메랄드", value: "#10B981" },
  { name: "블루", value: "#3B82F6" },
  { name: "퍼플", value: "#8B5CF6" },
  { name: "핑크", value: "#EC4899" },
  { name: "오렌지", value: "#F59E0B" },
  { name: "레드", value: "#EF4444" },
  { name: "그린", value: "#22C55E" },
  { name: "인디고", value: "#6366F1" },
];

export default function NewGroupPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    color: "#10B981",
    icon: "folder",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      toast({
        title: "입력 오류",
        description: "그룹 이름을 입력해주세요",
        variant: "destructive",
      });
      return;
    }

    try {
      setLoading(true);
      await groupsApi.createGroup({
        name: formData.name.trim(),
        description: formData.description.trim() || undefined,
        color: formData.color,
        icon: formData.icon,
      });

      toast({
        title: "그룹 생성 완료",
        description: `"${formData.name}" 그룹이 생성되었습니다`,
      });

      router.push("/dashboard/groups");
    } catch (error: any) {
      console.error("Failed to create group:", error);
      toast({
        title: "그룹 생성 실패",
        description: error.response?.data?.error || "An error occurred",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button
          variant="outline"
          size="icon"
          onClick={() => router.back()}
          disabled={loading}
        >
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">새 그룹 만들기</h1>
          <p className="text-gray-600 mt-1">
            과목을 그룹별로 정리하세요
          </p>
        </div>
      </div>

      {/* Form */}
      <Card className="p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Group Name */}
          <div className="space-y-2">
            <Label htmlFor="name">
              그룹 이름 <span className="text-red-500">*</span>
            </Label>
            <Input
              id="name"
              type="text"
              placeholder="예: 2025-1학기, 중요한 과목"
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              disabled={loading}
              required
              maxLength={100}
            />
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">설명 (선택)</Label>
            <Textarea
              id="description"
              placeholder="그룹에 대한 설명을 입력하세요"
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              disabled={loading}
              rows={3}
              maxLength={500}
            />
          </div>

          {/* Color Picker */}
          <div className="space-y-2">
            <Label>색상</Label>
            <div className="grid grid-cols-4 gap-3">
              {PRESET_COLORS.map((color) => (
                <button
                  key={color.value}
                  type="button"
                  onClick={() => setFormData({ ...formData, color: color.value })}
                  className={`relative p-4 rounded-lg border-2 transition-all ${
                    formData.color === color.value
                      ? "border-gray-900 ring-2 ring-gray-900 ring-offset-2"
                      : "border-gray-200 hover:border-gray-400"
                  }`}
                  disabled={loading}
                >
                  <div
                    className="w-full h-8 rounded"
                    style={{ backgroundColor: color.value }}
                  />
                  <p className="text-xs text-center mt-2 text-gray-600">
                    {color.name}
                  </p>
                  {formData.color === color.value && (
                    <div className="absolute top-2 right-2 w-5 h-5 bg-gray-900 rounded-full flex items-center justify-center">
                      <svg
                        className="w-3 h-3 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={3}
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Preview */}
          <div className="space-y-2">
            <Label>미리보기</Label>
            <div className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <div
                  className="w-12 h-12 rounded-lg flex items-center justify-center"
                  style={{
                    backgroundColor: formData.color,
                    opacity: 0.15,
                  }}
                >
                  <Folder
                    className="h-6 w-6"
                    style={{ color: formData.color }}
                  />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">
                    {formData.name || "그룹 이름"}
                  </h3>
                  {formData.description && (
                    <p className="text-sm text-gray-600 mt-1">
                      {formData.description}
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.back()}
              disabled={loading}
              className="flex-1"
            >
              취소
            </Button>
            <Button
              type="submit"
              disabled={loading || !formData.name.trim()}
              className="flex-1 bg-emerald-600 hover:bg-emerald-700"
            >
              {loading ? "생성 중..." : "그룹 만들기"}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}

