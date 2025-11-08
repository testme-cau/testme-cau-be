import { useState, useEffect, useCallback } from 'react';
import { PDF } from '@/types/api';
import { getPDFs, uploadPDF, deletePDF } from '@/lib/api/pdfs';
import { useApiRequest } from './useApiRequest';

export function usePDFs(subjectId: string) {
  const [pdfs, setPdfs] = useState<PDF[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [uploading, setUploading] = useState(false);
  const { execute } = useApiRequest();

  const loadPDFs = useCallback(async () => {
    if (!subjectId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const data = await getPDFs(subjectId);
      setPdfs(data || []);
    } catch (err: any) {
      const error = err instanceof Error ? err : new Error(err.message || 'Unknown error');
      setError(error);
      setPdfs([]);
    } finally {
      setLoading(false);
    }
  }, [subjectId]);

  useEffect(() => {
    loadPDFs();
  }, [loadPDFs]);

  const upload = async (file: File): Promise<boolean> => {
    setUploading(true);
    
    const result = await execute(
      async () => {
        await uploadPDF(subjectId, file);
        await loadPDFs();
        return true;
      },
      {
        successMessage: "PDF가 업로드되었습니다",
        errorMessage: "PDF 업로드 실패",
      }
    );
    
    setUploading(false);
    return result !== null;
  };

  const remove = async (pdfId: string): Promise<boolean> => {
    const result = await execute(
      async () => {
        await deletePDF(subjectId, pdfId);
        setPdfs(pdfs.filter(p => p.file_id !== pdfId));
        return true;
      },
      {
        successMessage: "PDF가 삭제되었습니다",
        errorMessage: "PDF 삭제 실패",
      }
    );
    
    return result !== null;
  };

  return {
    pdfs,
    loading,
    error,
    uploading,
    uploadPDF: upload,
    deletePDF: remove,
    reload: loadPDFs,
  };
}

