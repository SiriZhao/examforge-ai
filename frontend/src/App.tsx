import { useEffect, useMemo, useState } from "react";

import {
  createGenerateReviewJob,
  ensureReviewWorkspace,
  getGenerateReviewJob,
  reviewApi,
  reviewUpload,
  type LLMConfig,
  type OCRConfig,
  type ReviewProject,
} from "./api/client";
import { ReportView } from "./components/ReportView";

type Step = "settings" | "materials" | "diagnosis" | "progress" | "report" | "mock" | "anki" | "plan" | "export";
type MaterialRole = "slides" | "textbook" | "notes" | "syllabus" | "past_exam" | "answer_key" | "mistakes" | "other";

const steps: Array<[Step, string]> = [
  ["settings", "1. 复习设置"], ["materials", "2. 上传资料"], ["diagnosis", "3. 资料诊断"],
  ["progress", "4. 生成进度"], ["report", "5. 复习资料"], ["mock", "6. 模拟测试"],
  ["anki", "7. Anki 卡片"], ["plan", "8. 冲刺计划"], ["export", "9. 导出"],
];

const materialRoles: Array<[MaterialRole, string]> = [
  ["slides", "课程课件"], ["textbook", "教材"], ["notes", "个人笔记"], ["syllabus", "课程纲要 / 考试范围"],
  ["past_exam", "往年试卷"], ["answer_key", "答案解析"], ["mistakes", "错题"], ["other", "其他资料"],
];

const defaultLlm: LLMConfig = { enabled: false, provider: "deepseek", api_key: "", base_url: "https://api.deepseek.com", model: "" };

export default function App() {
  const [step, setStep] = useState<Step>("settings");
  const [project, setProject] = useState<ReviewProject | null>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [uploaded, setUploaded] = useState<Array<{ id: string; saved_filename: string; original_filename: string }>>([]);
  const [rolesByFile, setRoles] = useState<Record<string, MaterialRole>>({});
  const [diagnosis, setDiagnosis] = useState<any>(null);
  const [job, setJob] = useState<any>(null);
  const [result, setResult] = useState<any>(null);
  const [status, setStatus] = useState("");
  const [form, setForm] = useState({ course_name: "", exam_date: "", exam_type: "unknown", daily_minutes: 90, mastery_level: "forgotten", target_score: "", focus: "" });
  const [llm, setLlm] = useState<LLMConfig>(() => {
    try { return JSON.parse(localStorage.getItem("examforge-byok") || "null") || defaultLlm; } catch { return defaultLlm; }
  });

  useEffect(() => {
    void ensureReviewWorkspace().catch(() => setStatus("无法初始化本地工作空间，请刷新后重试。"));
  }, []);

  const completed = useMemo<Record<Step, boolean>>(() => ({
    settings: Boolean(project), materials: uploaded.length > 0, diagnosis: Boolean(diagnosis), progress: Boolean(job),
    report: Boolean(result), mock: Boolean(result), anki: Boolean(result), plan: Boolean(result), export: Boolean(result),
  }), [project, uploaded, diagnosis, job, result]);

  async function createProject() {
    const item = await reviewApi<ReviewProject>("/projects", "POST", form);
    setProject(item); setStep("materials"); setStatus("复习项目已创建。下一步上传并标记资料用途。");
  }

  async function upload() {
    if (!project || files.length === 0) return;
    setStatus("正在检查并上传资料...");
    const response = await reviewUpload<{ files: Array<{ id: string; saved_filename: string; original_filename: string; role: MaterialRole }> }>(`/projects/${project.id}/upload`, files);
    setUploaded(response.files);
    setRoles(Object.fromEntries(response.files.map((item) => [item.saved_filename, item.role])));
    setStatus("请确认每份资料的用途，再开始诊断。");
  }

  async function diagnose() {
    if (!project || uploaded.length === 0) return;
    setStatus("正在解析资料、识别角色并生成复习诊断...");
    await Promise.all(uploaded.map((item) => reviewApi(`/projects/${project.id}/files/${item.id}`, "PATCH", { role: rolesByFile[item.saved_filename] || "other" })));
    const data = await reviewApi(`/projects/${project.id}/diagnosis`);
    setDiagnosis(data); setStep("diagnosis"); setStatus("资料诊断完成。确认策略后开始分模块生成。");
  }

  async function generate() {
    if (!project) return;
    setStep("progress"); setStatus("正在创建生成任务：长资料会分块处理，并尽量保留往年题、定义、公式与例题。");
    const created = await createGenerateReviewJob({
      files: uploaded.map((item) => item.saved_filename), title: project.course_name, course_name: project.course_name,
      export_format: "md", export_formats: ["md", "docx", "pdf"], study_goal: "balanced", exam_type: form.exam_type as any,
      detail_level: "detailed", output_style: "teaching_assistant", enable_chunked_llm: true, retry_on_context_too_long: true,
      ocr_config: { provider: "rapidocr", mode: "fast", language: "chi_sim+eng" } as OCRConfig,
      llm_config: { ...llm, enabled: Boolean(llm.api_key) },
    });
    setJob(created);
    for (;;) {
      await new Promise((resolve) => window.setTimeout(resolve, 900));
      const current = await getGenerateReviewJob(created.job_id);
      setJob(current); setStatus(current.message);
      if (current.status === "completed") { setResult(current.result); setStep("report"); return; }
      if (current.status === "failed") throw new Error(current.error || "生成失败");
    }
  }

  function saveKey() {
    localStorage.setItem("examforge-byok", JSON.stringify(llm));
    setStatus("API 配置仅保存在当前浏览器。生成时会临时转发给你选择的模型服务，不会写入项目数据库或日志。");
  }

  async function testKey() {
    if (!llm.api_key || !llm.base_url) { setStatus("请先填写 API Key 和 Base URL。"); return; }
    try {
      const base = llm.base_url.replace(/\/$/, "");
      const response = await fetch(`${base}/models`, { headers: { Authorization: `Bearer ${llm.api_key}` }, signal: AbortSignal.timeout(15_000) });
      setStatus(response.ok ? "模型连接成功。API Key 只用于本次浏览器连接测试。" : `连接未成功（HTTP ${response.status}），请检查 Base URL、模型名称和 Key。`);
    } catch {
      setStatus("连接测试未成功。请检查网络、Base URL、浏览器 CORS 限制和 API Key。Key 没有发送到 ExamForge 服务器。");
    }
  }

  return <div className="examforge-app">
    <header className="examforge-top"><div><strong>ExamForge AI</strong><span>面向大学生期末考试的 AI 复习资料生成器</span></div><div><span className={llm.api_key ? "model-on" : "model-off"}>{llm.api_key ? "模型已配置" : "未配置模型"}</span><button onClick={() => setStep("settings")}>设置</button></div></header>
    <div className="examforge-layout">
      <aside className="step-nav">{steps.map(([id, label]) => <button key={id} className={step === id ? "active" : ""} onClick={() => setStep(id)} disabled={!completed[id] && !["settings", "materials"].includes(id)}>{completed[id] ? "✓ " : ""}{label}</button>)}</aside>
      <main className="examforge-main">
        {status && <div className="status-bar">{status}</div>}
        {step === "settings" && <Settings form={form} setForm={setForm} llm={llm} setLlm={setLlm} onCreate={createProject} onSave={saveKey} onTest={testKey} />}
        {step === "materials" && <Materials files={files} setFiles={setFiles} uploaded={uploaded} roles={rolesByFile} setRoles={setRoles} onUpload={upload} onDiagnose={diagnose} />}
        {step === "diagnosis" && <Diagnosis diagnosis={diagnosis} onGenerate={generate} />}
        {step === "progress" && <Progress job={job} />}
        {["report", "mock", "anki", "plan", "export"].includes(step) && result && <ReportView result={result} exporting={null} onExport={() => undefined} />}
      </main>
      <aside className="review-context"><h3>复习项目</h3><strong>{project?.course_name || "尚未创建"}</strong><p>无需注册 · 使用自己的 API</p>{diagnosis && <><h4>资料完整度</h4><strong>{diagnosis.material_completeness}/100</strong><h4>生成策略</h4>{diagnosis.recommended_strategy.map((item: string) => <p key={item}>{item}</p>)}</>}</aside>
    </div>
  </div>;
}

function Settings({ form, setForm, llm, setLlm, onCreate, onSave, onTest }: any) {
  const update = (key: string, value: unknown) => setForm((current: any) => ({ ...current, [key]: value }));
  const updateLlm = (key: string, value: unknown) => setLlm((current: any) => ({ ...current, [key]: value }));
  return <section className="review-page"><p className="eyebrow">创建复习项目</p><h1>把杂乱课程资料，变成真正能用来复习、刷题和冲刺的资料包。</h1>
    <div className="form-grid"><label>课程名称<input value={form.course_name} onChange={(event) => update("course_name", event.target.value)} placeholder="例如：概率论" /></label><label>考试日期<input type="date" value={form.exam_date} onChange={(event) => update("exam_date", event.target.value)} /></label><label>考试形式<select value={form.exam_type} onChange={(event) => update("exam_type", event.target.value)}><option value="unknown">暂不确定</option><option value="closed_book">闭卷笔试</option><option value="open_book">开卷笔试</option><option value="programming">编程考试</option><option value="lab_exam">实验考试</option><option value="essay_based">简答论述为主</option><option value="mixed">混合考试</option></select></label><label>每日复习时间（分钟）<input type="number" value={form.daily_minutes} onChange={(event) => update("daily_minutes", Number(event.target.value))} /></label><label>当前掌握程度<select value={form.mastery_level} onChange={(event) => update("mastery_level", event.target.value)}><option value="none">几乎没学</option><option value="weak">基础薄弱</option><option value="forgotten">学过但忘得较多</option><option value="solid">基本掌握</option><option value="sprint">主要需要冲刺</option></select></label><label>目标成绩<input value={form.target_score} onChange={(event) => update("target_score", event.target.value)} placeholder="例如：85+" /></label></div>
    <label className="wide-field">希望重点提升的方面<textarea value={form.focus} onChange={(event) => update("focus", event.target.value)} placeholder="例如：计算题、论述题、背诵效率" /></label>
    <section className="byok"><h2>你的 AI 模型</h2><p>推荐配置自己的模型以获得更自然的专题重组、往年题分析、模拟卷和 Anki。API Key 默认只保存在当前浏览器，不写入数据库、日志或 GitHub。</p><div className="form-grid"><label>供应商<select value={llm.provider || "deepseek"} onChange={(event) => updateLlm("provider", event.target.value)}><option value="deepseek">DeepSeek</option><option value="openai">OpenAI</option><option value="openai_compatible">OpenAI-compatible</option></select></label><label>模型名称<input value={llm.model || ""} onChange={(event) => updateLlm("model", event.target.value)} placeholder="填写你可用的模型名称" /></label><label>Base URL<input value={llm.base_url || ""} onChange={(event) => updateLlm("base_url", event.target.value)} placeholder="https://api.deepseek.com" /></label><label>API Key<input type="password" value={llm.api_key || ""} onChange={(event) => updateLlm("api_key", event.target.value)} autoComplete="off" /></label></div><button onClick={onSave}>保存到当前浏览器</button><button className="secondary" onClick={onTest}>测试连接</button></section>
    <button className="primary" disabled={!form.course_name.trim()} onClick={onCreate}>创建复习项目</button>
  </section>;
}

function Materials({ files, setFiles, uploaded, roles, setRoles, onUpload, onDiagnose }: any) {
  return <section className="review-page"><p className="eyebrow">上传与标记资料</p><h1>每类资料有不同作用，不会被粗暴拼接。</h1><input type="file" multiple accept=".pdf,.pptx,.docx,.md,.txt,.png,.jpg,.jpeg" onChange={(event) => setFiles(Array.from(event.target.files || []))} />{files.length > 0 && uploaded.length === 0 && <button className="primary" onClick={onUpload}>上传 {files.length} 份资料</button>}{uploaded.map((file: any) => <div className="file-row" key={file.saved_filename}><strong>{file.original_filename}</strong><select value={roles[file.saved_filename] || "other"} onChange={(event) => setRoles((current: any) => ({ ...current, [file.saved_filename]: event.target.value }))}>{materialRoles.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></div>)}{uploaded.length > 0 && <button className="primary" onClick={onDiagnose}>生成资料诊断</button>}</section>;
}

function Diagnosis({ diagnosis, onGenerate }: any) {
  if (!diagnosis) return <section className="review-page"><h1>等待资料诊断</h1></section>;
  return <section className="review-page"><p className="eyebrow">复习诊断</p><h1>先确认资料质量和生成策略。</h1><div className="diagnosis-score">资料完整度 <strong>{diagnosis.material_completeness}/100</strong></div><div className="diagnosis-grid"><article><h3>已有资料</h3><p>已处理 {diagnosis.files_processed} 份文件</p><p>{diagnosis.roles.join("、") || "未识别角色"}</p></article><article><h3>资料缺口</h3>{diagnosis.missing.map((item: string) => <p key={item}>{item}</p>)}</article><article><h3>推荐策略</h3>{diagnosis.recommended_strategy.map((item: string) => <p key={item}>{item}</p>)}</article></div><button className="primary" onClick={onGenerate}>确认并开始分模块生成</button></section>;
}

function Progress({ job }: any) {
  const modules = ["资料诊断", "重点地图", "核心讲义", "往年题分析", "题型攻略", "模拟试卷", "Anki 卡片", "冲刺计划"];
  return <section className="review-page"><p className="eyebrow">生成进度</p><h1>{job?.message || "正在准备任务"}</h1><progress value={job?.progress || 0} max="100" /><p>{job?.progress || 0}%</p><div className="module-status">{modules.map((item, index) => <div key={item}>{index < (job?.progress || 0) / 13 ? "✓" : "○"} {item}</div>)}</div></section>;
}

function guessRole(filename: string): MaterialRole {
  const text = filename.toLowerCase();
  if (/试卷|真题|历年|期末|exam|past/.test(text)) return "past_exam";
  if (/答案|解析|answer|solution/.test(text)) return "answer_key";
  if (/纲要|范围|大纲|syllabus/.test(text)) return "syllabus";
  if (/笔记|note/.test(text)) return "notes";
  if (/教材|textbook/.test(text)) return "textbook";
  if (/错题|wrong/.test(text)) return "mistakes";
  if (/课件|slide|ppt/.test(text)) return "slides";
  return "other";
}
