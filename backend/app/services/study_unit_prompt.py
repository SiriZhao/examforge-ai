from __future__ import annotations

from app.services.llm_capabilities import estimate_tokens


STUDY_UNIT_SYSTEM_PROMPT = (
    "You are a university study coach. Return strict, complete, compact JSON only, "
    "with no reasoning or wrapper."
)


def build_study_unit_prompt(chapter_title: str, chunk_text: str, *, concise: bool) -> str:
    detail = "Use at most four concise items per array." if concise else "Use at most six specific items per array."
    return (
        "Create one StudyUnit from only this chapter chunk. Do not synthesize the whole document, "
        "do not output Markdown, do not include analysis, and do not copy long source passages. "
        f"Chapter: {chapter_title}. {detail} "
        "Keep reason and how_to_review under 120 characters, and every array item under 120 characters. "
        "Return exactly one JSON object with fields name, reason, priority, must_know, key_points, "
        "formulas_or_methods, common_exam_angles, pitfalls, and how_to_review.\n\n"
        f"Chapter chunk:\n{chunk_text}"
    )


def estimate_study_unit_prompt_tokens(
    chapter_title: str,
    chunk_text: str,
    *,
    concise: bool,
    model: str | None,
) -> int:
    prompt = build_study_unit_prompt(chapter_title, chunk_text, concise=concise)
    return estimate_tokens(STUDY_UNIT_SYSTEM_PROMPT, model) + estimate_tokens(prompt, model) + 32
