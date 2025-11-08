import apiClient from './client';
import {
  PDF,
  PDFUploadResponse,
  PDFListResponse,
  APIResponse,
} from '@/types/api';

/**
 * Upload a PDF file
 */
export async function uploadPDF(subjectId: string, file: File): Promise<PDF> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post<PDFUploadResponse>(
    `/api/subjects/${subjectId}/pdfs/upload`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  
  // 백엔드 응답을 PDF 타입으로 변환
  const data = response.data;
  return {
    file_id: data.file_id,
    subject_id: subjectId,
    original_filename: data.original_filename,
    unique_filename: '', // 백엔드 응답에 없음
    storage_path: '', // 백엔드 응답에 없음
    size: data.size,
    user_id: '', // 백엔드 응답에 없음
    uploaded_at: data.uploaded_at,
    status: 'uploaded'
  };
}

/**
 * Get all PDFs for a subject
 */
export async function getPDFs(subjectId: string): Promise<PDF[]> {
  const response = await apiClient.get<PDFListResponse>(
    `/api/subjects/${subjectId}/pdfs`
  );
  return response.data.pdfs || [];
}

/**
 * Get download URL for a PDF (opens in new tab)
 */
export function getPDFDownloadUrl(subjectId: string, fileId: string): string {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
  return `${baseUrl}/api/subjects/${subjectId}/pdfs/${fileId}/download`;
}

/**
 * Download a PDF file
 */
export async function downloadPDF(subjectId: string, fileId: string): Promise<void> {
  try {
    // apiClient를 사용하여 다운로드 URL 가져오기
    const response = await apiClient.get<{ success: boolean; download_url: string; filename: string }>(
      `/api/subjects/${subjectId}/pdfs/${fileId}/download`
    );
    
    if (response.data.download_url) {
      // Firebase Storage signed URL을 새 탭에서 열기
      window.open(response.data.download_url, '_blank');
    } else {
      throw new Error('다운로드 URL을 가져올 수 없습니다.');
    }
  } catch (error) {
    console.error('Download failed:', error);
    throw error;
  }
}

/**
 * Delete a PDF file
 */
export async function deletePDF(subjectId: string, fileId: string): Promise<void> {
  await apiClient.delete<APIResponse<null>>(
    `/api/subjects/${subjectId}/pdfs/${fileId}`
  );
}

