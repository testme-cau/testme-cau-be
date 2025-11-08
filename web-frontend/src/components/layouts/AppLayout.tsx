"use client";

import { ReactNode, useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useSearchParams, useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { signOut } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Logo } from "@/components/ui/logo";
import {
  Menu,
  X,
  Home,
  BookOpen,
  FileText,
  LogOut,
  User,
  Folder,
  Plus,
  Trash2,
  Pencil,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { groupsApi } from "@/lib/api/groups";
import { Group } from "@/types/api";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { useToast } from "@/hooks/use-toast";
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
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const router = useRouter();
  const { user } = useAuth();
  const { toast } = useToast();

  const selectedGroup = searchParams.get("group");

  const navigation = [
    { name: "대시보드", href: "/dashboard", icon: Home },
  ];

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
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-64 transform bg-white shadow-lg transition-transform duration-300 ease-in-out lg:static lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-16 items-center justify-between border-b px-6">
            <Logo size="md" href="/dashboard" />
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="h-5 w-5" />
            </Button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 p-4 overflow-y-auto">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href && !selectedGroup;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200",
                    isActive
                      ? "bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-md"
                      : "text-gray-700 hover:bg-emerald-50 hover:text-emerald-700"
                  )}
                  onClick={() => setSidebarOpen(false)}
                >
                  <Icon className="h-5 w-5" />
                  {item.name}
                </Link>
              );
            })}

            {/* Groups Section */}
              <div className="pt-4 mt-4 border-t">
                <div className="flex items-center justify-between mb-2 px-2">
                  <div className="flex items-center gap-2">
                    <Folder className="h-4 w-4 text-gray-500" />
                    <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">그룹</span>
                  </div>
                  <button
                    onClick={() => {
                      setEditingGroup(null);
                      setGroupFormData({ name: "", description: "" });
                      setShowGroupForm(true);
                    }}
                    className="p-1 rounded hover:bg-emerald-50 text-emerald-600 transition-colors"
                    title="새 그룹"
                  >
                    <Plus className="h-4 w-4" />
                  </button>
                </div>


              {loadingGroups ? (
                <div className="px-3 py-2 text-xs text-gray-500">로딩 중...</div>
              ) : (
                <div className="space-y-1">
                  <button
                    onClick={() => handleGroupClick(null)}
                    className={cn(
                      "w-full flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200",
                      !selectedGroup
                        ? "bg-emerald-50 text-emerald-700"
                        : "text-gray-700 hover:bg-gray-50"
                    )}
                  >
                    모든 과목
                  </button>
                  <button
                    onClick={() => handleGroupClick("none")}
                    className={cn(
                      "w-full flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200",
                      selectedGroup === "none"
                        ? "bg-emerald-50 text-emerald-700"
                        : "text-gray-700 hover:bg-gray-50"
                    )}
                  >
                    그룹 없음
                  </button>
                  {groups.map((group) => (
                    <div
                      key={group.group_id}
                      className={cn(
                        "group/item relative flex items-center gap-1 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200",
                        selectedGroup === group.group_id
                          ? "bg-emerald-50 text-emerald-700"
                          : "text-gray-700 hover:bg-gray-50"
                      )}
                    >
                      <button
                        onClick={() => handleGroupClick(group.group_id)}
                        className="flex-1 text-left truncate"
                      >
                        {group.name}
                      </button>
                      <div className="flex items-center gap-1 opacity-0 group-hover/item:opacity-100 transition-all">
                        <button
                          onClick={(e) => handleEditClick(group, e)}
                          className="p-1 rounded hover:bg-emerald-50 text-emerald-600 transition-all"
                          title="수정"
                        >
                          <Pencil className="h-3 w-3" />
                        </button>
                        <button
                          onClick={(e) => handleDeleteClick(group, e)}
                          className="p-1 rounded hover:bg-red-50 text-red-600 transition-all"
                          title="삭제"
                        >
                          <Trash2 className="h-3 w-3" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </nav>

          {/* User info */}
          <div className="border-t p-4">
            <div className="mb-3 flex items-center gap-3 rounded-lg bg-gray-100 p-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 text-white shadow-sm">
                <User className="h-4 w-4" />
              </div>
              <div className="flex-1 overflow-hidden">
                <p className="truncate text-sm font-medium">
                  {user?.displayName || user?.email}
                </p>
                <p className="truncate text-xs text-gray-500">{user?.email}</p>
              </div>
            </div>
            <Button
              variant="outline"
              className="w-full hover:bg-emerald-50 hover:text-emerald-700 hover:border-emerald-500 transition-colors"
              onClick={handleSignOut}
            >
              <LogOut className="mr-2 h-4 w-4" />
              로그아웃
            </Button>
          </div>
        </div>
      </aside>

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
      <Dialog open={showGroupForm} onOpenChange={setShowGroupForm}>
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
                value={groupFormData.name}
                onChange={(e) => setGroupFormData({ ...groupFormData, name: e.target.value })}
                disabled={creatingGroup}
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
                value={groupFormData.description}
                onChange={(e) => setGroupFormData({ ...groupFormData, description: e.target.value })}
                disabled={creatingGroup}
                rows={3}
                className="w-full resize-none"
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setShowGroupForm(false);
                setGroupFormData({ name: "", description: "" });
                setEditingGroup(null);
              }}
              disabled={creatingGroup}
            >
              취소
            </Button>
            <Button
              type="button"
              onClick={handleCreateGroup}
              disabled={creatingGroup || !groupFormData.name.trim()}
              className="bg-emerald-600 hover:bg-emerald-700"
            >
              {creatingGroup ? (
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

