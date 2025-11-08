import { useState, useEffect, useCallback } from 'react';
import { Group, GroupCreateRequest, GroupUpdateRequest } from '@/types/api';
import { groupsApi } from '@/lib/api/groups';
import { useApiRequest } from './useApiRequest';

export function useGroups() {
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const { execute } = useApiRequest();

  const loadGroups = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await groupsApi.getGroups();
      setGroups(data);
    } catch (err: any) {
      const error = err instanceof Error ? err : new Error(err.message || 'Unknown error');
      setError(error);
      setGroups([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadGroups();
  }, [loadGroups]);

  const create = async (data: GroupCreateRequest): Promise<Group | null> => {
    return execute(
      async () => {
        const newGroup = await groupsApi.createGroup(data);
        setGroups([newGroup, ...groups]);
        return newGroup;
      },
      {
        successMessage: "그룹이 생성되었습니다",
        errorMessage: "그룹 생성 실패",
      }
    );
  };

  const update = async (groupId: string, data: GroupUpdateRequest): Promise<Group | null> => {
    return execute(
      async () => {
        const updated = await groupsApi.updateGroup(groupId, data);
        setGroups(groups.map(g => g.group_id === groupId ? updated : g));
        return updated;
      },
      {
        successMessage: "그룹이 수정되었습니다",
        errorMessage: "그룹 수정 실패",
      }
    );
  };

  const remove = async (groupId: string): Promise<boolean> => {
    const result = await execute(
      async () => {
        await groupsApi.deleteGroup(groupId);
        setGroups(groups.filter(g => g.group_id !== groupId));
        return true;
      },
      {
        successMessage: "그룹이 삭제되었습니다",
        errorMessage: "그룹 삭제 실패",
      }
    );
    
    return result !== null;
  };

  return {
    groups,
    loading,
    error,
    createGroup: create,
    updateGroup: update,
    deleteGroup: remove,
    reload: loadGroups,
  };
}

