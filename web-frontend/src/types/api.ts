// Group Types
export type ServiceStatus = 'closed_beta' | 'open_beta' | 'release';

export interface Group {
  group_id: string;
  user_id: string;
  name: string;
  description?: string | null;
  color?: string | null;
  icon?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface GroupCreateRequest {
  name: string;
  description?: string;
  color?: string;
  icon?: string;
}

export interface GroupUpdateRequest {
  name?: string;
  description?: string;
  color?: string;
  icon?: string;
}

// Subject Types
export interface LanguageOption {
  code: string;
  name: string;
  native_name: string;
  flag: string;
}

export interface LanguageListResponse {
  success: boolean;
  languages: LanguageOption[];
  count: number;
}

export interface UserProfile {
  uid: string;
  email?: string | null;
  display_name?: string | null;
  photo_url?: string | null;
  language_preference: string;
  created_at?: string;
  updated_at?: string | null;
}

export interface UserProfileResponse {
  success: boolean;
  user: UserProfile;
}

export interface UserProfileUpdateRequest {
  display_name?: string;
  language_preference?: string;
}

export interface Subject {
  subject_id: string;
  user_id: string;
  name: string;
  description?: string | null;
  group_id?: string | null;
  color?: string | null;
  language_preference?: string | null;
  pdf_count?: number;
  exam_count?: number;
  created_at: string;
  updated_at?: string | null;
}

export interface SubjectCreateRequest {
  name: string;
  description?: string;
  group_id?: string;
  color?: string;
  language_preference?: string;
}

export interface SubjectUpdateRequest {
  name?: string;
  description?: string;
  group_id?: string;
  color?: string;
  language_preference?: string;
}

// PDF Types
export interface PDF {
  file_id: string;
  subject_id: string;
  original_filename: string;
  unique_filename: string;
  storage_path: string;
  size: number;
  user_id: string;
  uploaded_at: string;
  status: string;
}

// Exam Types
export interface Question {
  id: number;
  question: string;
  type: 'multiple_choice' | 'essay';
  options?: string[] | null;
  points: number;
}

export interface Exam {
  exam_id: string;
  subject_id: string;
  title?: string;  // AI-generated exam title
  pdf_id: string;  // Keep for backward compatibility
  pdf_ids?: string[];  // New field: multiple PDFs
  user_id: string;
  questions: Question[];
  total_points: number;
  estimated_time: number;
  num_questions: number;
  difficulty: 'easy' | 'medium' | 'hard';
  created_at: string;
  status: string;
  ai_provider?: string;
  language?: string;
}

export interface ExamGenerationRequest {
  pdf_ids: string[];  // Changed from pdf_id to pdf_ids
  num_questions: number;
  difficulty?: 'easy' | 'medium' | 'hard';
  ai_provider?: 'gpt' | 'gemini';
  language?: string;
}

export interface AnswerSubmission {
  question_id: number;
  answer: string;
}

export interface ExamSubmissionRequest {
  exam_id: string;
  answers: AnswerSubmission[];
  ai_provider?: 'gpt' | 'gemini';
}

export interface QuestionResult {
  question_id: number;
  score: number;
  max_points: number;
  feedback: string;
  model_answer?: string;
  is_correct?: boolean;
}

export interface GradingResult {
  total_score: number;
  max_score: number;
  percentage: number;
  question_results: QuestionResult[];
  ai_provider?: string;
}

export interface SubmissionResult {
  submission_id: string;
  status: 'pending' | 'grading' | 'graded' | 'failed';
  answers?: AnswerSubmission[];
  grading_result?: GradingResult;
  error_message?: string;
  submitted_at: string;
  graded_at?: string;
}

export type JobStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';

export interface ExamJob {
  job_id: string;
  subject_id: string;
  pdf_ids: string[];
  num_questions: number;
  difficulty: 'easy' | 'medium' | 'hard';
  ai_provider?: 'gpt' | 'gemini';
  ai_model?: string;
  language?: string;
  status: JobStatus;
  progress_percentage: number;
  estimated_duration_seconds?: number;
  exam_id?: string;
  error_message?: string;
  created_at?: string;
  started_at?: string;
  completed_at?: string;
  failed_at?: string;
  cancelled_at?: string;
}

export interface GradingJob {
  job_id: string;
  subject_id: string;
  exam_id: string;
  submission_id: string;
  total_questions: number;
  status: JobStatus;
  ai_provider?: 'gpt' | 'gemini';
  progress_percentage: number;
  estimated_duration_seconds?: number;
  error_message?: string;
  created_at?: string;
  started_at?: string;
  completed_at?: string;
  failed_at?: string;
  cancelled_at?: string;
}

// API Response Types
export interface APIResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface GroupResponse {
  success: boolean;
  group: Group;
}

export interface GroupListResponse {
  success: boolean;
  groups: Group[];
  count: number;
}

export interface SubjectResponse {
  success: boolean;
  subject: Subject;
}

export interface SubjectListResponse {
  success: boolean;
  subjects: Subject[];
  count: number;
}

export interface PDFUploadResponse {
  success: boolean;
  file_id: string;
  original_filename: string;
  file_url: string;
  uploaded_at: string;
  size: number;
}

export interface PDFListResponse {
  success: boolean;
  pdfs: PDF[];
  count: number;
}

export interface ExamResponse {
  success: boolean;
  message?: string;
  exam: Exam;
}

export interface ExamListResponse {
  success: boolean;
  exams: Exam[];
  count: number;
}

export interface ExamJobResponse {
  success: boolean;
  job: ExamJob;
}

export interface ExamJobListResponse {
  success: boolean;
  jobs: ExamJob[];
}

export interface GradingResponse {
  success: boolean;
  grading: GradingResult;
}

export interface GradingJobResponse {
  success: boolean;
  submission_id: string;
  job: GradingJob;
}

export interface GradingJobListResponse {
  success: boolean;
  jobs: GradingJob[];
}

export interface BetaStatusResponse {
  status: ServiceStatus;
  allowed_emails: string[];
  updated_at?: string | null;
  updated_by?: string | null;
}

export interface WaitlistJoinPayload {
  email: string;
  note?: string;
}

export interface WaitlistJoinResponse {
  success: boolean;
  already_allowed?: boolean;
  already_pending?: boolean;
  message: string;
}

