"use client";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Group } from "@/types/api";

interface GroupDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  editingGroup: Group | null;
  formData: {
    name: string;
    description: string;
  };
  onFormDataChange: (data: { name: string; description: string }) => void;
  onSubmit: () => void;
  loading: boolean;
}

export function GroupDialog({
  open,
  onOpenChange,
  editingGroup,
  formData,
  onFormDataChange,
  onSubmit,
  loading,
}: GroupDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="text-xl font-bold">
            {editingGroup ? "그룹 수정" : "새 그룹 만들기"}
          </DialogTitle>
          <DialogDescription>
            {editingGroup
              ? "그룹 정보를 수정하세요. 변경사항은 즉시 반영됩니다."
              : "새로운 그룹을 만들어 과목을 체계적으로 관리하세요."}
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="group-name" className="text-sm font-medium">
              그룹 이름 <span className="text-red-500">*</span>
            </Label>
            <Input
              id="group-name"
              placeholder="예: 2025-1학기, 전공과목 등"
              value={formData.name}
              onChange={(e) =>
                onFormDataChange({ ...formData, name: e.target.value })
              }
              disabled={loading}
              autoFocus
              className="w-full"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="group-description" className="text-sm font-medium">
              설명 <span className="text-gray-400 text-xs">(선택사항)</span>
            </Label>
            <Textarea
              id="group-description"
              placeholder="그룹에 대한 간단한 설명을 입력하세요"
              value={formData.description}
              onChange={(e) =>
                onFormDataChange({
                  ...formData,
                  description: e.target.value,
                })
              }
              disabled={loading}
              rows={3}
              className="w-full resize-none"
            />
          </div>
        </div>
        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={loading}
          >
            취소
          </Button>
          <Button
            type="button"
            onClick={onSubmit}
            disabled={loading || !formData.name.trim()}
            className="bg-emerald-600 hover:bg-emerald-700"
          >
            {loading ? (
              <>
                <span className="mr-2">⏳</span>
                {editingGroup ? "수정 중..." : "생성 중..."}
              </>
            ) : (
              editingGroup ? "수정 완료" : "생성"
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

