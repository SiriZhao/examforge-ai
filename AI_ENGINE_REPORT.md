# RecallForge AI Engine v3.2 升级报告

## v0.6.0 LLM-first implementation summary (current worktree)

Audit confirmed all twelve requested root causes: the router previously built a complete `safe_draft` before AI; the hierarchical function sanitized/cloned it; the active path used `study_unit_prompt.py` and `generate_study_unit`; intent fields were not passed into that path; template modules were not active; Markdown was rebuilt by `generate_markdown_review`; deterministic planner artifacts dominated; failed chunks became local StudyUnits; merging was list concatenation; quality gates over-weighted question/card counts; and the V4 diagnosis was not production architecture.

The active AI path is now evidence-first: parsed files and source anchors feed flexible `ChunkUnderstanding` artifacts, a global `CourseModel`, an intent-aware `StudyBlueprint`, rich `UnitDraft` Markdown, and a global `canonical_markdown` synthesis. The model may reorganize and write at appropriate length; Python retains parsing, persistence, retries, checkpoints, source refs, validation and exports. The legacy planner and StudyUnit prompt remain compatibility code only.

AI mode no longer creates a safe draft before generation. Offline/basic mode deliberately calls `generate_review_report`. Provider failure enters an explicit offline fallback; partial stage failures are recorded as unresolved/failed status and are never silently converted to local units. Quality validation treats missing Anki/mock artifacts as warnings and scores grounded, coherent Markdown as the primary product.

## V4 quality acceptance

Synthetic acceptance fixtures now cover concept-heavy, formula-heavy, programming, laboratory/science, observed past-exam, and long multi-file material. Acceptance checks measure source coverage, repeated generic advice, duplicate paragraphs, concrete explanation, provenance labels, subject/mode-sensitive planning, targeted unit repair, and canonical export fidelity rather than field counts.

Every infrastructure chunk is persisted in the report overview as a successful `ChunkUnderstanding` or an explicit unresolved item. There is no `MAX_CHUNKS` truncation in the active path. Optional artifacts are requested only for matching study goals/exam modes, and their prompt requires `OBSERVED`, `INFERRED`, and `GENERATED` separation.

Markdown, DOCX, and PDF exports consume canonical Markdown. DOCX conversion now preserves headings, lists, Markdown tables, formulas as text, and fenced code blocks without reconstructing the legacy report template.

A bounded DeepSeek live smoke test completed the four active stages for a small Bayes-theorem fixture and returned grounded canonical Markdown. This validates provider wiring and canonical generation, not broad pedagogical quality across real courses.

## 升级目标

本次升级将长文档处理重构为可追踪的五阶段 Pipeline：

Document → Parser → Structure Analyzer → Knowledge Extractor → Generation Engine → Quality Checker

核心目标是保留文档结构和来源位置，让长材料分块后仍能覆盖不同章节，减少上下文断裂与重复总结，并在输出前自动检查完整性。

## 1. 文档结构理解

### Document Structure JSON

POST /parse 的每个 ParsedFile 现在包含 document_structure，Schema 版本为 3.2。

主要字段：

- document_id：基于文件名和解析文本生成的稳定哈希。
- filename、file_type、title、page_count：文档基本信息。
- sections：包含 section_id、title、level、parent_id、child_ids、page_start、page_end、block_ids 和 source_anchor。
- blocks：包含 block_id、type、page_number、source_anchor、text、rows、metadata 和 confidence。
- warnings：文件级解析警告。

识别能力：

- 标题：支持 Markdown 标题、中文章节、Chapter、Unit、Lecture 和多级数字标题。
- 章节树：记录层级、父子节点、起止页和关联内容块。
- 页码：PDF、Word、文本使用 p. 锚点，PPTX 使用 slide 锚点。
- 表格：Word 与 PPTX 提取原生行列；Markdown、文本和 PDF 文本层使用布局规则恢复行列。
- 图片：记录 Word 内嵌图片、PPTX 图片、PDF 页面图片和独立图片文件的元数据与来源。
- 公式：保留公式原文、所在页码和置信度，不静默改写。
- 页面状态：每页标记 processed、processed_with_warning、skipped_with_reason 或 failed_with_reason，空页和 OCR 警告不会被静默丢弃。

主要实现：

- backend/app/schemas/review.py
- backend/app/services/file_parser.py
- backend/app/services/structure_analyzer.py

## 2. 长文档 Chunk 策略

### 结构优先切分

split_material_chunks 已改为调用语义分块器，按以下优先级切分：

1. 章节和标题边界。
2. 空行与自然段。
3. 超长单段的安全字符窗口。

每个语义块保留 chunk_id、所属章节、来源锚点和与前一块的上下文桥接。

### 防止信息丢失

- 分块器返回全部结构块，不再按分数只保留前 N 个块。
- Knowledge Extractor 在生成前建立章节、定义、公式、表格、图片和待复核页面索引。
- 最终压缩使用均衡配额，让每个 chunk_insight 至少保留一部分，避免只保留文档开头。
- Evidence Pack 继续保留高价值题干和公式，用于重点排序。

### 防止重复总结

- 重叠内容带有“承接上文，仅用于上下文，不要重复总结”标签。
- Chunk Prompt 明确禁止再次总结承接区。
- 合并 chunk_insights 时按规范化文本删除跨块重复行。
- Quality Checker 检查重复专题并触发警告和扣分。

### 防止上下文断裂

- 普通块携带上一块末尾的完整自然段。
- 超长单段携带固定长度的上下文桥接。
- 页面来源锚点和章节标题进入 Generation Engine，模型可判断内容属于哪个文件、页面和章节。

主要实现：

- backend/app/services/chunking.py
- backend/app/services/knowledge_extractor.py
- backend/app/services/llm_service_prompt.py

## 3. Prompt 模板系统

新增 backend/app/templates/，由 Registry 根据 study_goal 和 output_style 选择模板：

| 模式 | 模板 | 主要策略 |
| --- | --- | --- |
| 考试模式 | exam.py | 考试范围、公式条件、题干、答题步骤、冲刺顺序 |
| 理解模式 | understanding.py | 概念依赖、原因、条件、例子和来源页码 |
| 记忆模式 | memory.py | 定义、公式、对比、易混点、主动回忆卡片与去重 |
| 刷题模式 | practice.py | 题型、题目、答案、解析、章节覆盖和来源依据 |

模板指令会与现有考试类型、详细度和输出风格策略组合，不改变原有请求字段。

## 4. Quality Checker

新增独立质量检查器，并接入现有 LLM 自动修复门槛。

检查项：

- 空内容：正文为空或短到无法使用时直接失败。
- 章节覆盖：从材料结构提取预期章节，输出覆盖率和缺失章节。
- 重复内容：检测重复或高度相似的专题名称。

ReportQuality 新增：

- section_coverage_ratio
- missing_sections
- duplicate_sections
- is_empty

对于多章节材料，覆盖率低于 50% 会触发失败并进入现有自动修复；覆盖率低于 80% 会产生警告。检查会先去除重复页眉，并优先使用 study_units，避免将兼容映射到 chapters 的同一专题误判为重复。

主要实现：

- backend/app/services/quality_checker.py
- backend/app/services/llm_quality.py

## 5. Pipeline 集成

生成端点保持原有请求和主要响应兼容。内部执行顺序调整为：

1. Parser 解析原生文本或 OCR。
2. Structure Analyzer 构建 Document Structure JSON。
3. Knowledge Extractor 建立来源可追踪的知识索引。
4. Generation Engine 使用结构化材料、语义块和对应模式模板生成。
5. Quality Checker 检查空内容、章节覆盖和重复，并复用原有一次自动修复及安全底稿回退。
6. 原有 Markdown、Word、PDF 和 Anki 导出继续执行。

处理进度新增“分析标题、章节树、页码、表格和图片”与“知识提取”阶段。

## 6. 测试结果

验证日期：2026-09-09

| 验证项 | 结果 |
| --- | --- |
| v3.2 专项与解析回归测试 | 17/17 通过 |
| 完整后端测试套件 | 84/84 通过 |
| Python 全模块编译检查 | 通过 |

新增测试覆盖：

- Document Structure JSON、章节树、页码锚点、表格与公式块。
- 多章节语义分块、最大块长度、上下文桥接。
- Knowledge Extractor 来源锚点与待复核页面。
- 四类 Prompt 模板路由。
- 跨块均衡压缩与重复行删除。
- 空输出、缺失章节和重复专题检查。
- 原有上传、OCR、生成、自动修复和导出回归。

测试输出中的 FastAPI 弃用警告来自当前依赖版本，不影响功能和测试结果。

## 7. 后续优化建议

1. 为复杂图表、流程图和公式增加视觉模型结构化解析，并与原生文本证据分开保存。
2. 将 Document Structure 和 Knowledge Extraction 持久化到项目数据库，避免重复解析同一文件。
3. 当文档达到数百个 Chunk 时增加多层 Map-Reduce 合成与可恢复任务队列。
4. 使用真实课程长文档建立覆盖率、事实一致性、重复率和来源可追踪率的离线评测集。
