import { useState, useEffect, useCallback } from 'react';
import { Subject, SubjectUpdateRequest } from '@/types/api';
import { getSubject, updateSubject, deleteSubject } from '@/lib/api/subjects';
import { useApiRequest } from './useApiRequest';

export function useSubject(subjectId: string) {
  const [subject, setSubject] = useState<Subject | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const { execute } = useApiRequest();

  const loadSubject = useCallback(async () => {
    if (!subjectId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const data = await getSubject(subjectId);
      setSubject(data);
    } catch (err: any) {
      const error = err instanceof Error ? err : new Error(err.message || 'Unknown error');
      setError(error);
    } finally {
      setLoading(false);
    }
  }, [subjectId]);

  useEffect(() => {
    loadSubject();
  }, [loadSubject]);

  const update = async (data: SubjectUpdateRequest): Promise<Subject | null> => {
    return execute(
      async () => {
        const updated = await updateSubject(subjectId, data);
        setSubject(updated);
        return updated;
      },
      {
        successMessage: "과목이 수정되었습니다",
        errorMessage: "과목 수정 실패",
      }
    );
  };

  const remove = async (): Promise<boolean> => {
    const result = await execute(
      async () => {
        await deleteSubject(subjectId);
        return true;
      },
      {
        successMessage: "과목이 삭제되었습니다",
        errorMessage: "과목 삭제 실패",
      }
    );
    
    return result !== null;
  };

  return {
    subject,
    loading,
    error,
    updateSubject: update,
    deleteSubject: remove,
    reload: loadSubject,
  };
}

