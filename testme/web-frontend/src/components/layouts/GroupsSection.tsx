"use client";

import { Folder, Plus, Pencil, Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { Group } from "@/types/api";
import { useTranslations } from "next-intl";

interface GroupsSectionProps {
  groups: Group[];
  loading: boolean;
  selectedGroup: string | null;
  onGroupClick: (groupId: string | null) => void;
  onEditClick: (group: Group, e: React.MouseEvent) => void;
  onDeleteClick: (group: Group, e: React.MouseEvent) => void;
  onNewGroupClick: () => void;
}

export function GroupsSection({
  groups,
  loading,
  selectedGroup,
  onGroupClick,
  onEditClick,
  onDeleteClick,
  onNewGroupClick,
}: GroupsSectionProps) {
  const t = useTranslations("groups");

  return (
    <div className="pt-4 mt-4 border-t">
      <div className="flex items-center justify-between mb-2 px-2">
        <div className="flex items-center gap-2">
          <Folder className="h-4 w-4 text-gray-500" />
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
            {t("title")}
          </span>
        </div>
        <button
          onClick={onNewGroupClick}
          className="p-1 rounded hover:bg-emerald-50 text-emerald-600 transition-colors"
          title={t("new")}
        >
          <Plus className="h-4 w-4" />
        </button>
      </div>

      {loading ? (
        <div className="px-3 py-2 text-xs text-gray-500">{t("loading")}</div>
      ) : (
        <div className="space-y-1">
          <button
            onClick={() => onGroupClick(null)}
            className={cn(
              "w-full flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200",
              !selectedGroup
                ? "bg-emerald-50 text-emerald-700"
                : "text-gray-700 hover:bg-gray-50"
            )}
          >
            {t("all")}
          </button>
          <button
            onClick={() => onGroupClick("none")}
            className={cn(
              "w-full flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200",
              selectedGroup === "none"
                ? "bg-emerald-50 text-emerald-700"
                : "text-gray-700 hover:bg-gray-50"
            )}
          >
            {t("none")}
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
                onClick={() => onGroupClick(group.group_id)}
                className="flex-1 text-left truncate"
              >
                {group.name}
              </button>
              <div className="flex items-center gap-1 opacity-0 group-hover/item:opacity-100 transition-all">
                <button
                  onClick={(e) => onEditClick(group, e)}
                  className="p-1 rounded hover:bg-emerald-50 text-emerald-600 transition-all"
                  title={t("edit")}
                >
                  <Pencil className="h-3 w-3" />
                </button>
                <button
                  onClick={(e) => onDeleteClick(group, e)}
                  className="p-1 rounded hover:bg-red-50 text-red-600 transition-all"
                  title={t("delete")}
                >
                  <Trash2 className="h-3 w-3" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

