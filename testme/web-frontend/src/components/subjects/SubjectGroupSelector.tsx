import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { Group } from "@/types/api";
import { Folder } from "lucide-react";

interface SubjectGroupSelectorProps {
  currentGroupId?: string | null;
  groups: Group[];
  loading: boolean;
  onChange: (groupId: string) => void;
}

export function SubjectGroupSelector({
  currentGroupId,
  groups,
  loading,
  onChange,
}: SubjectGroupSelectorProps) {
  return (
    <div className="mt-4 flex items-center gap-3">
      <Folder className="h-4 w-4 text-gray-500" />
      <span className="text-sm font-medium text-gray-700">그룹:</span>
      <Select
        value={currentGroupId || "none"}
        onValueChange={onChange}
        disabled={loading}
      >
        <SelectTrigger className="w-[200px]">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="none">그룹 없음</SelectItem>
          {groups.map((group) => (
            <SelectItem key={group.group_id} value={group.group_id}>
              {group.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {loading && <LoadingSpinner size="sm" />}
    </div>
  );
}

