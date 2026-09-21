# RecallForge v3.0 UI 实施报告

## 实施结果

现有 React 前端已升级为 RecallForge v3.0 产品界面，并接入原有工作区、项目、文件上传、资料诊断、异步 AI 生成任务和导出接口。正式入口仍为 `frontend/src/main.tsx`，技术栈保持 React 19、Vite 与 TypeScript。设计稿原型保留为独立参考入口，不参与正式产品构建。

界面使用 Forest & Paper 设计语言：暖白背景、深墨绿主色、低对比度结构线与纸张式内容表面。桌面端使用 224px 固定侧栏、72px 顶栏、中央上传主任务和右侧最近项目；窄屏收为 64px 图标侧栏，内容、表单、项目列表和结果页面自动改为单列。

## 修改内容

### 产品页面

- `Dashboard`：真实上传入口、文件校验与待上传列表、复习设置、四种学习模式、最近项目和空状态。
- `MaterialsPage`：展示已解析资料、修改资料角色、追加资料并进入诊断。
- `DiagnosisPage`：展示资料完整度、资料缺口、风险和后端推荐策略；确认学习模式后创建生成任务。
- `ProcessingPage`：使用服务器返回的真实进度驱动上传与解析、OCR、章节理解、AI 生成与导出、完成五个阶段；支持失败重试和轮询中断后的安全恢复。
- `ProjectsPage`：从工作区读取真实项目与资料信息，支持重新打开未完成或已完成任务。
- `ResultsPage`：展示知识总结、思维导图、问答卡片、练习题和模拟考试；根据后端实际产物启用 Markdown、Word、PDF 和 Anki CSV 下载。
- `ModelSettings`：保留 BYOK 配置、浏览器本地保存和连接测试，明确本地整理模式与模型配置状态。

### 业务流程

- 首次上传会创建复习项目；上传失败后保留文件与已创建项目，重试不会重复创建项目。
- 文件角色修改通过原有项目文件 PATCH 接口保存，再请求资料诊断。
- AI 生成使用原有异步 job 接口。轮询支持 AbortController 清理，页面返回首页后任务继续运行；已知 job id 保存在当前工作区的 localStorage，重新打开项目可恢复查询。
- 生成失败不会显示虚假结果；失败阶段停在「AI 生成与导出」，此前阶段保持完成，最终阶段保持等待。
- 导出只在后端返回对应产物时启用。job 存在时使用 job scoped 下载地址，下载错误会在结果页显示。
- 最近项目接口补充了创建时间、目标、重点和资料列表，同时保持工作区隔离。

## 新增组件与目录

### `frontend/src/design-system`

- `Button.tsx`：primary、secondary、text 三种变体，支持 loading、disabled、原生按钮属性和 ref。
- `Card.tsx`：统一内容表面、圆角、描边和布局容器。
- `Modal.tsx`：基于原生 dialog，支持 Escape、焦点返回和可访问标题。
- `Upload.tsx`：拖拽与文件选择、格式/大小/数量校验、去重、删除和错误状态。
- `Progress.tsx`：确定型与不确定型进度、五阶段状态、文字与图标双重反馈。
- `Icon.tsx`：类型化 SVG 图标集合。
- `tokens.css`：颜色、间距、圆角、尺寸和动效 token。
- `styles.css`：应用框架、组件状态、页面布局及响应式规则。

### `frontend/src/components`

- `AppShell`、`ModeSelector`、`ProjectFields`、`ProjectList`
- `ModelSettings`、`ResultTabs`、`KnowledgeMap`、`Flashcards`、`Questions`

### 状态与类型

- `frontend/src/api/workspace.ts` 定义项目、资料、诊断、页面、模式和任务引用类型。
- `frontend/src/hooks/useReviewWorkspace.ts` 集中管理初始化、上传、诊断、生成、轮询恢复、项目切换和错误状态。
- `frontend/src/api/client.ts` 的 job 查询支持 AbortSignal，用于安全取消页面级轮询。
- 正式页面和组件没有使用 `any`；所有外部数据都使用现有 API 类型或新增领域类型。
- `frontend/package-lock.json` 刷新了允许范围内的传递依赖解析；原锁文件引用的 `@jridgewell/gen-mapping@0.3.23` 在安装时返回 404，更新后测试与构建可正常执行，未增加直接依赖。

## 设计与可访问性

- 主色 `#245C49`，hover `#194632`，辅助底色 `#EEF4EF`，页面背景 `#F8F9F6`，主要文字 `#232D29`。
- 组件间距采用 4px 基数；常规控件高度至少 40px，侧栏导航至少 44px。
- 上传模式、任务阶段和生成状态均使用文字/图标与颜色共同表达。
- 提供跳转到主要内容链接、可见键盘焦点、dialog 标题、progressbar 语义、tablist 键盘方向键/Home/End 支持。
- `prefers-reduced-motion` 会关闭过渡与呼吸动画。
- Markdown 使用 React 文本节点渲染，不注入未经处理的 HTML。

## 测试结果

执行日期：2026-09-09。

- `npm test`：2 个测试文件、12 项测试全部通过。
- `npm run build`：TypeScript project build 与 Vite production build 通过；109 个模块完成转换。
- `python -m pytest tests/test_platform_mvp.py -q`（`backend` 目录）：4 项接口测试全部通过。
- 浏览器验收：真实 Vite 开发入口与本地 FastAPI 服务连接成功；1440×960 桌面布局、390×844 窄屏布局通过；窄屏 `documentWidth` 与 `viewport` 均为 390px。
- 浏览器交互：文件选择及移除、学习模式、模型设置 dialog、最近项目空状态均正常；控制台 0 error、0 warning。
- 自动化测试覆盖：上传成功/失败重试、资料角色保存、诊断、job 创建与轮询、失败任务、轮询恢复、真实结果内容、卡片翻面、模拟题答题、可用/不可用导出、导出失败和模型配置保存。

验收截图位于 `output/playwright/recallforge-v3-product-home.png` 与 `output/playwright/recallforge-v3-product-mobile.png`。

后端测试输出包含 FastAPI 在 Python 3.14 下的弃用警告，不影响本次测试结果。

## 后续优化建议

以下事项不属于本次 UI 重构，建议按真实使用数据再安排：

1. 将当前内存中的生成任务注册表持久化，确保后端进程重启后仍能恢复任务与下载。
2. 为生成任务补充工作区级授权绑定，避免仅凭 job id 查询或下载。
3. 在后端提供项目与最后一次生成任务的正式关联，取代前端 localStorage 中的恢复索引。
4. 对超长报告和大型卡组做性能采样；确认存在实际瓶颈后再引入分段渲染或虚拟列表。
5. 若桌面发行要求完全离线，随应用打包字体资源，并补充 Windows 缩放比例下的视觉回归截图。
