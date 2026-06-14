import { useState } from "react";

import { downloadFilename, downloadUrl, type ExportFormat, type GenerateReviewResponse, type OptimizationGoal } from "../api/client";
import { MarkdownView } from "./MarkdownView";

type ReportViewProps = {
  result: GenerateReviewResponse | null;
  onExport: (format: ExportFormat) => void;
  exporting: ExportFormat | null;
  onOpenLLMSettings?: () => void;
  onTestLLM?: () => void;
  optimizationGoal?: OptimizationGoal;
  optimizationOptions?: Array<{ value: OptimizationGoal; label: string }>;
  optimizing?: boolean;
  onOptimizationGoalChange?: (value: OptimizationGoal) => void;
  onReoptimize?: () => void;
};

type ReportTab = "overview" | "priority" | "topics" | "questionTypes" | "mock" | "anki" | "markdown";

const TABS: Array<{ id: ReportTab; label: string }> = [
  { id: "overview", label: "总览" },
  { id: "priority", label: "复习单元" },
  { id: "topics", label: "高频考点" },
  { id: "questionTypes", label: "题型分析" },
  { id: "mock", label: "模拟卷" },
  { id: "anki", label: "Anki 卡片" },
  { id: "markdown", label: "Markdown 预览" },
];

export function ReportView({
  result,
  onExport,
  exporting,
  onOpenLLMSettings = () => undefined,
  onTestLLM = () => undefined,
  optimizationGoal = "memorization",
  optimizationOptions = [],
  optimizing = false,
  onOptimizationGoalChange = () => undefined,
  onReoptimize = () => undefined,
}: ReportViewProps) {
  const [activeTab, setActiveTab] = useState<ReportTab>("overview");
  const [showFallbackNotice, setShowFallbackNotice] = useState(true);

  if (!result) {
    return (
      <section className="panel empty-state">
        <p className="eyebrow">生成结果</p>
        <h2>复习资料包将在这里生成</h2>
        <p>
          生成后，这里会展示完整的复习报告，包括复习导览、知识结构、高频考点、模拟卷、Anki 卡片和 Markdown 预览。
        </p>
        <div className="empty-tips">
          <span>上传往年题后，可以获得更准确的高频考点和题型线索。</span>
          <span>本地整理模式无需 API Key，也可以生成基础安全底稿。</span>
        </div>
      </section>
    );
  }

  const report = result.review_report;

  return (
    <section className="panel result-panel">
      <div className="section-header">
        <div>
          <p className="eyebrow">生成结果</p>
          <h2>{report.title}</h2>
          <p className="muted">生成时间：{report.generated_at}</p>
        </div>
        <div className="download-actions">
          {(["md", "docx", "pdf"] as ExportFormat[]).map((format) =>
            result.download_links[format] ? (
              <a
                key={format}
                className="secondary"
                href={downloadUrl(result.download_links[format] || "")}
                download={downloadFilename(result.download_links[format] || "")}
                target="_blank"
                rel="noreferrer"
              >
                下载 {format.toUpperCase()}
              </a>
            ) : (
              <button key={format} className="secondary" type="button" onClick={() => onExport(format)} disabled={exporting !== null}>
                {exporting === format ? "正在导出..." : `导出 ${format.toUpperCase()}`}
              </button>
            ),
          )}
          {result.anki_csv_download_path && (
            <a
              className="secondary accent"
              href={downloadUrl(result.anki_csv_download_path)}
              download={downloadFilename(result.anki_csv_download_path)}
              target="_blank"
              rel="noreferrer"
            >
              下载 Anki CSV
            </a>
          )}
        </div>
      </div>

      <ReportSourceNotice
        result={result}
        visible={showFallbackNotice}
        onOpenLLMSettings={onOpenLLMSettings}
        onTestLLM={onTestLLM}
        onDismiss={() => setShowFallbackNotice(false)}
        onRegenerate={() => onExport("md")}
      />

      <div className="quick-actions">
        <label className="field compact-field">
          <span>重新优化方向</span>
          <select value={optimizationGoal} onChange={(event) => onOptimizationGoalChange(event.target.value as OptimizationGoal)}>
            {optimizationOptions.map((item) => (
              <option key={item.value} value={item.value}>{item.label}</option>
            ))}
          </select>
        </label>
        <button type="button" className="secondary accent" onClick={onReoptimize} disabled={optimizing}>
          {optimizing ? "正在优化..." : "重新优化这份资料"}
        </button>
      </div>

      <QualityPanel result={result} />
      <GenerationSummaryPanel result={result} />
      <MockExamBasisNotice result={result} />

      {report.insufficient_materials.length > 0 && (
        <div className="warning-box">
          <strong>材料内容较少</strong>
          <p>当前上传资料提取到的文本较少，生成结果可能不够完整。建议补充课件、教材、笔记或往年题。</p>
          <ul>
            {report.insufficient_materials.map((item, index) => (
              <li key={`${item}-${index}`}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {report.past_exam_analysis.detected_files.length === 0 && (
        <div className="info-box">
          <strong>建议上传往年题</strong>
          <p>上传往年题后，系统可以更准确地分析高频考点和题型分布。</p>
        </div>
      )}

      <div className="report-tabs" role="tablist" aria-label="报告模块">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            className={activeTab === tab.id ? "tab-button active" : "tab-button"}
            type="button"
            role="tab"
            aria-selected={activeTab === tab.id}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "overview" && <OverviewTab result={result} />}
      {activeTab === "priority" && <PriorityTab result={result} />}
      {activeTab === "topics" && <TopicsTab result={result} />}
      {activeTab === "questionTypes" && <QuestionTypesPanel result={result} />}
      {activeTab === "mock" && <MockExamTab result={result} />}
      {activeTab === "anki" && <AnkiTab result={result} />}
      {activeTab === "markdown" && <MarkdownView markdown={result.markdown} />}
    </section>
  );
}

function ReportSourceNotice({
  result,
  visible,
  onOpenLLMSettings,
  onTestLLM,
  onDismiss,
  onRegenerate,
}: {
  result: GenerateReviewResponse;
  visible: boolean;
  onOpenLLMSettings: () => void;
  onTestLLM: () => void;
  onDismiss: () => void;
  onRegenerate: () => void;
}) {
  const source = result.report_source ?? "rule_based";
  const status = result.llm_status ?? "disabled";
  const chunked = result.llm_context_strategy === "chunked";

  if (source === "local_safe_draft_with_ai_outline" && visible) {
    return (
      <div className="llm-fallback-box">
        <strong>当前报告来源：本地安全底稿 + AI 专题命名</strong>
        <p>
          完整 AI 深度整理未成功，但系统已使用轻量 AI 调用优化专题名称和复习结构，避免公式碎片或 OCR 噪声作为章节标题。
        </p>
        <div className="quick-actions">
          <button type="button" className="secondary accent" onClick={onOpenLLMSettings}>去配置大模型</button>
          <button type="button" className="secondary" onClick={onTestLLM}>测试连接</button>
          <button type="button" className="secondary" onClick={onDismiss}>继续查看安全底稿</button>
          <button type="button" className="secondary" onClick={onRegenerate}>重新生成</button>
        </div>
      </div>
    );
  }

  if (status === "success" || source === "llm_enhanced" || source === "llm_markdown_fallback") {
    const markdownFallback = source === "llm_markdown_fallback";
    return (
      <div className="success-box">
        <strong>当前报告来源：{markdownFallback ? "AI Markdown 兼容模式" : chunked ? "分块 AI 深度整理" : "AI 深度整理"}</strong>
        <p>
          {markdownFallback
            ? "大模型返回了 Markdown 格式内容，系统已自动兼容并完成质量校验与导出处理。"
            : chunked
            ? "资料较长，系统已先分块理解，再进行全局重组，尽量保留可复习信息并生成完整资料包。"
            : "系统已结合材料证据、OCR 结果、题目线索和大模型，对章节/专题、考点、题型、模拟卷和 Anki 卡片进行重组整理。"}
        </p>
      </div>
    );
  }

  if ((status === "failed" || source === "rule_based_with_llm_failed") && visible) {
    const error = result.llm_error;
    const qualityFailed = error?.code === "QUALITY_FAILED";
    return (
      <div className="llm-fallback-box">
        <strong>当前报告来源：本地安全底稿</strong>
        <p>
          {qualityFailed
            ? "系统检测到 AI 输出存在内容过短、缺少题目、缺少答案、乱码或空泛等问题，已自动回退到更稳定的本地安全底稿。"
            : "大模型增强未成功，系统已保留本地生成的可用复习资料。建议检查大模型配置后重新生成，以获得更高质量结果。"}
        </p>
        {error && (
          <dl className="error-detail">
            <div><dt>错误类型</dt><dd>{error.code}</dd></div>
            <div><dt>错误说明</dt><dd>{error.message}</dd></div>
            <div><dt>修复建议</dt><dd>{error.suggestion}</dd></div>
            <div><dt>服务商</dt><dd>{error.provider || "未提供"}</dd></div>
            <div><dt>模型</dt><dd>{error.model || "未提供"}</dd></div>
          </dl>
        )}
        <div className="quick-actions">
          <button type="button" className="secondary accent" onClick={onOpenLLMSettings}>去配置大模型</button>
          <button type="button" className="secondary" onClick={onTestLLM}>测试连接</button>
          <button type="button" className="secondary" onClick={onDismiss}>继续查看安全底稿</button>
          <button type="button" className="secondary" onClick={onRegenerate}>重新生成</button>
        </div>
      </div>
    );
  }

  return (
    <div className="info-box">
      <strong>当前报告来源：本地整理模式</strong>
      <p>
        系统已基于 OCR、关键词、题目识别和材料结构生成基础复习资料。若希望获得更自然的章节重组、更贴近考试的题型归纳和更高质量的模拟题，建议开启大模型增强。
      </p>
      <button type="button" className="secondary accent" onClick={onOpenLLMSettings}>开启大模型增强</button>
    </div>
  );
}

function QualityPanel({ result }: { result: GenerateReviewResponse }) {
  const quality = result.review_report.quality;
  if (!quality) return null;
  const items = [
    ["资料完整度", quality.material_completeness_score],
    ["考点覆盖度", quality.topic_coverage_score],
    ["模拟题质量", quality.mock_exam_quality_score],
    ["Anki 可用性", quality.anki_quality_score],
    ["导出就绪度", quality.export_readiness_score],
    ["证据整合度", quality.evidence_integration_score],
  ] as const;
  return (
    <section className="mini-section">
      <h3>生成质量评分：{quality.quality_score}/100</h3>
      <div className="feature-grid">
        {items.map(([label, value]) => <MetricCard key={label} label={label} value={value} />)}
      </div>
    </section>
  );
}

function GenerationSummaryPanel({ result }: { result: GenerateReviewResponse }) {
  const summary = result.generation_summary;
  if (!summary) return null;
  return (
    <section className="mini-section">
      <h3>本次生成过程</h3>
      <ul>
        <li>已处理 {summary.files_processed} 个文件，合计 {summary.pages_total} 页。</li>
        <li>文字层提取 {summary.pages_text_extracted} 页，OCR 识别 {summary.pages_ocr_processed} 页，OCR 缓存命中 {summary.ocr_cache_hits} 次。</li>
        <li>构建 {summary.evidence_chunks} 个材料证据块，识别 {summary.detected_study_units} 个复习单元候选、{summary.detected_question_types} 类题型线索。</li>
        <li>生成 {summary.mock_questions_count} 道模拟题、{summary.anki_cards_count} 张 Anki 卡片；最终来源：{summary.final_report_source}。</li>
      </ul>
    </section>
  );
}

function MockExamBasisNotice({ result }: { result: GenerateReviewResponse }) {
  const report = result.review_report;
  const conservative = report.overview?.mock_exam_mode === "conservative";
  const hasPastExam = report.past_exam_analysis.detected_files.length > 0;
  if (conservative) {
    return (
      <div className="warning-box">
        <strong>模拟卷依据：保守练习题模式</strong>
        <p>当前材料不足以稳定还原真实题型，系统已生成保守练习题。建议上传更多往年题或开启 AI 深度整理，以获得更贴近考试的模拟卷。</p>
      </div>
    );
  }
  if (hasPastExam) {
    return (
      <div className="success-box">
        <strong>模拟卷依据：已参考上传的往年题型线索生成</strong>
        <p>系统会优先使用真实题干结构、题型分布和高频考点来组织模拟题，避免固定模板凑题。</p>
      </div>
    );
  }
  return (
    <div className="info-box">
      <strong>模拟卷依据：基于课程材料生成</strong>
      <p>当前未检测到明确往年题。上传往年试卷并开启 AI 深度整理后，题型归纳和模拟卷质量通常会明显提升。</p>
    </div>
  );
}

function QuestionTypesPanel({ result }: { result: GenerateReviewResponse }) {
  const items = result.review_report.question_types ?? [];
  if (items.length === 0) return null;
  return (
    <section className="mini-section">
      <h3>题型分析</h3>
      {items.map((item) => (
        <article key={item.name} className="question-type-card">
          <div className="section-header compact">
            <h4>{item.name}</h4>
            <span className="score-pill">{item.confidence ?? 70}</span>
          </div>
          <p>{item.evidence || (item.is_from_past_exam ? "来自往年题线索" : "根据课程材料推测的练习题型")}</p>
          {item.features?.length > 0 && <BadgeList items={item.features} />}
          <p className="muted">{item.answer_strategy}</p>
          {item.related_topics?.length > 0 && <p className="muted">相关考点：{item.related_topics.join("、")}</p>}
          {item.sample_questions?.length > 0 && <p className="muted">样例题：{item.sample_questions.join("；")}</p>}
          {item.practice_suggestions && <p className="muted">练习方式：{item.practice_suggestions}</p>}
        </article>
      ))}
    </section>
  );
}

function OverviewTab({ result }: { result: GenerateReviewResponse }) {
  const report = result.review_report;
  return (
    <div className="tab-panel">
      <p className="summary">{report.summary}</p>
      <div className="feature-grid">
        <MetricCard label="识别出的往年题" value={report.past_exam_analysis.detected_files.length} />
        <MetricCard label="高频考点" value={report.past_exam_analysis.high_frequency_topics.length || report.high_frequency_points.length} />
        <MetricCard label="模拟题数量" value={report.mock_exam.questions.length} />
        <MetricCard label="Anki 卡片" value={report.anki_cards.length} />
      </div>
      <section className="quick-list">
        <h3>推荐复习顺序</h3>
        <ol>
          {report.review_order.slice(0, 6).map((item) => (
            <li key={item.chapter}>
              <strong>{item.chapter}</strong>：{item.importance}/100
              <span className="list-note">{item.reason}</span>
            </li>
          ))}
        </ol>
      </section>
      <section className="quick-list">
        <h3>考前冲刺计划</h3>
        <div className="sprint-grid">
          {report.sprint_plans.map((plan) => (
            <article key={plan.days} className="mini-section">
              <h4>{plan.title}</h4>
              <ul>
                {plan.schedule.map((item, index) => (
                  <li key={`${plan.days}-${index}`}>{item}</li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}

function PriorityTab({ result }: { result: GenerateReviewResponse }) {
  const report = result.review_report;
  if (report.study_units?.length) {
    return (
      <div className="tab-panel">
        <h3>知识结构与复习单元</h3>
        {report.study_units.map((unit) => (
          <article key={unit.name} className="mini-section">
            <h4>{unit.name} <span className="score-pill">{unit.priority}</span></h4>
            <p>{unit.reason}</p>
            <p className="muted">{unit.how_to_review}</p>
          </article>
        ))}
      </div>
    );
  }

  return (
    <div className="tab-panel">
      <h3>章节优先级评分</h3>
      <div className="table-wrap">
        <table>
          <thead>
            <tr><th>章节/专题</th><th>重要度</th><th>材料命中</th><th>往年题命中</th><th>题型</th></tr>
          </thead>
          <tbody>
            {report.chapters.map((chapter) => (
              <tr key={chapter.chapter}>
                <td>{chapter.chapter}</td>
                <td><span className="score-pill">{chapter.importance}</span></td>
                <td>{chapter.material_frequency}</td>
                <td>{chapter.past_exam_frequency}</td>
                <td>{chapter.question_types.join("、") || "暂无"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function TopicsTab({ result }: { result: GenerateReviewResponse }) {
  const report = result.review_report;
  return (
    <div className="tab-panel">
      <p className="summary">{report.past_exam_analysis.summary}</p>
      {(report.question_types?.length ?? 0) > 0 && (
        <section className="quick-list">
          <h3>题型归纳</h3>
          {(report.question_types ?? []).map((item) => (
            <article key={item.name} className="mini-section">
              <h4>{item.name}</h4>
              <p>{item.evidence}</p>
              <p className="muted">{item.answer_strategy}</p>
            </article>
          ))}
        </section>
      )}
      <div className="table-wrap">
        <table>
          <thead>
            <tr><th>考点</th><th>章节/专题</th><th>频次</th><th>题型</th></tr>
          </thead>
          <tbody>
            {report.past_exam_analysis.high_frequency_topics.map((topic) => (
              <tr key={`${topic.chapter}-${topic.topic}`}>
                <td>{topic.topic}</td>
                <td>{topic.chapter}</td>
                <td>{topic.frequency}</td>
                <td>{topic.question_types.join("、") || "未知"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function MockExamTab({ result }: { result: GenerateReviewResponse }) {
  return (
    <div className="mock-exam-list tab-panel">
      <div className="section-header compact">
        <h3>模拟卷与参考答案</h3>
        <span className="muted">题目、答案、解析和来源依据会一起导出。</span>
      </div>
      {result.review_report.mock_exam.questions.map((question, index) => (
        <article key={`${question.question_type}-${index}`} className="mock-question-card">
          <div className="mock-question-meta">
            <span className="question-index">{index + 1}</span>
            <strong>{question.type || question.question_type}</strong>
            <span>{question.difficulty || "中等"}</span>
          </div>
          <p className="question-stem">{question.question}</p>
          {(question.options ?? []).length > 0 && (
            <ol className="option-list">
              {(question.options ?? []).map((option, optionIndex) => (
                <li key={`${option}-${optionIndex}`}>{option}</li>
              ))}
            </ol>
          )}
          <div className="answer-block">
            <strong>参考答案</strong>
            <p>{question.answer || "—"}</p>
          </div>
          <div className="answer-block">
            <strong>解析</strong>
            <p>{question.explanation || "—"}</p>
          </div>
          <div className="mock-footnotes">
            <span>相关考点：{question.related_topic || question.concept || "—"}</span>
            <span>来源依据：{question.source_basis || question.source_hint || "基于材料生成"}</span>
          </div>
        </article>
      ))}
    </div>
  );
}
function AnkiTab({ result }: { result: GenerateReviewResponse }) {
  return (
    <div className="tab-panel">
      <div className="section-header compact">
        <h3>Anki 卡片</h3>
        {result.anki_csv_download_path && (
          <a
            className="secondary accent"
            href={downloadUrl(result.anki_csv_download_path)}
            download={downloadFilename(result.anki_csv_download_path)}
            target="_blank"
            rel="noreferrer"
          >
            下载 Anki CSV
          </a>
        )}
      </div>
      <div className="table-wrap anki-table-wrap">
        <table>
          <thead>
            <tr><th>Front</th><th>Back</th><th>Tags</th></tr>
          </thead>
          <tbody>
            {result.review_report.anki_cards.map((card) => (
              <tr key={`${card.front}-${card.tags}`}>
                <td>{card.front || "—"}</td>
                <td>{card.back || "—"}</td>
                <td><BadgeList items={String(card.tags || "—").split(/\s+/).filter(Boolean)} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: number }) {
  return <div className="metric-card"><strong>{value}</strong><span>{label}</span></div>;
}

function BadgeList({ items }: { items: string[] }) {
  const cleanItems = items.length > 0 ? items : ["—"];
  return (
    <div className="badge-list">
      {cleanItems.map((item, index) => (
        <span key={`${item}-${index}`} className="soft-badge">{item}</span>
      ))}
    </div>
  );
}