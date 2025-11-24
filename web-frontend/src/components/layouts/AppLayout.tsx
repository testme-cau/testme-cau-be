"use client";

import { ReactNode, useState, useEffect, useCallback } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { signOut } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Menu } from "lucide-react";
import { groupsApi } from "@/lib/api/groups";
import { getSubjects } from "@/lib/api/subjects";
import { Group, Subject } from "@/types/api";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { useToast } from "@/hooks/use-toast";
import { Sidebar } from "./Sidebar";
import { GroupDialog } from "./GroupDialog";
import { LanguageSelector } from "./LanguageSelector";

interface AppLayoutProps {
  children: ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [groups, setGroups] = useState<Group[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loadingGroups, setLoadingGroups] = useState(true);
  const [loadingSubjects, setLoadingSubjects] = useState(true);
  const [showGroupForm, setShowGroupForm] = useState(false);
  const [groupFormData, setGroupFormData] = useState({ name: "", description: "" });
  const [creatingGroup, setCreatingGroup] = useState(false);
  const [editingGroup, setEditingGroup] = useState<Group | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [groupToDelete, setGroupToDelete] = useState<Group | null>(null);
  const [deletingGroup, setDeletingGroup] = useState(false);
  const searchParams = useSearchParams();
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const { toast } = useToast();

  const selectedGroup = searchParams.get("group");

  const loadGroups = useCallback(async () => {
    try {
      const data = await groupsApi.getGroups();
      setGroups(data);
    } catch (error) {
      console.error("Failed to load groups:", error);
    } finally {
      setLoadingGroups(false);
    }
  }, []);

  const loadSubjects = useCallback(async () => {
    try {
      const data = await getSubjects();
      const validSubjects = data.filter(s => s.subject_id && s.subject_id.trim() !== '');
      setSubjects(validSubjects);
    } catch (error) {
      console.error("Failed to load subjects:", error);
    } finally {
      setLoadingSubjects(false);
    }
  }, []);

  useEffect(() => {
    if (authLoading) {
      return;
    }

    if (!user) {
      setGroups([]);
      setSubjects([]);
      setLoadingGroups(false);
      setLoadingSubjects(false);
      return;
    }

    loadGroups();
    loadSubjects();

    const handleGroupsUpdated = () => {
      loadGroups();
    };
    const handleSubjectsUpdated = () => {
      loadSubjects();
    };

    if (typeof window !== "undefined") {
      window.addEventListener("groupsUpdated", handleGroupsUpdated);
      window.addEventListener("subjectsUpdated", handleSubjectsUpdated);
    }
    
    return () => {
      if (typeof window !== "undefined") {
        window.removeEventListener("groupsUpdated", handleGroupsUpdated);
        window.removeEventListener("subjectsUpdated", handleSubjectsUpdated);
      }
    };
  }, [authLoading, user, loadGroups, loadSubjects]);

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
    const { error } = await signOut();

    if (error) {
      toast({
        title: "로그아웃 실패",
        description: "다시 시도해주세요.",
        variant: "destructive",
      });
      return;
    }

    if (typeof window !== "undefined") {
      window.location.href = "/";
      return;
    }

    router.replace("/");
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
        <header className="flex h-16 items-center border-b bg-white px-4 lg:px-6">
          <Button
            variant="ghost"
            size="icon"
            className="mr-3 lg:hidden"
            onClick={() => setSidebarOpen(true)}
            aria-label="사이드바 열기"
          >
            <Menu className="h-5 w-5" />
          </Button>
          <div className="flex flex-1 justify-end">
            <LanguageSelector />
          </div>
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
