# RecallForge v3.0 桌面端设计交接

## 交付与预览

本交付是可运行的 React 高保真交互原型。独立入口为 `frontend/recallforge-v3.html`，不替换当前业务首页。启动方式：在 `frontend` 目录运行 `npm run dev`，打开 `/recallforge-v3.html`。原型源码位于 `frontend/src/design/main.tsx`，设计 token 与响应式样式位于同目录 `recallforge.css`。

导航覆盖学习首页、AI 处理、学习结果、组件规范；顶部齿轮可打开设置弹窗。首页点击「体验示例」可完整查看处理流程；最近项目提供结果直达入口。原型使用示例项目和高数知识，不调用真实 AI，不解析所选文件。文件上传上限 50 MB 是交互设计约定，需要后端协同确认。没有将示例模型状态冒充真实连接状态。

## 设计方向：Forest & Paper

暖白纸面配深墨绿，以轻量导航和宽阔内容区建立安静、专注的学习空间。避免数据看板式统计卡片和密集表格；首页只强调一个核心任务：上传学习资料。辅助模式用单选卡片呈现，右侧项目以文件为线索，而非后台数据行。

品牌标记为四角星形线条，表达「从资料中提炼知识」。该标记使用 SVG，支持无损缩放。插图为 CSS 纸张与 SVG 文件图标，无位图依赖。

## 首页布局

基准画板：1440 × 900 CSS px；推荐桌面宽度 1280–1600。

- 左侧固定 Sidebar：224 px；品牌位于顶部，个人空间、创建项目与三项主导航向下排列；组件规范及身份区置底。
- 顶栏：72 px；面包屑左对齐，模型状态和设置在右侧。Logo 常驻侧栏顶部，与顶栏共同构成全局导航。
- 主内容：左右 36 px，顶部 52 px。采用 `minmax(0, 1fr) 288px` 双栏布局，列间距 40 px；最大宽度 1440 px。
- 中央引导：英文微标题 9 px、中文主标题 36 px、说明 13 px；标题下方留 34 px。
- Upload Box：基准高度 316 px，圆角 14 px，1 px 虚线；纸张插图、上传文案、主按钮、支持格式垂直居中。支持 PDF、PPT/PPTX、PNG/JPEG/WebP、DOC/DOCX。
- 模式卡片：四列，间距 10 px；选中采用浅绿底、绿色描边、勾选标记，同时设置 `aria-pressed`。切换更新下方模式说明和生成按钮文案。
- 最近项目：独立细分隔线，内边距 27 px；每项呈现文件类型、单行文件名、生成内容摘要、创建时间、状态。长标题省略，生产版本应增加可聚焦详情或完整名称提示。
- 页底轻量流程提示「上传资料 → AI 理解 → 生成内容 → 导出复习」。

响应式：1200 px 以下 Sidebar 200 px、模式两列；980 px 以下最近项目移至主内容下方；720 px 以下侧栏收为 64 px 图标栏、模式两列、项目单列。页面允许自然滚动，不压缩主要操作目标。

## AI 处理页面

内容最大宽度 710 px，单一中心视线。顶部标题与文件名，中部呼吸式图标、确定型进度条，下方垂直五阶段：上传 → OCR → 章节理解 → AI 生成 → 完成。

每阶段显示序号/完成图标、阶段说明和文字状态；避免只依靠颜色。原型约 11 秒走完整个演示；可暂停、继续、返回首页。100% 时保留完成状态，用户主动点击「查看学习内容」。采用 220 ms 进度过渡、2 s 呼吸动画；`prefers-reduced-motion` 关闭动态效果。

真实接入要求：进度由服务器任务状态驱动，禁止生产中使用假进度计时器。未知进度时使用不确定型进度；OCR 不适用时明确「无需 OCR，已跳过」。失败时保留成功阶段，在错误阶段给出原因与重试；取消需要服务器确认终止后再标记取消。页面离开不应隐式销毁后台任务。

## 结果页面

顶部为标题、来源文件和导出按钮，下方横向内容标签页。主内容白色文档面板 + 210 px 学习路径侧栏。

- 知识总结：章节编号、主标题、核心概念提示、分节讲解、公式和来源说明。
- 思维导图：中心概念与三条知识分支；语义化 DOM 保持文字可读，生产复杂图可采用 React Flow，并保留文本纲要视图。
- 问答卡片：单卡问答切换；键盘可触发，先回忆再揭示答案。生产版本补充卡组导航、掌握程度和间隔重复调度。
- 练习题：单选交互，选择后显示正确性与解释，不能只有颜色反馈。
- 模拟考试：可编辑答案和显式「查看解析」；当前为两题自评节选，不含自动评分。
- 导出：当前标签内容可实际下载为 Markdown。生产版可加 PDF、Word、Anki TSV，只有真实可用格式才能显示可执行操作。

## 设计系统

### 颜色

- 主色 `#245C49`：主按钮、选中标签、品牌；hover `#194632`。
- 辅助色 `#EEF4EF`：提示、概念容器；不用于长文本。
- 背景色 `#F8F9F6`；内容表面 `#FFFFFF`；侧栏 `#F1F3ED`。
- 主要文字 `#232D29`；次要文字 `#69736D`；结构描边 `#E4E8E1`。
- 成功、等待、失败都要附文字/图标。原型部分装饰与辅助文案使用较浅色，生产交付前需逐项测量文字对比度，并将必要信息提升至至少 WCAG AA 4.5:1。

### 字体与间距

字体：DM Sans / Noto Sans SC；降级至系统 sans-serif。当前 Web 字体通过 Google Fonts 加载；离线桌面发行建议自托管有许可证的字体文件或用系统字体，避免网络依赖。

主标题 36/50，结果标题 30/42，二级标题 26/36，正文 13–14/24，组件文字 12/18，元数据 10–11/16。原型低密度桌面强调精致，生产可提供界面缩放并提升小字号到 12 px。

间距基数 4 px：4、8、12、16、24、32、48。常规卡片圆角 12 px，按钮 8 px，上传区 14 px。阴影仅用于轻微纸张层次、浮层和提示，主界面以细描边区分层级。

### 组件约定

- **Button**：primary / secondary / text / icon。常规高 40 px，左右 17 px；default、hover、focus-visible、disabled、loading。图标按钮须有可访问名称。原型焦点环 3 px；生产触控入口扩大至 44 px。
- **Card**：内容卡和模式卡分开。模式是单选，选中用底色、边框、勾选三重表达。按钮信息不嵌套额外按钮。
- **Upload Box**：idle / dragging / selected / invalid / uploading。点击与拖拽等价；支持多选、删除、格式与大小提示。前端校验仅辅助，服务端必须再次校验扩展名、MIME、大小和实际内容。
- **Sidebar**：默认、悬停、选中、折叠；推荐路由接入后添加 `aria-current="page"`，折叠模式提供工具提示。
- **Progress**：waiting / running / paused / completed / failed / cancelled。确定型使用 `aria-valuenow`；阶段转换使用节制的 live region，避免每个百分比都播报。
- **File Item**：type、name、createdAt、status、summary、onOpen。状态枚举 ready / processing / completed / failed。空项目列表应显示「还没有学习项目」，保留上传主入口。
- **Result Tabs**：生产补齐 roving tabindex、左右方向键、Home/End；原型可通过 Tab 聚焦各标签并用 Enter 选择。
- **Dialog**：使用原生 dialog 模态行为，Escape 关闭；生产设置支持真实 provider、model、连接测试与状态反馈。

## React 实现建议

保留现有 React 19 + TypeScript + Vite。原型为了便于交接集中于一个入口文件；正式开发按组件与领域拆分：

```text
src/
  app/AppShell.tsx
  components/ui/{Button,Card,Icon,Dialog}.tsx
  features/upload/{UploadBox,SelectedFiles}.tsx
  features/projects/{ProjectList,FileItem}.tsx
  features/jobs/{JobProgress,StageItem}.tsx
  features/results/{ResultTabs,Summary,MindMap,Flashcards,Practice,MockExam}.tsx
  pages/{Dashboard,Processing,Results,Settings}.tsx
  styles/{tokens,layout,components}.css
```

以服务端任务为唯一真实状态：`Project → Material[] → GenerationJob → Artifact[]`。UI 状态如当前模式、标签、卡片翻面与任务状态分离。已有 `src/api/client.ts` 提供 review workspace、项目上传、生成 job 和轮询能力，应在这些已有接口上适配，不先另造一套后端。

建议类型：

```ts
type StudyMode = 'cram' | 'understand' | 'flashcards' | 'mock';
type JobState = 'queued' | 'running' | 'completed' | 'failed' | 'cancelled';
type Stage = 'upload' | 'ocr' | 'understand' | 'generate' | 'complete';
type ArtifactKind = 'summary' | 'mindmap' | 'flashcards' | 'practice' | 'mock';
interface Artifact {
  id: string;
  kind: ArtifactKind;
  content: unknown; // 正式实现按 kind 使用 discriminated union
  sourceRefs: { materialId: string; page?: number; section?: string }[];
}
```

轮询接入使用 AbortController 和 effect cleanup，任务终态停止轮询；可优先使用现有 API，后续按需要改 SSE。失败包含可读信息与 retryable 标记。长文件列表虚拟化需以实测为依据。Markdown 输出渲染进行安全处理；公式使用 KaTeX；生成内容保留原文引用，方便核对。

导出由 artifact 类型与后端支持格式共同决定；不能给尚未生成的模块启用导出。客户端 Blob 下载仅适用于本原型和小型纯文本内容。正式桌面可结合现有容器，文件对话框及保存路径通过受限桥接暴露。

## 验收边界

本轮交付：界面设计、组件风格、交互样例、布局与工程交接。模型接入、真实解析、持久化、服务端任务恢复、自动评分与 PDF/Word 导出属于业务接入工作，当前没有实现。已有业务入口继续使用原实现。

## 独立交付与验证记录

可直接双击 `docs/RecallForge-v3-preview.html` 查看完整交互原型，无需安装依赖（字体网络不可用时自动回退系统字体）。该文件由 React 生产构建内嵌生成；后续以 `frontend/src/design` 源文件为准。

独立打包命令：`npx vite build --config vite.design.config.ts`，产物目录为 `frontend/dist-design`。

新增设计入口已在独立临时依赖环境通过 TypeScript strict 检查及 Vite 生产构建。仓库原锁文件的 `@jridgewell/gen-mapping@0.3.23` 下载返回 404，因此没有声称原项目完整安装或业务测试通过；未改动依赖声明或锁文件。

浏览器已确认首页、五阶段流程、结果页，验证卡片翻面、练习反馈、模拟题填写和参考解析、Markdown 下载、设置弹窗及 Escape 关闭。截图位于 `output/playwright`。
补充验证：文件选择与删除、390 px 窄屏无横向溢出检查通过。单文件 HTML 通过本地 HTTP 预览验证；自动化浏览器禁止 file: 协议，因此未自动验证双击打开。
