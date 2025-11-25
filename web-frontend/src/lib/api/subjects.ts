import apiClient from '@/lib/api/client';
import type {
  Subject,
  SubjectCreateRequest,
  SubjectListResponse,
  SubjectResponse,
  SubjectUpdateRequest,
} from '@/types/api';

const SUBJECTS_ENDPOINT = '/api/subjects';

export async function getSubjects(): Promise<Subject[]> {
  const { data } =
    await apiClient.get<SubjectListResponse>(SUBJECTS_ENDPOINT);
  return data.subjects;
}

export async function getSubject(subjectId: string): Promise<Subject> {
  const { data } = await apiClient.get<SubjectResponse>(
    `${SUBJECTS_ENDPOINT}/${subjectId}`
  );
  return data.subject;
}

export async function createSubject(
  payload: SubjectCreateRequest
): Promise<Subject> {
  const { data } = await apiClient.post<SubjectResponse>(
    SUBJECTS_ENDPOINT,
    payload
  );
  return data.subject;
}

export async function updateSubject(
  subjectId: string,
  payload: SubjectUpdateRequest
): Promise<Subject> {
  const { data } = await apiClient.put<SubjectResponse>(
    `${SUBJECTS_ENDPOINT}/${subjectId}`,
    payload
  );
  return data.subject;
}

export async function deleteSubject(subjectId: string): Promise<void> {
  await apiClient.delete(`${SUBJECTS_ENDPOINT}/${subjectId}`);
}

