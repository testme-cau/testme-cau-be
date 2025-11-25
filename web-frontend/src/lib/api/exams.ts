import apiClient from '@/lib/api/client';
import type {
  Exam,
  ExamGenerationRequest,
  ExamJob,
  ExamJobListResponse,
  ExamJobResponse,
  ExamListResponse,
  ExamResponse,
  GradingJob,
  GradingJobListResponse,
  GradingJobResponse,
  SubmissionResult,
} from '@/types/api';

const subjectsEndpoint = (subjectId: string) => `/api/subjects/${subjectId}`;

export async function getExams(subjectId: string): Promise<Exam[]> {
  const { data } = await apiClient.get<ExamListResponse>(
    `${subjectsEndpoint(subjectId)}/exams`
  );
  return data.exams ?? [];
}

export async function getExam(
  subjectId: string,
  examId: string
): Promise<Exam> {
  const { data } = await apiClient.get<ExamResponse>(
    `${subjectsEndpoint(subjectId)}/exams/${examId}`
  );
  return data.exam;
}

export async function deleteExam(
  subjectId: string,
  examId: string
): Promise<void> {
  await apiClient.delete(
    `${subjectsEndpoint(subjectId)}/exams/${examId}`
  );
}

export async function generateExam(
  subjectId: string,
  payload: ExamGenerationRequest
): Promise<ExamJob> {
  const { data } = await apiClient.post<ExamJobResponse>(
    `${subjectsEndpoint(subjectId)}/exams/generate`,
    payload
  );
  return data.job;
}

export async function getExamJobs(subjectId: string): Promise<ExamJob[]> {
  const { data } = await apiClient.get<ExamJobListResponse>(
    `${subjectsEndpoint(subjectId)}/exam-jobs`
  );
  return data.jobs ?? [];
}

export async function cancelExamJob(
  subjectId: string,
  jobId: string
): Promise<ExamJob> {
  const { data } = await apiClient.delete<ExamJobResponse>(
    `${subjectsEndpoint(subjectId)}/exam-jobs/${jobId}`
  );
  return data.job;
}

export async function getGradingJobs(
  subjectId: string
): Promise<GradingJob[]> {
  const { data } = await apiClient.get<GradingJobListResponse>(
    `${subjectsEndpoint(subjectId)}/grading-jobs`
  );
  return data.jobs ?? [];
}

export async function submitExam(
  subjectId: string,
  examId: string,
  answers: Array<{ question_id: number; answer: string }>
): Promise<GradingJobResponse> {
  const { data } = await apiClient.post<GradingJobResponse>(
    `${subjectsEndpoint(subjectId)}/exams/${examId}/submit`,
    answers
  );
  return data;
}

export async function getSubmission(
  subjectId: string,
  examId: string
): Promise<SubmissionResult> {
  const { data } = await apiClient.get<{ success: boolean; submission: SubmissionResult }>(
    `${subjectsEndpoint(subjectId)}/exams/${examId}/submission`
  );
  return data.submission;
}

