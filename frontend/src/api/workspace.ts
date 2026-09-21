import { downloadUrl, reviewApi, type ExamType, type StudyGoal, type OutputStyle, type GenerateReviewJob } from './client';
export type MaterialRole = 'slides' | 'textbook' | 'notes' | 'syllabus' | 'past_exam' | 'answer_key' | 'mistakes' | 'other';
export interface Material {id: string; original_filename: string; saved_filename: string; role: MaterialRole; pages: number}
export interface Project {
  id: string; course_name: string; exam_date: string; exam_type: string; daily_minutes: number; mastery_level: string;
  target_score?: string; focus?: string; created_at?: string; files?: Material[];
}
export interface ProjectForm {course_name: string; exam_date: string; exam_type: ExamType; daily_minutes: number; mastery_level: string; target_score: string; focus: string}
export interface Diagnosis {material_completeness: number; files_processed: number; roles: MaterialRole[]; missing: string[]; risks: string[]; recommended_strategy: string[]}
export type Page = 'home' | 'materials' | 'diagnosis' | 'processing' | 'results' | 'projects';
export type Mode = 'cram' | 'understand' | 'cards' | 'mock';
export const MODES: {id: Mode; title: string; description: string; detail: string; icon: 'bolt' | 'book' | 'cards' | 'target'; goal: StudyGoal; style: OutputStyle}[] = [
  {id:'cram',title:'考试突击',description:'抓住重点，高效备考',detail:'优先整理高频考点、核心公式与易错题',icon:'bolt',goal:'one_day_sprint',style:'sprint'},
  {id:'understand',title:'理解学习',description:'循序渐进，真正学懂',detail:'通过概念、关联知识和例题建立理解',icon:'book',goal:'balanced',style:'teaching_assistant'},
  {id:'cards',title:'知识卡片',description:'主动回忆，记得更牢',detail:'把知识拆成简短问答，支持主动回忆',icon:'cards',goal:'anki_focused',style:'anki_cards'},
  {id:'mock',title:'模拟考试',description:'以练代学，查漏补缺',detail:'按材料范围整理练习题与参考解析',icon:'target',goal:'practice_heavy',style:'practice_training'},
];
export const MATERIAL_ROLES: [MaterialRole,string][] = [['slides','课程课件'],['textbook','教材'],['notes','个人笔记'],['syllabus','课程纲要 / 考试范围'],['past_exam','往年试卷'],['answer_key','答案解析'],['mistakes','错题'],['other','其他资料']];
export const DEFAULT_FORM: ProjectForm = {course_name:'',exam_date:'',exam_type:'unknown',daily_minutes:90,mastery_level:'forgotten',target_score:'',focus:''};
export interface JobReference {id: string; status: GenerateReviewJob['status']}
export type ErrorContext = 'workspace' | 'upload' | 'diagnosis' | 'generation' | 'download' | 'project' | 'model' | 'general';
export type UserFacingError = {kind: 'network' | 'file' | 'ocr' | 'model' | 'missing' | 'service' | 'unknown'; title: string; message: string};
export async function listProjects() {return reviewApi<Project[]>('/projects');}
function rawErrorMessage(error: unknown): string {
  if (typeof error === 'object' && error && 'response' in error) {
    const response = (error as {response?: {data?: {detail?: unknown}}}).response;
    if (typeof response?.data?.detail === 'string') return response.data.detail;
  }
  return error instanceof Error ? error.message : '';
}
export function userFacingError(error: unknown, context: ErrorContext = 'general'): UserFacingError {
  const raw=rawErrorMessage(error);const text=raw.toLowerCase();
  if (/export_render_error|export_file_write_error/.test(text) || context==='download') return {kind:'service',title:'导出文件创建失败',message:'复习资料已经生成并保存。你可以重新导出，无需重新生成或重新识别资料。'};
  if (/llm_output_truncated/.test(text)) return {kind:'model',title:'生成内容较长',message:'模型响应被截断；系统会缩小当前章节并自动有限重试，已完成章节不会重做。'};
  if (/llm_context_exceeded/.test(text)) return {kind:'model',title:'当前章节超过模型输入限制',message:'系统会按章节与语义边界继续拆分后重试。'};
  if (/provider_rate_limit/.test(text)) return {kind:'model',title:'模型请求过于频繁',message:'服务商触发限流，请稍后从 checkpoint 继续。'};
  if (/provider_quota_exceeded/.test(text)) return {kind:'model',title:'模型额度不足',message:'请检查服务商余额或额度；已完成章节和生成内容仍然保留。'};
  if (/auth_failed|config_missing|model_not_found/.test(text)) return {kind:'model',title:'模型配置无法使用',message:'请检查 API Key、模型名称和 Base URL；已完成章节和生成内容仍然保留。'};
  if (/llm_timeout|llm_provider_error|llm_response_parse_error/.test(text)) return {kind:'model',title:'模型暂时无法响应',message:'请稍后重试；系统会从未完成章节继续，不会重新 OCR。'};
  if (/abort|cancel|取消/.test(text)) return {kind:'network',title:'操作已经停止',message:'这次操作已停止，没有产生新的更改。你可以重新开始。'};
  if (/ocr|文字识别|图像识别/.test(text)) return {kind:'ocr',title:'图片文字没有识别完成',message:'请确认图片清晰、方向正确，然后重新识别；也可以换用文字版 PDF。'};
  if (/model|模型|api key|quota|额度|token|context length/.test(text) || context==='model') return {kind:'model',title:'AI 模型暂时不可用',message:'请检查模型设置和可用额度，然后重试。你的已上传资料不会丢失。'};
  if (/network|fetch|timeout|timed out|cors|无法连接|连接后端|econn/.test(text)) return {kind:'network',title:'暂时连接不上服务',message:'请检查网络或确认 RecallForge 服务已经启动，然后重试。'};
  if (/文件|格式|file type|unsupported|empty|too large|413/.test(text) || context==='upload') return {kind:'file',title:'这份文件暂时无法处理',message:'请确认格式受支持、文件可以正常打开，并且单个文件不超过 50 MB，然后重新上传。'};
  if (/404|not found|不存在|已删除/.test(text)) return {kind:'missing',title:'没有找到这项内容',message:'它可能已被删除或失效。请返回项目列表后重新选择。'};
  if (/500|502|503|504|service|internal|服务器/.test(text)) return {kind:'service',title:'服务暂时没有完成这一步',message:'你的资料和项目仍然保留。请稍后重试。'};
  if (context==='generation') return {kind:'unknown',title:'复习资料没有生成完成',message:'已上传资料仍然保留。请重新生成；如果问题持续出现，请检查模型设置。'};
  if (context==='diagnosis') return {kind:'unknown',title:'资料分析没有完成',message:'请保留当前资料并重试，不需要重新上传。'};
  if (context==='project') return {kind:'unknown',title:'项目操作没有完成',message:'项目内容没有改变，请重试。'};
  return {kind:'unknown',title:'这一步没有完成',message:'当前内容已经保留，请重试。'};
}
export function errorMessage(error: unknown, context: ErrorContext = 'general'): string {return userFacingError(error,context).message;}
export async function downloadArtifact(path: string, filename: string) {
  const response = await fetch(downloadUrl(path));
  if (!response.ok) throw new Error(`下载失败（HTTP ${response.status}），请重试。`);
  const url = URL.createObjectURL(await response.blob());
  const link = document.createElement('a'); link.href=url;link.download=filename;document.body.append(link);link.click();link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url),1000);
}
