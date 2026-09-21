# RecallForge V4 Generation Engine Diagnosis

## Audit scope
Reviewed `generation_pipeline.py`, `generation_store.py`, `generate_review_jobs_v31.py`, structure analysis, semantic chunking, review schemas, provider adapters, quality/planner services, exporters, and key frontend renderers.

## Architecture before
The retired path parsed/OCRed files, created a shallow `DocumentStructure`, called `provider.generate_study_unit` per chunk, merged StudyUnits, and rebuilt a deterministic report. That path remains only as compatibility code for older tests and deliberate offline mode.

## Active production path

Normal AI mode in `generate_review.py` calls `generate_hierarchical_report` without a safe draft. The active implementation in `generation_pipeline.py` builds source chapters/chunks, calls provider `generate_stage` for `chunk_understanding`, then global `course_model`, `study_blueprint`, per-unit `unit_draft`, and `course_synthesis`. The resulting `canonical_markdown` is stored on `ReviewReport.markdown` and passed unchanged to Markdown, DOCX, and PDF exporters. `ReviewReport.overview` retains CourseModel, Blueprint, ChunkUnderstanding, unit status, and source coverage diagnostics. If a stage fails, the chunk is explicitly unresolved/failed; only a catastrophic complete-pipeline failure enters Basic Offline Review.

Python owns parsing/OCR, source anchors, checkpoints, provider budgets, retries, validation, persistence, and export. The LLM owns course interpretation, blueprint structure, explanation depth, cross-chapter relationships, and canonical writing.

## Root causes of observed quality failures

1. **136 pages -> one chapter/chunk.** `analyze_document_structure` only recognizes headings emitted by `detect_chapter_title`/simple markdown/numbering. When extraction has no matching heading, `build_section_tree` intentionally creates one fallback section spanning every page. `_select_chapter_sections` then accepts that fallback. There is no page-count anomaly gate, TOC/bookmark/layout/semantic reconstruction, or mandatory re-segmentation, so a catastrophic structure is treated as valid.
2. **Chunking is text-size first.** `split_semantic_chunks` groups blank-line units and only uses headings it can regex-match. It adds overlap text to prompts; overlap is not represented as evidence to exclude from output and is later merged without semantic identity, causing repeated sentences and concepts.
3. **Generation is chunk-summary composition.** The pipeline invokes a single StudyUnit writer directly against OCR text. There is no stable course-level intermediate model, concept IDs, source-fragment graph, blueprint, or cross-unit synthesis. Merging therefore concatenates partially overlapping summaries rather than merging knowledge.
4. **Schema is presentation-oriented.** `StudyUnit` contains free-form lists (`must_know`, `key_points`, etc.) without concepts, relationships, source refs, provenance, learning objectives, or quality state. Facts cannot be traced or deduplicated reliably.
5. **Prompts/providers permit generic prose.** Provider normalization accepts structurally valid JSON as success; parse success is effectively generation success. Fallback/local units can be surfaced in the same report path. There is no deterministic filler/repetition lint before publication and no targeted repair loop.
6. **Chapter semantics are weak.** Heading detection is page-local, deduplicates titles globally per page only, and does not use bookmarks, typography, slide titles, TOC, repeated headers, page transitions, or topic shifts. Section page ranges can also assign broad ranges to multiple headings.
7. **Mind map is not a graph.** Existing report/frontend models expose summaries and a map renderer but no typed `nodes`/`edges`; bullets are used as a visual proxy, so prerequisite/contrast/derivation relationships are absent.
8. **Recall/questions are downstream text transforms.** Flashcards and questions are generated from report text/planner heuristics, with no question blueprint, concept linkage, active-recall taxonomy, or leakage checks.
9. **Mock exams lack an exam model.** Existing generated questions have loose fields; quality checks count fields/questions but do not enforce topic coverage, difficulty/type distributions, score/time, learning-objective coverage, discrimination, or rubric points.
10. **Quality scoring is shallow.** `llm_quality` computes completeness/keyword-style scores after generation. It does not combine groundedness, source alignment, duplication, specificity, factual consistency, or exam relevance, and it cannot repair a specific failed unit.
11. **Failure states are ambiguous.** Pipeline creates local safe units after provider circuit errors and labels the response as partial/fallback; UI can render those units as study content. There is no per-unit READY/PARTIAL/NEEDS_REPAIR/FAILED contract or chapter retry UX.
12. **Caching is incomplete.** SQLite correctly persists parsed files/checkpoints and decouples exports, but artifacts are keyed mainly by request fingerprint and chunk checkpoints. Course model, blueprint, graph, questions, and exams are not independently versioned/reusable.

## V4 design
Introduce versioned artifacts: `DocumentModel -> CourseModel -> StudyBlueprint -> StudyUnit[] -> CourseSynthesis -> QualityReport -> CanonicalStudyMaterial`. Each artifact stores schema version, source hash, prompt/provider metadata, status, and diagnostics. Core entities are Concepts, Formulas, Examples, Objectives, ExamSignals, SourceRefs, and typed Relationships. User-visible content is generated only from CourseModel/Blueprint; OCR recovery remains diagnostic.

Structure reconstruction combines parser metadata, bookmarks/TOC, typography and numbering, slide titles, repeated-header removal, page transitions, and semantic topic classification. Add sanity checks (especially long-document one-section/one-chunk anomaly) that force alternate segmentation or mark NEEDS_REPAIR.

Use evidence-aware chunks with complete definition/formula/example boundaries and overlap IDs excluded during synthesis. Extract concepts first, normalize aliases, assign stable IDs/source refs, then build graph and learning/exam signals. Generate chapter blueprints before prose. Generate units with provenance and status, synthesize cross-chapter dependencies, run deterministic lint, then LLM critic only for failures, followed by targeted repair and final dedupe.

Add subject profiles (generic engine plus domain hints), active-recall question blueprints, exam blueprints with coverage/difficulty/type constraints, and three first-class features: recommended learning path, teacher-likely-exam signals, and 30-minute last-minute review/contrast cards. Preserve SQLite jobs, resume, OCR cache, canonical persistence, independent exporters, provider diagnostics, budgets/retries/timeouts, and privacy controls.

## Completion gates
V4 is READY only after long-document segmentation, semantic golden fixtures, duplicate/filler rejection, graph edge validation, active-recall and exam blueprint tests, critic+repair tests, checkpoint resume, exporter isolation, frontend build, and separate fake/live-provider reports pass. Missing credentials are reported as `BLOCKED_CREDENTIAL`, never as a live-provider pass.

## Acceptance evidence in this worktree

`backend/tests/test_llm_first_acceptance.py` and `backend/tests/test_llm_first_pipeline.py` provide deterministic provider tests for stage ordering, intent propagation, subject/mode variation, long-document coverage, targeted unit repair, canonical Markdown, and generic-advice rejection. These are fake-provider acceptance tests; they do not claim live provider quality.
