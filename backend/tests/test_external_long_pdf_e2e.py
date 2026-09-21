from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

import pytest
from docx import Document
from fastapi.testclient import TestClient
from pypdf import PdfReader

from app.config import settings
from app.main import app
from app.schemas.review import GenerateReviewResponse, LLMConfig, OCRConfig, StudyUnit
from app.services import generation_store
from app.services.file_parser import parse_file
from app.services.generation_pipeline import generate_hierarchical_report
from app.services.generator import generate_markdown_review
from app.services.llm_providers import get_llm_provider
from app.services.review_planner import generate_review_report


def test_external_long_pdf_e2e(monkeypatch) -> None:
    raw_path = os.getenv("RECALLFORGE_E2E_PDF")
    if not raw_path:
        pytest.skip("RECALLFORGE_E2E_PDF is not configured")
    source = Path(raw_path).resolve()
    repository_root = Path(__file__).resolve().parents[2]
    assert source.is_file() and source.suffix.lower() == ".pdf"
    assert not source.is_relative_to(repository_root)

    with TemporaryDirectory(prefix="RecallForge-e2e-") as temporary:
        root = Path(temporary)
        monkeypatch.setattr(settings, "storage_dir", root)
        monkeypatch.setattr(settings, "ocr_cache_dir", root / "ocr-cache")
        monkeypatch.setattr(settings, "output_dir", root / "exports")
        monkeypatch.setenv("RECALLFORGE_JOB_DB", str(root / "generation.sqlite3"))

        # This supplied textbook has a complete native text layer. Fast mode
        # verifies the production parser's preferred path (native extraction
        # plus OCR fallback only for weak pages) without needlessly OCRing all
        # 136 pages a second time.
        parsed = parse_file(source, OCRConfig(provider="rapidocr", mode="fast"))
        assert len(parsed.pages) == 136
        assert parsed.raw_text.strip()
        assert parsed.document_structure
        assert parsed.document_structure.sections

        live_llm = os.getenv("RECALLFORGE_E2E_LLM", "").strip() == "1"
        provider_name = (settings.default_llm_provider or "deepseek") if live_llm else "openai"
        provider = get_llm_provider(provider_name)
        provider_key = (
            settings.deepseek_api_key if provider_name == "deepseek" else settings.openai_api_key
        ) if live_llm else "local-e2e-key-never-sent"
        model = settings.default_llm_model or provider.default_model
        config = LLMConfig(
            provider=provider_name,
            model=model,
            base_url=settings.default_llm_base_url or provider.default_base_url,
            api_key=provider_key or None,
            enabled=True,
        )
        if not live_llm:
            def deterministic_study_unit(chapter_title, chunk_text, *_args, **_kwargs):
                return StudyUnit(
                    name=chapter_title,
                    reason="External PDF hierarchy test",
                    priority=80,
                    must_know=[f"当前语义块包含 {len(chunk_text)} 个字符"],
                    key_points=[chapter_title],
                    formulas_or_methods=[],
                    common_exam_angles=["按章节复习并核对原始页码"],
                    pitfalls=["不要脱离教材来源"],
                    how_to_review="先主动回忆，再对照教材核验。",
                )

            monkeypatch.setattr(provider, "generate_study_unit", deterministic_study_unit)
        job_id = f"external-e2e-{uuid4().hex}"
        generation_store.create_or_resume(
            job_id,
            {
                "files": [str(source)],
                "project_id": "external-e2e",
                "llm_config": config.model_dump(mode="json"),
            },
        )
        generation_store.save_parsed(job_id, [parsed.model_dump(mode="json")])

        safe_draft = generate_review_report(parsed.raw_text, title="Linear Algebra")
        result, stats = generate_hierarchical_report(
            [parsed],
            safe_draft,
            config,
            job_id=job_id,
            checkpoint_callback=lambda key, chapter, chunk, status, content, code, message: generation_store.save_checkpoint(
                job_id,
                key,
                chapter,
                chunk,
                status,
                content,
                code,
                message,
            ),
        )
        markdown = generate_markdown_review(result.report)
        assert stats.chapter_count > 0
        assert stats.chunk_count > 0
        assert stats.chapter_count > 1, "P0 regression: long PDF collapsed to one chapter"
        assert stats.chunk_count > 1, "P0 regression: long PDF collapsed to one chunk"
        assert result.report.study_units or result.report.chapters
        assert markdown.strip()
        if result.llm_status != "success":
            assert result.llm_error
            assert result.llm_error.code in {
                "CONFIG_MISSING",
                "AUTH_FAILED",
                "MODEL_NOT_FOUND",
                "PROVIDER_RATE_LIMIT",
                "PROVIDER_QUOTA_EXCEEDED",
                "LLM_TIMEOUT",
                "LLM_PROVIDER_ERROR",
                "LLM_RESPONSE_PARSE_ERROR",
                "LLM_OUTPUT_TRUNCATED",
                "LLM_CONTEXT_EXCEEDED",
            }

        response = GenerateReviewResponse(
            review_report=result.report,
            markdown=markdown,
            export_format="docx",
            report_source=result.report_source,
            llm_status=result.llm_status,
            fallback_used=result.fallback_used,
            llm_error=result.llm_error,
            llm_context_strategy=result.llm_context_strategy,
        )
        generation_store.update_job(
            job_id,
            status="completed" if result.llm_status == "success" else "partial",
            progress=100,
            message="External E2E generation persisted.",
            result=response.model_dump(mode="json"),
            error_code=result.llm_error.code if result.llm_error else None,
            error_message=result.llm_error.message if result.llm_error else None,
            retryable=bool(result.llm_error and result.llm_error.can_retry),
        )

        checkpoints = generation_store.load_checkpoints(job_id)
        assert checkpoints
        assert all(
            item["status"] == "completed"
            or (
                item["status"] in {"retryable_failed", "failed"}
                and item["error_code"]
                and item["error_code"] != "GENERATION_UNKNOWN_ERROR"
            )
            for item in checkpoints.values()
        )

        monkeypatch.setattr(
            provider,
            "generate_study_unit",
            lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("Export must not call the LLM")),
        )
        client = TestClient(app)
        exported_response = client.get(f"/api/review/jobs/{job_id}/download/docx")
        assert exported_response.status_code == 200
        output_files = list((root / "exports").glob("*.docx"))
        assert len(output_files) == 1
        output = output_files[0]
        assert output.exists() and output.stat().st_size > 0
        reopened = Document(output)
        assert any(paragraph.text.strip() for paragraph in reopened.paragraphs)
        assert len(PdfReader(str(source)).pages) == 136
        persisted = generation_store.get_job(job_id)
        assert persisted and persisted["result"] and persisted["export_status"]["docx"]["status"] == "completed"

        print(
            {
                "page_count": len(parsed.pages),
                "chapter_count": stats.chapter_count,
                "chunk_count": stats.chunk_count,
                "llm_calls": stats.llm_calls,
                "retry_count": stats.retry_count,
                "generation_result": result.llm_status,
                "provider_error": result.llm_error.code if result.llm_error else None,
                "export_result": "success",
                "export_size": output.stat().st_size,
                "provider_mode": "live" if live_llm else "deterministic_local",
            }
        )
