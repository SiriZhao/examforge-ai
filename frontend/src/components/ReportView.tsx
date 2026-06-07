import { useState } from "react";

import { downloadUrl, type ExportFormat, type GenerateReviewResponse } from "../api/client";
import { MarkdownView } from "./MarkdownView";

type ReportViewProps = {
  result: GenerateReviewResponse | null;
  onExport: (format: ExportFormat) => void;
  exporting: ExportFormat | null;
  onOpenLLMSettings?: () => void;
  onTestLLM?: () => void;
};

type ReportTab = "overview" | "priority" | "topics" | "mock" | "anki" | "markdown";

const TABS: Array<{ id: ReportTab; label: string }> = [
  { id: "overview", label: "总览" },
  { id: "priority", label: "章节优先级" },
  { id: "topics", label: "高频考点" },
  { id: "mock", label: "模拟卷" },
  { id: "anki", label: "Anki 卡片" },
  { id: "markdown", label: "Markdown 预览" },
];

export function ReportView({ result, onExport, exporting, onOpenLLMSettings = () => undefined, onTestLLM = () => undefined }: ReportViewProps) {
  const [activeTab, setActiveTab] = useState<ReportTab>("overview");
  const [showFallbackNotice, setShowFallbackNotice] = useState(true);

  if (!result) {
    return (
      <section className="panel empty-state">
        <p className="eyebrow">生成结果</p>
        <h2>复习资料包将在这里生成</h2>
        <p>
          生成后，这里会展示完整的复习报告，包括总览、章节优先级、高频考点、模拟卷、Anki 卡片和 Markdown 预览。
        </p>
        <div className="empty-tips">
          <span>上传往年题后，可以获得更准确的高频考点分析。</span>
          <span>规则模式无需 API Key，也可以生成基础复习资料。</span>
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
          {(["md", "docx", "pdf"] as ExportFormat[]).map((format) => (
            result.download_links[format] ? (
              <a key={format} className="secondary" href={downloadUrl(result.download_links[format] || "")} target="_blank" rel="noreferrer">
                下载 {format.toUpperCase()}
              </a>
            ) : (
              <button key={format} className="secondary" type="button" onClick={() => onExport(format)} disabled={exporting !== null}>
                {exporting === format ? "正在导出..." : `导出 ${format.toUpperCase()}`}
              </button>
            )
          ))}
          {result.anki_csv_download_path && (
            <a className="secondary accent" href={downloadUrl(result.anki_csv_download_path)} target="_blank" rel="noreferrer">
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

  if (status === "success" || source === "llm_enhanced") {
    const chunked = result.llm_context_strategy === "chunked";
    return (
      <div className="success-box">
        <strong>大模型增强已完成</strong>
        <p>当前报告来源：规则模式 + 大模型增强</p>
        <p>
          {chunked
            ? "由于资料较长，系统已自动进行分块摘要和合并增强。"
            : "已使用大模型对章节总结、考点归纳、模拟题和复习计划进行增强。"}
        </p>
      </div>
    );
  }

  if ((status === "failed" || source === "rule_based_with_llm_failed") && visible) {
    const error = result.llm_error;
    return (
      <div className="llm-fallback-box">
        <strong>{result.llm_error?.code === "CONTEXT_TOO_LONG" ? "资料过长，大模型增强未完成" : "已生成规则版报告，但大模型增强未成功"}</strong>
        <p>当前报告由本地规则模式生成，可用于基础复习整理。由于大模型增强未成功，章节概括、考点归纳、模拟题质量和复习计划的系统性可能有限。</p>
        <p>
          {result.llm_error?.code === "CONTEXT_TOO_LONG"
            ? "系统已保留规则版报告。建议减少单次上传资料，或分批上传课件、教材和往年题后分别生成。"
            : "建议检查大模型配置后重新生成，以获得更准确的重点提炼、更清晰的章节优先级、更完整的模拟卷和 Anki 卡片。"}
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
          <button type="button" className="secondary" onClick={onDismiss}>继续查看规则版</button>
          <button type="button" className="secondary" onClick={onRegenerate}>重新生成</button>
        </div>
      </div>
    );
  }

  return (
    <div className="info-box">
      <strong>当前报告来源：规则模式</strong>
      <p>本报告由本地规则生成，适合快速整理资料。若要获得更自然、更系统的章节总结、模拟卷和 Anki 卡片，建议开启大模型增强后重新生成。</p>
      <button type="button" className="secondary accent" onClick={onOpenLLMSettings}>开启大模型增强</button>
    </div>
  );
}

function OverviewTab({ result }: { result: GenerateReviewResponse }) {
  const report = result.review_report;
  return (
    <div className="tab-panel">
      <p className="summary">{report.summary}</p>
      <div className="feature-grid">
        <MetricCard label="识别出的往年题" value={report.past_exam_analysis.detected_files.length} />
        <MetricCard label="高频考点" value={report.past_exam_analysis.high_frequency_topics.length} />
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
  return (
    <div className="tab-panel">
      <h3>章节优先级评分</h3>
      <div className="table-wrap">
        <table>
          <thead>
            <tr><th>章节</th><th>重要度</th><th>材料命中</th><th>往年题命中</th><th>题型</th></tr>
          </thead>
          <tbody>
            {result.review_report.chapters.map((chapter) => (
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
  const analysis = result.review_report.past_exam_analysis;
  return (
    <div className="tab-panel">
      <p className="summary">{analysis.summary}</p>
      <div className="table-wrap">
        <table>
          <thead>
            <tr><th>考点</th><th>章节</th><th>频次</th><th>题型</th></tr>
          </thead>
          <tbody>
            {analysis.high_frequency_topics.map((topic) => (
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
    <div className="mock-exam tab-panel">
      <div className="section-header compact">
        <h3>模拟卷与参考答案</h3>
        <span className="muted">已包含在 Markdown 和 Word 导出文件中。</span>
      </div>
      {result.review_report.mock_exam.questions.map((question, index) => (
        <article key={`${question.question_type}-${index}`}>
          <strong>{index + 1}. {question.question_type}</strong>
          <p>{question.question}</p>
          <p className="muted">参考答案：{question.answer}</p>
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
          <a className="secondary accent" href={downloadUrl(result.anki_csv_download_path)} target="_blank" rel="noreferrer">
            下载 Anki CSV
          </a>
        )}
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr><th>正面</th><th>背面</th><th>标签</th></tr>
          </thead>
          <tbody>
            {result.review_report.anki_cards.map((card) => (
              <tr key={`${card.front}-${card.tags}`}>
                <td>{card.front}</td>
                <td>{card.back}</td>
                <td>{card.tags}</td>
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
