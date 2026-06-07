import { useMemo, useRef, useState, type RefObject } from "react";

import {
  createGenerateReviewJob,
  getGenerateReviewJob,
  testLLMConnection,
  uploadFiles,
  type ExportFormat,
  type GenerateReviewResponse,
  type LLMConfig,
  type LLMTestResponse,
  type OCRConfig,
} from "./api/client";
import { ChatPanel } from "./components/ChatPanel";
import { ReportView } from "./components/ReportView";

const ACCEPTED_EXTENSIONS = [".pptx", ".pdf", ".docx", ".md", ".png", ".jpg", ".jpeg"];
const MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024;
const AUTHOR_URL = "https://github.com/SiriZhao";

const LLM_PRESETS: Record<string, { baseUrl: string; model: string; label: string; hint: string }> = {
  deepseek: {
    baseUrl: "https://api.deepseek.com",
    model: "deepseek-v4-flash",
    label: "DeepSeek",
    hint: "推荐使用 deepseek-v4-flash。deepseek-chat 和 deepseek-reasoner 作为兼容模型名保留。",
  },
  openai: {
    baseUrl: "https://api.openai.com/v1",
    model: "gpt-4o-mini",
    label: "OpenAI",
    hint: "适合多语言材料和更自然的总结表达。",
  },
  qwen: {
    baseUrl: "https://dashscope.aliyuncs.com/compatible-mode/v1",
    model: "qwen-plus",
    label: "通义千问 / Qwen",
    hint: "适合中文课件、教材和笔记，可使用 DashScope 兼容接口。",
  },
  custom_openai_compatible: {
    baseUrl: "",
    model: "",
    label: "OpenAI-compatible 自定义接口",
    hint: "可填写私有网关、OpenRouter 或其他兼容 Chat Completions 的接口。",
  },
};

const PROGRESS_STEPS = ["正在上传", "正在提取文本", "正在识别扫描内容", "正在生成复习资料", "正在导出"];

type MaterialCategory = "slides" | "exam" | "document" | "image";

export default function App() {
  const settingsRef = useRef<HTMLDetailsElement>(null);
  const llmRef = useRef<HTMLFieldSetElement>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [courseName, setCourseName] = useState("期末复习资料包");
  const [ocrConfig, setOcrConfig] = useState<OCRConfig>({
    provider: "rapidocr",
    api_url: "",
    api_key: "",
    secret_key: "",
    language: "chi_sim+eng",
  });
  const [llmConfig, setLlmConfig] = useState<LLMConfig>({
    provider: "deepseek",
    model: "deepseek-v4-flash",
    base_url: "https://api.deepseek.com",
    api_key: "",
    enabled: false,
  });
  const [result, setResult] = useState<GenerateReviewResponse | null>(null);
  const [status, setStatus] = useState("添加学习材料后，点击开始生成复习资料包。");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState<ExportFormat | null>(null);
  const [progress, setProgress] = useState(0);
  const [progressLabel, setProgressLabel] = useState("准备就绪");
  const [aboutOpen, setAboutOpen] = useState(false);
  const [llmTest, setLlmTest] = useState<LLMTestResponse | null>(null);
  const [testingLLM, setTestingLLM] = useState(false);
  const [configSaved, setConfigSaved] = useState(false);

  const progressStepIndex = useMemo(
    () => Math.min(Math.floor(progress / 20), PROGRESS_STEPS.length - 1),
    [progress],
  );

  const categoryCounts = useMemo(() => {
    return files.reduce<Record<MaterialCategory, number>>(
      (counts, file) => {
        counts[getMaterialCategory(file)] += 1;
        return counts;
      },
      { slides: 0, exam: 0, document: 0, image: 0 },
    );
  }, [files]);

  function openLLMSettings() {
    if (settingsRef.current) {
      settingsRef.current.open = true;
    }
    window.setTimeout(() => llmRef.current?.scrollIntoView({ behavior: "smooth", block: "center" }), 0);
  }

  async function runLLMTest() {
    setTestingLLM(true);
    setLlmTest(null);
    try {
      const response = await testLLMConnection(normalizeLlmConfig(llmConfig));
      setLlmTest(response);
    } finally {
      setTestingLLM(false);
    }
  }

  function saveLLMConfig() {
    window.localStorage.setItem("examforge-llm-config", JSON.stringify(normalizeLlmConfig(llmConfig)));
    setConfigSaved(true);
    window.setTimeout(() => setConfigSaved(false), 3000);
  }

  function addFiles(nextFiles: FileList | File[]) {
    const incoming = Array.from(nextFiles);
    const valid = incoming.filter(
      (file) => isAcceptedFile(file.name) && file.size <= MAX_FILE_SIZE_BYTES,
    );
    const rejected = incoming.length - valid.length;
    setFiles((current) => {
      const keys = new Set(current.map((file) => `${file.name}-${file.size}`));
      return [...current, ...valid.filter((file) => !keys.has(`${file.name}-${file.size}`))];
    });
    setError(
      rejected > 0
        ? `已跳过 ${rejected} 个文件。请使用 50MB 以内的 PPTX、PDF、DOCX、MD、PNG、JPG 或 JPEG 文件。`
        : "",
    );
  }

  function removeFile(index: number) {
    setFiles((current) => current.filter((_, itemIndex) => itemIndex !== index));
  }

  async function handleGenerate(format: ExportFormat = "md") {
    if (files.length === 0) {
      setError("请先添加至少一个课件、文档、图片或往年题文件。");
      return;
    }

    setLoading(true);
    setExporting(format);
    setProgress(5);
    setProgressLabel("正在上传");
    setError("");
    setStatus("正在上传文件到本地后端...");

    try {
      const uploadResult = await uploadFiles(files);
      setProgress(10);
      setProgressLabel("任务已提交");
      setStatus("扫描版 PDF 可能需要更长时间，请保持页面打开。");

      const job = await createGenerateReviewJob({
        files: uploadResult.files.map((file) => file.saved_filename),
        export_format: format,
        export_formats: ["md", "docx", "pdf"],
        title: courseName || "期末复习资料包",
        course_name: courseName || "期末复习资料包",
        ocr_config: normalizeOcrConfig(ocrConfig),
        llm_config: normalizeLlmConfig(llmConfig),
      });

      let generated: GenerateReviewResponse | null = null;
      while (!generated) {
        await sleep(1000);
        const jobStatus = await getGenerateReviewJob(job.job_id);
        setProgress(jobStatus.progress);
        setProgressLabel(translateJobMessage(jobStatus.message));
        setStatus(translateJobMessage(jobStatus.message));

        if (jobStatus.status === "completed" && jobStatus.result) {
          generated = jobStatus.result;
          break;
        }
        if (jobStatus.status === "failed") {
          throw new Error(jobStatus.error || "生成失败。");
        }
      }

      setProgress(100);
      setProgressLabel("已完成");
      setResult(generated);
      setStatus("复习资料包已生成，Markdown、Word、PDF 和 Anki CSV 已准备好。");
    } catch (requestError) {
      const message = requestError instanceof Error ? requestError.message : "生成失败。";
      setError(`${message} 建议：检查后端是否运行、移除损坏文件，或将 OCR 切换为 RapidOCR。`);
      setStatus("生成失败。");
      setProgress(100);
      setProgressLabel("生成失败");
    } finally {
      setLoading(false);
      setExporting(null);
    }
  }

  return (
    <main className="app-shell">
      <header className="hero">
        <div className="hero-copy">
          <p className="brand-line">
            <strong>ExamForge AI</strong>
            <span>期末复习资料生成器</span>
          </p>
          <h1>把杂乱的课程资料，整理成可直接复习的冲刺资料包</h1>
          <p className="intro">
            上传课件、笔记、教材、扫描试卷和往年题，ExamForge AI 会自动提取重点、分析高频考点、生成模拟卷、Anki 卡片和考前冲刺计划。
          </p>
          <div className="hero-tags" aria-label="产品亮点">
            <span>无需 API Key 也可使用</span>
            <span>支持扫描版试卷</span>
            <span>支持 Markdown / Word / PDF / Anki 导出</span>
          </div>
        </div>
        <div className="hero-card">
          <strong>为期末考试而生</strong>
          <span>这不是普通的文档问答工具。它会帮你生成章节优先级、高频考点、冲刺计划、模拟题和记忆卡片。</span>
        </div>
      </header>

      <section className="workspace">
        <section className="panel control-panel">
          <div className="section-title">
            <p className="eyebrow">创建复习资料包</p>
            <h2>学习材料</h2>
            <p>新用户可以直接使用默认的规则模式生成资料。OCR 和大模型设置均为可选高级功能。</p>
          </div>

          <label className="field">
            <span>课程或考试名称</span>
            <input
              value={courseName}
              onChange={(event) => setCourseName(event.target.value)}
              placeholder="例如：植物生物学导论"
            />
          </label>

          <FileDropzone files={files} addFiles={addFiles} removeFile={removeFile} counts={categoryCounts} />

          <details className="advanced-settings" ref={settingsRef}>
            <summary>
              <span>高级设置</span>
              <small>OCR 和大模型设置</small>
            </summary>
            <ConfigGrid
              llmRef={llmRef}
              ocrConfig={ocrConfig}
              setOcrConfig={setOcrConfig}
              llmConfig={llmConfig}
              setLlmConfig={setLlmConfig}
              llmTest={llmTest}
              testingLLM={testingLLM}
              configSaved={configSaved}
              onTestLLM={runLLMTest}
              onSaveLLM={saveLLMConfig}
            />
          </details>

          <div className="quality-guide info-box">
            <strong>想要更准确的复习资料？</strong>
            <p>
              规则模式无需 API Key，适合快速生成基础报告；如果你希望得到更系统的章节总结、更准确的高频考点、更完整的模拟卷和 Anki 卡片，建议开启大模型增强。
            </p>
            <button type="button" className="secondary accent" onClick={openLLMSettings}>
              配置大模型
            </button>
          </div>

          <button className="primary-action" type="button" onClick={() => handleGenerate("md")} disabled={loading}>
            {loading ? "正在生成..." : "开始生成"}
          </button>

          <ProgressBar
            value={progress}
            label={progressLabel}
            step={PROGRESS_STEPS[progressStepIndex]}
            failed={Boolean(error)}
          />
          <p className="status-text">{status}</p>
          {error && <p className="error-text">{error}</p>}
        </section>

        <ReportView
          result={result}
          onExport={handleGenerate}
          exporting={exporting}
          onOpenLLMSettings={openLLMSettings}
          onTestLLM={runLLMTest}
        />
      </section>

      {result && <ChatPanel reviewReport={result.review_report} />}

      <footer className="app-footer">
        <span>© 2026 SiriZhao｜开源地址：</span>
        <a href={AUTHOR_URL} target="_blank" rel="noreferrer">github.com/SiriZhao</a>
        <button type="button" className="link-button" onClick={() => setAboutOpen(true)}>关于</button>
      </footer>

      {aboutOpen && <AboutDialog onClose={() => setAboutOpen(false)} />}
    </main>
  );
}

function FileDropzone({
  files,
  addFiles,
  removeFile,
  counts,
}: {
  files: File[];
  addFiles: (files: FileList | File[]) => void;
  removeFile: (index: number) => void;
  counts: Record<MaterialCategory, number>;
}) {
  const [dragging, setDragging] = useState(false);

  return (
    <section className="upload-card">
      <label
        className={`dropzone ${dragging ? "is-dragging" : ""}`}
        onDragOver={(event) => {
          event.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(event) => {
          event.preventDefault();
          setDragging(false);
          addFiles(event.dataTransfer.files);
        }}
      >
        <span className="upload-icon">文件</span>
        <strong>拖拽文件到这里，或点击选择文件</strong>
        <span>支持 PPTX、PDF、DOCX、MD、PNG、JPG、JPEG，单个文件最大 50MB。</span>
        <input hidden multiple type="file" accept={ACCEPTED_EXTENSIONS.join(",")} onChange={(event) => addFiles(event.target.files ?? [])} />
      </label>

      <div className="category-pills" aria-label="已上传材料分类">
        <CategoryPill label="课件" value={counts.slides} />
        <CategoryPill label="往年题" value={counts.exam} />
        <CategoryPill label="文档" value={counts.document} />
        <CategoryPill label="图片" value={counts.image} />
      </div>

      <div className="file-list">
        {files.length === 0 ? (
          <p className="helper-text">建议上传课件或教材，再搭配至少一份往年题或扫描试卷，分析会更准确。</p>
        ) : (
          files.map((file, index) => (
            <div className="file-row" key={`${file.name}-${file.size}`}>
              <span className="file-type">{getFileBadge(file)}</span>
              <span className="file-name">{file.name}</span>
              <span className="material-kind">{categoryLabel(getMaterialCategory(file))}</span>
              <small>{formatSize(file.size)}</small>
              <button type="button" aria-label={`移除 ${file.name}`} onClick={() => removeFile(index)}>
                清空
              </button>
            </div>
          ))
        )}
      </div>
    </section>
  );
}

function ConfigGrid({
  llmRef,
  ocrConfig,
  setOcrConfig,
  llmConfig,
  setLlmConfig,
  llmTest,
  testingLLM,
  configSaved,
  onTestLLM,
  onSaveLLM,
}: {
  llmRef: RefObject<HTMLFieldSetElement | null>;
  ocrConfig: OCRConfig;
  setOcrConfig: (value: OCRConfig) => void;
  llmConfig: LLMConfig;
  setLlmConfig: (value: LLMConfig) => void;
  llmTest: LLMTestResponse | null;
  testingLLM: boolean;
  configSaved: boolean;
  onTestLLM: () => void;
  onSaveLLM: () => void;
}) {
  const currentPreset = LLM_PRESETS[llmConfig.provider ?? "deepseek"] ?? LLM_PRESETS.deepseek;

  function chooseProvider(provider: string) {
    const preset = LLM_PRESETS[provider] ?? LLM_PRESETS.deepseek;
    setLlmConfig({
      ...llmConfig,
      provider,
      base_url: llmConfig.base_url && provider === llmConfig.provider ? llmConfig.base_url : preset.baseUrl,
      model: llmConfig.model && provider === llmConfig.provider ? llmConfig.model : preset.model,
    });
  }

  return (
    <div className="config-grid">
      <fieldset>
        <legend>OCR 设置</legend>
        <p className="helper-text">用于图片和扫描版 PDF。文字版 PDF、PPTX 和 DOCX 通常不需要 OCR。</p>
        <label className="field">
          <span>OCR 服务</span>
          <select value={ocrConfig.provider} onChange={(event) => setOcrConfig({ ...ocrConfig, provider: event.target.value as OCRConfig["provider"] })}>
            <option value="rapidocr">RapidOCR，本地识别，无需密钥</option>
            <option value="baidu_ocr">百度 OCR，云端识别</option>
            <option value="local_tesseract">本地 Tesseract</option>
            <option value="custom_api">自定义 OCR 接口</option>
            <option value="openai_vision">OpenAI 视觉识别</option>
          </select>
        </label>
      </fieldset>

      <fieldset ref={llmRef}>
        <legend>大模型增强</legend>
        <p className="helper-text">规则模式无需 API Key，适合快速生成基础报告；开启大模型增强后，可以提升章节总结、高频考点、模拟卷、Anki 卡片和冲刺计划的质量。</p>
        <label className="checkbox-row">
          <input checked={Boolean(llmConfig.enabled)} type="checkbox" onChange={(event) => setLlmConfig({ ...llmConfig, enabled: event.target.checked })} />
          <span>启用大模型增强</span>
        </label>
        <label className="field">
          <span>服务商</span>
          <select value={llmConfig.provider ?? "deepseek"} onChange={(event) => chooseProvider(event.target.value)}>
            {Object.entries(LLM_PRESETS).map(([value, preset]) => (
              <option key={value} value={value}>{preset.label}</option>
            ))}
          </select>
        </label>
        <p className="provider-hint">{currentPreset.hint}</p>
        <div className="settings-grid">
          <label className="field">
            <span>API Key</span>
            <input type="password" value={llmConfig.api_key ?? ""} onChange={(event) => setLlmConfig({ ...llmConfig, api_key: event.target.value })} placeholder="请输入 API Key，仅保存在本地配置中" />
          </label>
          <label className="field">
            <span>Base URL</span>
            <input value={llmConfig.base_url ?? ""} onChange={(event) => setLlmConfig({ ...llmConfig, base_url: event.target.value })} placeholder={currentPreset.baseUrl} />
          </label>
          <label className="field">
            <span>模型名称</span>
            <input value={llmConfig.model ?? ""} onChange={(event) => setLlmConfig({ ...llmConfig, model: event.target.value })} placeholder={currentPreset.model} list="deepseek-models" />
            <datalist id="deepseek-models">
              <option value="deepseek-v4-flash" />
              <option value="deepseek-v4-pro" />
              <option value="deepseek-chat" />
              <option value="deepseek-reasoner" />
            </datalist>
          </label>
        </div>
        <div className="quick-actions">
          <button type="button" className="secondary accent" onClick={onTestLLM} disabled={testingLLM}>
            {testingLLM ? "正在测试大模型连接..." : "测试大模型连接"}
          </button>
          <button type="button" className="secondary" onClick={onSaveLLM}>保存大模型配置</button>
        </div>
        {configSaved && <p className="success-box">配置已保存到本地。请注意不要将 API Key 提交到 GitHub。</p>}
        {llmTest?.ok && <p className="success-box">{llmTest.message || "大模型连接成功，可以重新生成复习资料。"}</p>}
        {llmTest && !llmTest.ok && llmTest.error && (
          <div className="warning-box">
            <strong>测试失败：{llmTest.error.code}</strong>
            <p>{llmTest.error.message}</p>
            <p>{llmTest.error.suggestion}</p>
          </div>
        )}
      </fieldset>
    </div>
  );
}

function CategoryPill({ label, value }: { label: string; value: number }) {
  return <span className={value > 0 ? "category-pill active" : "category-pill"}>{label} <strong>{value}</strong></span>;
}

function ProgressBar({ value, label, step, failed }: { value: number; label: string; step: string; failed: boolean }) {
  return (
    <div className={failed ? "progress-wrap failed" : "progress-wrap"} aria-live="polite">
      <div className="progress-meta"><span>{step}</span><strong>{Math.round(value)}%</strong></div>
      <div className="progress-track"><div className="progress-fill" style={{ width: `${value}%` }} /></div>
      <small>{label}</small>
      <small>OCR 提醒：扫描版 PDF 会逐页渲染和识别，因此耗时更长。</small>
      {failed && <small>可尝试减少文件数量、切换到 RapidOCR，或重新运行 start.bat 启动后端。</small>}
    </div>
  );
}

function AboutDialog({ onClose }: { onClose: () => void }) {
  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <section className="about-dialog" role="dialog" aria-modal="true" aria-label="关于 ExamForge AI" onClick={(event) => event.stopPropagation()}>
        <div className="section-header compact">
          <h2>关于</h2>
          <button type="button" className="secondary" onClick={onClose}>关闭</button>
        </div>
        <dl className="about-list">
          <div><dt>产品名称</dt><dd>ExamForge AI</dd></div>
          <div><dt>中文名称</dt><dd>期末复习资料生成器</dd></div>
          <div><dt>作者</dt><dd>SiriZhao</dd></div>
          <div><dt>GitHub</dt><dd><a href={AUTHOR_URL} target="_blank" rel="noreferrer">https://github.com/SiriZhao</a></dd></div>
        </dl>
        <p className="summary">一个面向大学生期末复习场景的本地 AI 复习资料生成工具，可将课件、教材、笔记、扫描试卷和往年题整理为复习资料包、模拟卷和记忆卡片。</p>
      </section>
    </div>
  );
}

function getMaterialCategory(file: File): MaterialCategory {
  const name = file.name.toLowerCase();
  if (name.endsWith(".pptx")) return "slides";
  if (/\b(exam|paper|past|quiz|test|mock)\b/.test(name) || /试卷|真题|往年|考试/.test(name)) return "exam";
  if (name.endsWith(".png") || name.endsWith(".jpg") || name.endsWith(".jpeg")) return "image";
  return "document";
}

function categoryLabel(category: MaterialCategory) {
  return { slides: "课件", exam: "往年题", document: "文档", image: "图片" }[category];
}

function getFileBadge(file: File) {
  const extension = file.name.split(".").pop()?.toUpperCase() || "文件";
  return extension === "JPEG" ? "JPG" : extension;
}

function isAcceptedFile(name: string) {
  const lower = name.toLowerCase();
  return ACCEPTED_EXTENSIONS.some((extension) => lower.endsWith(extension));
}

function formatSize(size: number) {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / 1024 / 1024).toFixed(1)} MB`;
}

function normalizeOcrConfig(config: OCRConfig): OCRConfig {
  return {
    ...config,
    api_url: config.api_url || null,
    api_key: config.api_key || null,
    secret_key: config.secret_key || null,
    language: config.language || "chi_sim+eng",
  };
}

function normalizeLlmConfig(config: LLMConfig): LLMConfig {
  const provider = config.provider || "deepseek";
  const preset = LLM_PRESETS[provider] ?? LLM_PRESETS.deepseek;
  return {
    provider,
    model: config.model || preset.model || null,
    base_url: config.base_url || preset.baseUrl || null,
    api_key: config.api_key || null,
    enabled: Boolean(config.enabled),
  };
}

function translateJobMessage(message: string) {
  const lower = message.toLowerCase();
  if (lower.includes("upload")) return "正在上传";
  if (lower.includes("ocr")) return "正在识别扫描内容";
  if (lower.includes("extract") || lower.includes("parse")) return "正在提取文本";
  if (lower.includes("export")) return "正在导出";
  if (lower.includes("done") || lower.includes("complete")) return "已完成";
  if (lower.includes("fail")) return "生成失败";
  return message || "正在处理";
}

function sleep(ms: number) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}
