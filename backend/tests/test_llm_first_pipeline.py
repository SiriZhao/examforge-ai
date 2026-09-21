"""Deterministic acceptance checks for the LLM-first generation boundary."""
from app.schemas.review import LLMConfig, ParsedFile, ParsedPage
from app.services import generation_pipeline as pipeline


class FakeProvider:
    display_name = "fake"
    default_model = "fake-model"

    def __init__(self):
        self.stages = []

    def generate_stage(self, stage, prompt, config, *, max_output_tokens):
        self.stages.append((stage, prompt))
        if stage == "chunk_understanding":
            return {"major_topics": ["shared concept"], "semantic_summary": "evidence from this chunk"}
        if stage == "course_model":
            return {"course_title": "Fixture course", "subject_domain": "other"}
        if stage == "study_blueprint":
            return {"units": [{"title": "Synthesized unit"}]}
        if stage == "unit_draft":
            return {"title": "Synthesized unit", "markdown": "## Synthesized unit\nExplanation across source chunks."}
        return {"canonical_markdown": "# Model-authored review\n\n## Synthesized unit\nExplanation across source chunks."}


def test_pipeline_is_llm_first_and_preserves_canonical_markdown(monkeypatch):
    fake = FakeProvider()
    monkeypatch.setattr(pipeline, "get_llm_provider", lambda _: fake)
    parsed = ParsedFile(
        filename="fixture.txt", file_type=".txt", path="fixture.txt",
        pages=[ParsedPage(page_number=1, text="shared concept", source="text_extract", source_anchor="fixture, p. 1")],
        raw_text="shared concept",
    )
    result, _ = pipeline.generate_hierarchical_report(
        [parsed], None, LLMConfig(enabled=True, provider="openai"),
        job_id="fake", title="Fixture", study_goal="practice_heavy",
        exam_type="programming", detail_level="exhaustive", output_style="practice_training",
    )
    stages = [name for name, _ in fake.stages]
    assert stages[:3] == ["chunk_understanding", "course_model", "study_blueprint"]
    assert "unit_draft" in stages and "course_synthesis" in stages
    assert "Model-authored review" in result.report.markdown
    assert "practice_heavy" in fake.stages[0][1]
    assert "programming" in fake.stages[0][1]
