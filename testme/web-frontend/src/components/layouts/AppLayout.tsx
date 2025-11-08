"use client";

import { ReactNode, useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { signOut } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Menu } from "lucide-react";
import { groupsApi } from "@/lib/api/groups";
import { Group } from "@/types/api";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { useToast } from "@/hooks/use-toast";
import { Sidebar } from "./Sidebar";
import { GroupDialog } from "./GroupDialog";

interface AppLayoutProps {
  children: ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [groups, setGroups] = useState<Group[]>([]);
  const [loadingGroups, setLoadingGroups] = useState(true);
  const [showGroupForm, setShowGroupForm] = useState(false);
  const [groupFormData, setGroupFormData] = useState({ name: "", description: "" });
  const [creatingGroup, setCreatingGroup] = useState(false);
  const [editingGroup, setEditingGroup] = useState<Group | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [groupToDelete, setGroupToDelete] = useState<Group | null>(null);
  const [deletingGroup, setDeletingGroup] = useState(false);
  const searchParams = useSearchParams();
  const router = useRouter();
  const { user } = useAuth();
  const { toast } = useToast();

  const selectedGroup = searchParams.get("group");

  useEffect(() => {
    loadGroups();

    // Listen for group updates
    const handleGroupsUpdated = () => {
      loadGroups();
    };
    window.addEventListener("groupsUpdated", handleGroupsUpdated);
    
    return () => {
      window.removeEventListener("groupsUpdated", handleGroupsUpdated);
    };
  }, []);

  const loadGroups = async () => {
    try {
      const data = await groupsApi.getGroups();
      setGroups(data);
    } catch (error) {
      console.error("Failed to load groups:", error);
    } finally {
      setLoadingGroups(false);
    }
  };

  const handleGroupClick = (groupId: string | null) => {
    if (groupId === null) {
      router.push("/dashboard");
    } else {
      router.push(`/dashboard?group=${groupId}`);
    }
    setSidebarOpen(false);
  };

  const handleNewGroupClick = () => {
    setEditingGroup(null);
    setGroupFormData({ name: "", description: "" });
    setShowGroupForm(true);
  };

  const handleCreateGroup = async () => {
    if (!groupFormData.name.trim()) {
      toast({
        title: "입력 오류",
        description: "그룹 이름을 입력해주세요",
        variant: "destructive",
      });
      return;
    }

    setCreatingGroup(true);
    try {
      if (editingGroup) {
        // Update existing group
        await groupsApi.updateGroup(editingGroup.group_id, {
          name: groupFormData.name.trim(),
          description: groupFormData.description.trim() || undefined,
        });
        toast({
          title: "그룹 수정 완료",
          description: `"${groupFormData.name}" 그룹이 수정되었습니다.`,
        });
      } else {
        // Create new group
        await groupsApi.createGroup({
          name: groupFormData.name.trim(),
          description: groupFormData.description.trim() || undefined,
        });
        toast({
          title: "그룹 생성 완료",
          description: `"${groupFormData.name}" 그룹이 생성되었습니다.`,
        });
      }
      setShowGroupForm(false);
      setGroupFormData({ name: "", description: "" });
      setEditingGroup(null);
      await loadGroups();
    } catch (error: any) {
      toast({
        title: editingGroup ? "그룹 수정 실패" : "그룹 생성 실패",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setCreatingGroup(false);
    }
  };

  const handleEditClick = (group: Group, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingGroup(group);
    setGroupFormData({
      name: group.name,
      description: group.description || "",
    });
    setShowGroupForm(true);
  };

  const handleDeleteClick = (group: Group, e: React.MouseEvent) => {
    e.stopPropagation();
    setGroupToDelete(group);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!groupToDelete) return;

    setDeletingGroup(true);
    try {
      await groupsApi.deleteGroup(groupToDelete.group_id);
      toast({
        title: "그룹 삭제 완료",
        description: `"${groupToDelete.name}" 그룹이 삭제되었습니다.`,
      });
      await loadGroups();
      // If deleted group was selected, redirect to all subjects
      if (selectedGroup === groupToDelete.group_id) {
        router.push("/dashboard");
      }
    } catch (error: any) {
      toast({
        title: "그룹 삭제 실패",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setDeletingGroup(false);
      setDeleteDialogOpen(false);
      setGroupToDelete(null);
    }
  };

  const handleSignOut = async () => {
    await signOut();
    window.location.href = "/login";
  };

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      {/* Sidebar */}
      <Sidebar
        sidebarOpen={sidebarOpen}
        onSidebarClose={() => setSidebarOpen(false)}
        groups={groups}
        loadingGroups={loadingGroups}
        selectedGroup={selectedGroup}
        onGroupClick={handleGroupClick}
        onGroupEdit={handleEditClick}
        onGroupDelete={handleDeleteClick}
        onNewGroupClick={handleNewGroupClick}
        user={user}
        onSignOut={handleSignOut}
      />

      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Header */}
        <header className="flex h-16 items-center justify-between border-b bg-white px-4 lg:px-6">
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-5 w-5" />
          </Button>
          <div className="hidden lg:block"></div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto p-4 lg:p-6">{children}</main>
      </div>

      {/* Group Create/Edit Dialog */}
      <GroupDialog
        open={showGroupForm}
        onOpenChange={(open) => {
          setShowGroupForm(open);
          if (!open) {
            setGroupFormData({ name: "", description: "" });
            setEditingGroup(null);
          }
        }}
        editingGroup={editingGroup}
        formData={groupFormData}
        onFormDataChange={setGroupFormData}
        onSubmit={handleCreateGroup}
        loading={creatingGroup}
      />

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
        loading={deletingGroup}
      />
    </div>
  );
}
