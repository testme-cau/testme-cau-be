"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { groupsApi } from "@/lib/api/groups";
import type { Group } from "@/types/api";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { EmptyState } from "@/components/ui/empty-state";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { toast } from "@/hooks/use-toast";
import { Plus, Folder, Edit2, Trash2 } from "lucide-react";

export default function GroupsPage() {
  const router = useRouter();
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [groupToDelete, setGroupToDelete] = useState<Group | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    loadGroups();
  }, []);

  const loadGroups = async () => {
    try {
      setLoading(true);
      const data = await groupsApi.getGroups();
      setGroups(data);
    } catch (error: any) {
      console.error("Failed to load groups:", error);
      toast({
        title: "그룹 로드 실패",
        description: error.response?.data?.error || "An error occurred",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClick = (group: Group, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setGroupToDelete(group);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!groupToDelete) return;

    try {
      setDeleting(true);
      await groupsApi.deleteGroup(groupToDelete.group_id);
      
      toast({
        title: "그룹 삭제 완료",
        description: `"${groupToDelete.name}" 그룹이 삭제되었습니다.`,
      });

      // Remove from list
      setGroups(groups.filter((g) => g.group_id !== groupToDelete.group_id));
      setDeleteDialogOpen(false);
      setGroupToDelete(null);
    } catch (error: any) {
      console.error("Failed to delete group:", error);
      toast({
        title: "삭제 실패",
        description: error.response?.data?.error || "An error occurred",
        variant: "destructive",
      });
    } finally {
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">그룹 관리</h1>
          <p className="text-gray-600 mt-2">
            과목을 그룹별로 정리하고 관리하세요
          </p>
        </div>
        <Button
          onClick={() => router.push("/dashboard/groups/new")}
          className="bg-emerald-600 hover:bg-emerald-700"
        >
          <Plus className="h-4 w-4 mr-2" />
          새 그룹
        </Button>
      </div>

      {/* Groups List */}
      {groups.length === 0 ? (
        <EmptyState
          icon={<Folder className="h-12 w-12 text-emerald-600" />}
          title="그룹이 없습니다"
          description="첫 번째 그룹을 만들어 과목을 정리해보세요"
          action={
            <Button
              onClick={() => router.push("/dashboard/groups/new")}
              className="bg-emerald-600 hover:bg-emerald-700"
            >
              <Plus className="h-4 w-4 mr-2" />
              그룹 만들기
            </Button>
          }
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {groups.map((group) => (
            <Card
              key={group.group_id}
              className="group relative cursor-pointer transition-all hover:shadow-lg hover:shadow-emerald-100 hover:border-emerald-300"
              onClick={() => router.push(`/dashboard/groups/${group.group_id}`)}
            >
              {/* Delete Button */}
              <button
                onClick={(e) => handleDeleteClick(group, e)}
                className="absolute top-4 right-4 z-10 p-2 rounded-lg bg-white hover:bg-red-50 text-gray-400 hover:text-red-600 shadow-sm transition-all opacity-0 group-hover:opacity-100"
                aria-label="그룹 삭제"
              >
                <Trash2 className="h-4 w-4" />
              </button>

              <div className="p-6">
                {/* Group Icon/Color */}
                <div
                  className="w-12 h-12 rounded-lg flex items-center justify-center mb-4"
                  style={{
                    backgroundColor: group.color || "#10B981",
                    opacity: 0.1,
                  }}
                >
                  <Folder
                    className="h-6 w-6"
                    style={{ color: group.color || "#10B981" }}
                  />
                </div>

                {/* Group Info */}
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {group.name}
                </h3>
                {group.description && (
                  <p className="text-gray-600 text-sm line-clamp-2">
                    {group.description}
                  </p>
                )}

                {/* Metadata */}
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <p className="text-xs text-gray-500">
                    생성일: {new Date(group.created_at).toLocaleDateString("ko-KR")}
                  </p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        title="그룹 삭제"
        description={`정말로 "${groupToDelete?.name}" 그룹을 삭제하시겠습니까? 이 그룹에 속한 과목들은 그룹 없음 상태로 변경됩니다.`}
        onConfirm={handleDeleteConfirm}
        confirmText="삭제"
        cancelText="취소"
        variant="destructive"
        loading={deleting}
      />
    </div>
  );
}

