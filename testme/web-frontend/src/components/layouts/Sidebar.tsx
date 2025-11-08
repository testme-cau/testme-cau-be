"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Logo } from "@/components/ui/logo";
import { X, Home, LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { Group } from "@/types/api";
import { GroupsSection } from "./GroupsSection";
import { SidebarUserProfile } from "./SidebarUserProfile";

interface NavigationItem {
  name: string;
  href: string;
  icon: LucideIcon;
}

interface SidebarProps {
  sidebarOpen: boolean;
  onSidebarClose: () => void;
  groups: Group[];
  loadingGroups: boolean;
  selectedGroup: string | null;
  onGroupClick: (groupId: string | null) => void;
  onGroupEdit: (group: Group, e: React.MouseEvent) => void;
  onGroupDelete: (group: Group, e: React.MouseEvent) => void;
  onNewGroupClick: () => void;
  user: {
    displayName?: string | null;
    email?: string | null;
  } | null;
  onSignOut: () => void;
}

export function Sidebar({
  sidebarOpen,
  onSidebarClose,
  groups,
  loadingGroups,
  selectedGroup,
  onGroupClick,
  onGroupEdit,
  onGroupDelete,
  onNewGroupClick,
  user,
  onSignOut,
}: SidebarProps) {
  const pathname = usePathname();

  const navigation: NavigationItem[] = [
    { name: "대시보드", href: "/dashboard", icon: Home },
  ];

  return (
    <>
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={onSidebarClose}
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
              onClick={onSidebarClose}
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
                  onClick={onSidebarClose}
                >
                  <Icon className="h-5 w-5" />
                  {item.name}
                </Link>
              );
            })}

            {/* Groups Section */}
            <GroupsSection
              groups={groups}
              loading={loadingGroups}
              selectedGroup={selectedGroup}
              onGroupClick={onGroupClick}
              onEditClick={onGroupEdit}
              onDeleteClick={onGroupDelete}
              onNewGroupClick={onNewGroupClick}
            />
          </nav>

          {/* User info */}
          <SidebarUserProfile user={user} onSignOut={onSignOut} />
        </div>
      </aside>
    </>
  );
}

