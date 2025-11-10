// Group Types
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
  pdf_id: string;
  user_id: string;
  questions: Question[];
  total_points: number;
  estimated_time: number;
  num_questions: number;
  difficulty: 'easy' | 'medium' | 'hard';
  created_at: string;
  status: string;
  ai_provider?: string;
}

export interface ExamGenerationRequest {
  pdf_id: string;
  num_questions: number;
  difficulty?: 'easy' | 'medium' | 'hard';
  ai_provider?: 'gpt' | 'gemini';
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
  is_correct?: boolean;
}

export interface GradingResult {
  total_score: number;
  max_score: number;
  percentage: number;
  question_results: QuestionResult[];
  ai_provider?: string;
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

export interface GradingResponse {
  success: boolean;
  grading: GradingResult;
}

