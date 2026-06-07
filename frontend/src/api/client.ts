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

export type OCRConfig = {
  provider: "rapidocr" | "local_tesseract" | "custom_api" | "openai_vision" | "baidu_ocr";
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
  question: string;
  answer: string;
  chapter: string;
  concept: string;
};

export type AnkiCard = {
  front: string;
  back: string;
  tags: string;
};

export type ReviewReport = {
  title: string;
  summary: string;
  chapters: ChapterReview[];
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
  generated_at: string;
};

export type GenerateReviewResponse = {
  review_report: ReviewReport;
  markdown: string;
  download_path: string;
  download_links: Partial<Record<ExportFormat, string>>;
  anki_csv_download_path?: string | null;
  export_format: ExportFormat;
  report_source?: "rule_based" | "llm_enhanced" | "rule_based_with_llm_failed";
  llm_status?: "disabled" | "success" | "failed";
  fallback_used?: boolean;
  llm_error?: LLMErrorInfo | null;
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
        throw new Error(
          "无法连接后端服务。请重新双击 start.bat；如果仍然失败，请运行 scripts\\stop-app.ps1 后再启动。",
        );
      }
      const data = error.response?.data as { message?: string; detail?: string } | undefined;
      throw new Error(data?.message ?? data?.detail ?? error.message);
    }
    throw error;
  }
}

