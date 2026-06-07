from app.schemas.review import ReviewReport
from app.services.review_planner import generate_review_report


def analyze_content(
    file_id: str, content: str, focus: str | None = None
) -> ReviewReport:
    return generate_review_report(
        content=content,
        title=f"复习分析报告：{file_id}",
        focus=focus,
    )
