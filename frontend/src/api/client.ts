import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  (window.location.port === "5173" ? "http://127.0.0.1:8000" : window.location.origin);

const api = axios.create({ baseURL: API_BASE_URL });

export type UploadedFileInfo = {
  original_filename: string;
  saved_filename: string;
  file_type: string;
  file_size: number;
  saved_path: string;
};

export type UploadResponse = {
  files: UploadedFileInfo[];
  message: string;
};

export type ExportFormat = "md" | "docx" | "pdf";
export type StudyGoal =
  | "one_day_sprint"
  | "three_day_sprint"
  | "seven_day_plan"
  | "memorization"
  | "practice_heavy"
  | "anki_focused"
  | "past_exam_focused"
  | "balanced";
export type ExamType =
  | "unknown"
  | "closed_book"
  | "open_book"
  | "computer_based"
  | "programming"
  | "lab_exam"
  | "essay_based"
  | "oral_presentation"
  | "coursework_report";
export type OptimizationGoal = "memorization" | "practice" | "anki" | "concise" | "detailed" | "sprint" | "exam_like" | "fix_quality";

export type OCRConfig = {
  provider: "rapidocr" | "local_tesseract" | "custom_api" | "openai_vision" | "baidu_ocr";
  mode?: "fast" | "full";
  api_url?: string | null;
  api_key?: string | null;
  secret_key?: string | null;
  language?: string;
};

export type LLMConfig = {
  provider?: string | null;
  model?: string | null;
  api_key?: string | null;
  base_url?: string | null;
  enabled?: boolean;
};

export type LLMErrorInfo = {
  code: string;
  message: string;
  suggestion: string;
  provider?: string | null;
  model?: string | null;
  can_retry?: boolean;
  fallback_used?: boolean;
};

export type LLMTestResponse = {
  ok: boolean;
  provider: string;
  model: string;
  message?: string | null;
  error?: LLMErrorInfo | null;
};

export type ChapterReview = {
  chapter: string;
  importance: number;
  material_frequency: number;
  past_exam_frequency: number;
  weighted_score: number;
  keywords: string[];
  formulas: string[];
  question_types: string[];
  examples: string[];
  frequency: number;
  review_advice: string;
};

export type PastExamTopic = {
  topic: string;
  chapter: string;
  frequency: number;
  question_types: string[];
  keywords: string[];
};

export type PastExamFileAnalysis = {
  filename: string;
  confidence: number;
  question_count: number;
  question_types: string[];
  matched_chapters: string[];
};

export type SprintPlan = {
  days: number;
  title: string;
  schedule: string[];
};

export type GeneratedExamQuestion = {
  question_type: string;
  type?: string;
  question: string;
  answer: string;
  chapter: string;
  concept: string;
  explanation?: string;
  difficulty?: string;
  related_topic?: string;
  source_hint?: string;
};

export type AnkiCard = {
  front: string;
  back: string;
  tags: string;
  card_type?: string;
  priority?: number;
  source_hint?: string;
};

export type StudyUnit = {
  name: string;
  reason: string;
  priority: number;
  must_know: string[];
  key_points: string[];
  formulas_or_methods: string[];
  common_exam_angles: string[];
  pitfalls: string[];
  how_to_review: string;
};

export type QuestionTypeInsight = {
  name: string;
  confidence?: number;
  evidence: string;
  evidence_sources?: string[];
  features: string[];
  related_topics: string[];
  answer_strategy: string;
  sample_questions: string[];
  practice_suggestions?: string;
  is_from_past_exam?: boolean;
};

export type ReportQuality = {
  quality_score: number;
  material_completeness_score: number;
  topic_coverage_score: number;
  mock_exam_quality_score: number;
  anki_quality_score: number;
  export_readiness_score: number;
  evidence_integration_score: number;
  quality_warnings: string[];
  quality_failures: string[];
  repairable: boolean;
};

export type GenerationSummary = {
  files_processed: number;
  pages_total: number;
  pages_text_extracted: number;
  pages_ocr_processed: number;
  pages_ocr_skipped: number;
  ocr_cache_hits: number;
  evidence_chunks: number;
  detected_study_units: number;
  detected_question_types: number;
  mock_questions_count: number;
  anki_cards_count: number;
  llm_calls: number;
  fallback_used: boolean;
  final_report_source: string;
  notes: string[];
};

export type ReviewReport = {
  title: string;
  summary: string;
  study_goal?: StudyGoal;
  exam_type?: ExamType;
  overview?: Record<string, unknown>;
  chapters: ChapterReview[];
  study_units?: StudyUnit[];
  question_types?: QuestionTypeInsight[];
  past_exam_analysis: {
    detected_files: PastExamFileAnalysis[];
    high_frequency_topics: PastExamTopic[];
    summary: string;
  };
  review_order: Array<{
    chapter: string;
    importance: number;
    reason: string;
  }>;
  sprint_plans: SprintPlan[];
  mock_exam: {
    title: string;
    questions: GeneratedExamQuestion[];
  };
  anki_cards: AnkiCard[];
  high_frequency_points: string[];
  sprint_checklist: string[];
  low_priority: string[];
  insufficient_materials: string[];
  quality?: ReportQuality | null;
  markdown?: string;
  generated_at: string;
};

export type GenerateReviewResponse = {
  review_report: ReviewReport;
  markdown: string;
  download_path: string;
  download_links: Partial<Record<ExportFormat, string>>;
  anki_csv_download_path?: string | null;
  export_format: ExportFormat;
  report_source?:
    | "rule_based"
    | "local_safe_draft_with_ai_outline"
    | "llm_enhanced"
    | "llm_markdown_fallback"
    | "rule_based_with_llm_failed";
  llm_status?: "disabled" | "success" | "failed";
  fallback_used?: boolean;
  llm_error?: LLMErrorInfo | null;
  llm_context_strategy?: "disabled" | "direct" | "compressed" | "chunked" | "failed";
  generation_summary?: GenerationSummary;
};

export type GenerateReviewJob = {
  job_id: string;
  status: "queued" | "running" | "completed" | "failed";
  progress: number;
  message: string;
  result: GenerateReviewResponse | null;
  error: string | null;
  created_at: string;
  updated_at: string;
};

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export type MockExamQuestion = {
  question: string;
  answer: string;
  chapter: string;
  concept: string;
  question_type: string;
};

export type GenerateMockExamResponse = {
  questions: MockExamQuestion[];
  message: string;
};

export type GenerateReviewParams = {
  files: string[];
  export_format?: ExportFormat;
  export_formats?: ExportFormat[];
  title: string;
  course_name?: string;
  study_goal?: StudyGoal;
  exam_type?: ExamType;
  ocr_config: OCRConfig;
  llm_config: LLMConfig;
};

export async function uploadFiles(files: File[]): Promise<UploadResponse> {
  const body = new FormData();
  files.forEach((file) => body.append("files", file));
  return request<UploadResponse>("/upload", { method: "POST", body });
}

export async function generateReview(params: GenerateReviewParams): Promise<GenerateReviewResponse> {
  return request<GenerateReviewResponse>("/generate-review", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
}

export async function reoptimizeReview(params: {
  current_report: ReviewReport;
  evidence_text?: string;
  optimization_goal: OptimizationGoal;
  original_study_goal: StudyGoal;
  original_exam_type: ExamType;
  llm_config: LLMConfig;
}): Promise<{ review_report: ReviewReport; markdown: string; optimized: boolean; message: string; quality: ReportQuality }> {
  return request("/api/review/reoptimize", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
}

export async function createGenerateReviewJob(params: GenerateReviewParams): Promise<{ job_id: string }> {
  return request<{ job_id: string }>("/generate-review-jobs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
}

export async function getGenerateReviewJob(jobId: string): Promise<GenerateReviewJob> {
  return request<GenerateReviewJob>(`/generate-review-jobs/${jobId}`, { method: "GET" });
}

export async function testLLMConnection(config: LLMConfig): Promise<LLMTestResponse> {
  return request<LLMTestResponse>("/api/llm/test", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });
}

export async function chat(params: {
  message: string;
  review_report: ReviewReport | null;
  history: ChatMessage[];
}): Promise<{ reply: string }> {
  return request<{ reply: string }>("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
}

export async function generateMockExam(
  reviewReport: ReviewReport,
  count = 8,
): Promise<GenerateMockExamResponse> {
  return request<GenerateMockExamResponse>("/generate-mock-exam", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ review_report: reviewReport, count }),
  });
}

export function downloadUrl(downloadPath: string): string {
  if (downloadPath.startsWith("/")) {
    return `${API_BASE_URL}${downloadPath}`;
  }
  const filename = downloadPath.split(/[\\/]/).pop();
  return filename ? `${API_BASE_URL}/download/${encodeURIComponent(filename)}` : "#";
}

async function request<T>(path: string, options: RequestInit): Promise<T> {
  try {
    const response = await api.request<T>({
      url: path,
      method: options.method,
      data: options.body,
      headers: options.headers as Record<string, string> | undefined,
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (!error.response) {
        throw new Error("无法连接后端服务。请重新双击 start.bat；如果仍然失败，请运行 scripts\\stop-app.ps1 后再启动。");
      }
      const data = error.response?.data as { message?: string; detail?: string } | undefined;
      throw new Error(data?.message ?? data?.detail ?? error.message);
    }
    throw error;
  }
}
