"use client";

import { Button } from "@/components/ui/button";
import { LogOut, User } from "lucide-react";

interface SidebarUserProfileProps {
  user: {
    displayName?: string | null;
    email?: string | null;
  } | null;
  onSignOut: () => void;
}

export function SidebarUserProfile({ user, onSignOut }: SidebarUserProfileProps) {
  return (
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
        onClick={onSignOut}
      >
        <LogOut className="mr-2 h-4 w-4" />
        로그아웃
      </Button>
    </div>
  );
}

