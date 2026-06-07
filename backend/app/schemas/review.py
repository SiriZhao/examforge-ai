from typing import Literal

from pydantic import BaseModel, Field


class UploadedFileInfo(BaseModel):
    original_filename: str
    saved_filename: str
    file_type: str
    file_size: int
    saved_path: str


class UploadResponse(BaseModel):
    files: list[UploadedFileInfo]
    message: str


OCRProvider = Literal[
    "rapidocr",
    "local_tesseract",
    "custom_api",
    "openai_vision",
    "baidu_ocr",
]


class OCRConfig(BaseModel):
    provider: OCRProvider = "rapidocr"
    api_url: str | None = None
    api_key: str | None = None
    secret_key: str | None = None
    model: str | None = None
    language: str = "chi_sim+eng"


class ParseRequest(BaseModel):
    files: list[str]
    ocr_config: OCRConfig = Field(default_factory=OCRConfig)


class ParsedPage(BaseModel):
    page_number: int
    text: str
    source: Literal["text_extract", "ocr_fallback"]


class ParsedFile(BaseModel):
    filename: str
    file_type: str
    path: str
    pages: list[ParsedPage]
    raw_text: str


class ParseResponse(BaseModel):
    files: list[ParsedFile]
    message: str


ExportFormat = Literal["md", "docx", "pdf"]
QuestionType = Literal["选择题", "填空题", "判断题", "计算题", "简答题", "论述题", "未知"]
DifficultyLevel = Literal["简单", "中等", "困难", "未知"]


class LLMConfig(BaseModel):
    provider: str | None = None
    model: str | None = None
    api_key: str | None = None
    base_url: str | None = None
    enabled: bool = False


LLMErrorCode = Literal[
    "CONFIG_MISSING",
    "AUTH_FAILED",
    "NETWORK_ERROR",
    "TIMEOUT",
    "MODEL_NOT_FOUND",
    "RATE_LIMITED",
    "CONTEXT_TOO_LONG",
    "RESPONSE_PARSE_ERROR",
    "UNKNOWN_ERROR",
]

ReportSource = Literal["rule_based", "llm_enhanced", "rule_based_with_llm_failed"]
LLMStatus = Literal["disabled", "success", "failed"]
LLMContextStrategy = Literal["disabled", "direct", "compressed", "chunked", "failed"]


class LLMErrorInfo(BaseModel):
    code: LLMErrorCode
    message: str
    suggestion: str
    provider: str | None = None
    model: str | None = None
    can_retry: bool = True
    fallback_used: bool = False


class LLMTestRequest(LLMConfig):
    enabled: bool = True


class LLMTestResponse(BaseModel):
    ok: bool
    provider: str
    model: str
    message: str | None = None
    error: LLMErrorInfo | None = None


class GenerateReviewRequest(BaseModel):
    files: list[str]
    export_format: ExportFormat = "md"
    export_formats: list[ExportFormat] | None = None
    title: str = "期末复习资料包"
    course_name: str | None = None
    material_types: dict[str, str] = Field(default_factory=dict)
    ocr_config: OCRConfig = Field(default_factory=OCRConfig)
    llm_config: LLMConfig = Field(default_factory=LLMConfig)


class ExamQuestion(BaseModel):
    question: str
    question_type: QuestionType
    chapter: str | None = None
    difficulty: DifficultyLevel = "未知"
    keywords: list[str] = Field(default_factory=list)


class ChapterReview(BaseModel):
    chapter: str
    importance: int = Field(ge=0, le=100)
    material_frequency: int = Field(default=0, ge=0)
    past_exam_frequency: int = Field(default=0, ge=0)
    weighted_score: int = Field(default=0, ge=0, le=100)
    keywords: list[str] = Field(default_factory=list)
    formulas: list[str] = Field(default_factory=list)
    question_types: list[QuestionType] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)
    frequency: int = Field(ge=0)
    review_advice: str


class PastExamTopic(BaseModel):
    topic: str
    chapter: str
    frequency: int = Field(ge=0)
    question_types: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)


class PastExamFileAnalysis(BaseModel):
    filename: str
    confidence: int = Field(ge=0, le=100)
    question_count: int = Field(ge=0)
    question_types: list[str] = Field(default_factory=list)
    matched_chapters: list[str] = Field(default_factory=list)


class PastExamAnalysis(BaseModel):
    detected_files: list[PastExamFileAnalysis] = Field(default_factory=list)
    high_frequency_topics: list[PastExamTopic] = Field(default_factory=list)
    summary: str = ""


class ReviewPlanItem(BaseModel):
    chapter: str
    importance: int = Field(ge=0, le=100)
    reason: str


class SprintPlan(BaseModel):
    days: int
    title: str
    schedule: list[str] = Field(default_factory=list)


class GeneratedExamQuestion(BaseModel):
    question_type: str
    question: str
    answer: str
    chapter: str
    concept: str


class GeneratedMockExam(BaseModel):
    title: str
    questions: list[GeneratedExamQuestion] = Field(default_factory=list)


class AnkiCard(BaseModel):
    front: str
    back: str
    tags: str


class ReviewReport(BaseModel):
    title: str
    summary: str
    chapters: list[ChapterReview] = Field(default_factory=list)
    past_exam_analysis: PastExamAnalysis = Field(default_factory=PastExamAnalysis)
    review_order: list[ReviewPlanItem] = Field(default_factory=list)
    sprint_plans: list[SprintPlan] = Field(default_factory=list)
    mock_exam: GeneratedMockExam = Field(default_factory=lambda: GeneratedMockExam(title="模拟卷"))
    anki_cards: list[AnkiCard] = Field(default_factory=list)
    high_frequency_points: list[str] = Field(default_factory=list)
    sprint_checklist: list[str] = Field(default_factory=list)
    low_priority: list[str] = Field(default_factory=list)
    insufficient_materials: list[str] = Field(default_factory=list)
    generated_at: str


class GenerateReviewResponse(BaseModel):
    review_report: ReviewReport
    markdown: str
    download_path: str
    download_links: dict[ExportFormat, str] = Field(default_factory=dict)
    anki_csv_download_path: str | None = None
    export_format: ExportFormat
    report_source: ReportSource = "rule_based"
    llm_status: LLMStatus = "disabled"
    fallback_used: bool = False
    llm_error: LLMErrorInfo | None = None
    llm_context_strategy: LLMContextStrategy = "disabled"


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    review_report: ReviewReport | None = None
    history: list[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str


class MockExamQuestion(BaseModel):
    question: str
    answer: str
    chapter: str
    concept: str
    question_type: QuestionType


class GenerateMockExamRequest(BaseModel):
    review_report: ReviewReport
    count: int = Field(default=8, ge=1, le=30)


class GenerateMockExamResponse(BaseModel):
    questions: list[MockExamQuestion]
    message: str


class AnalyzeRequest(BaseModel):
    file_id: str
    focus: str | None = None


class TopicSummary(BaseModel):
    topic: str
    confidence: float
    notes: list[str]


class AnalyzeResponse(BaseModel):
    file_id: str
    summaries: list[TopicSummary]
    recommendations: list[str]


class ExportRequest(BaseModel):
    file_id: str
    format: str = "markdown"


class ExportResponse(BaseModel):
    file_id: str
    output_path: str
