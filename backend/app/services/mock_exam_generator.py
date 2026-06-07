from app.schemas.review import MockExamQuestion, ReviewReport
from app.services.review_planner import INSUFFICIENT_MESSAGE


def generate_mock_exam(report: ReviewReport, count: int) -> tuple[list[MockExamQuestion], str]:
    insufficient = bool(report.insufficient_materials) or report.high_frequency_points == [
        INSUFFICIENT_MESSAGE
    ]
    target_count = min(count, 4 if insufficient else count)
    questions: list[MockExamQuestion] = []

    chapters = sorted(report.chapters, key=lambda item: item.importance, reverse=True)
    if not chapters:
        return [], f"{INSUFFICIENT_MESSAGE} 无法生成模拟题。"

    for chapter in chapters:
        concepts = chapter.keywords or [chapter.chapter]
        for concept in concepts[:3]:
            if len(questions) >= target_count:
                break
            question_type = chapter.question_types[0] if chapter.question_types else "简答题"
            questions.append(
                MockExamQuestion(
                    question=make_question(question_type, chapter.chapter, concept),
                    answer=make_answer(question_type, concept, chapter.review_advice),
                    chapter=chapter.chapter,
                    concept=concept,
                    question_type=question_type,
                )
            )
        if len(questions) >= target_count:
            break

    message = f"已生成 {len(questions)} 道模拟题。"
    if insufficient:
        message += f" {INSUFFICIENT_MESSAGE} 已减少题量。"
    return questions, message


def make_question(question_type: str, chapter: str, concept: str) -> str:
    if question_type == "选择题":
        return f"【选择题】关于 {chapter} 中的“{concept}”，下列说法哪一项最准确？"
    if question_type == "计算题":
        return f"【计算题】围绕 {chapter} 的“{concept}”设计一道典型计算题，并写出关键步骤。"
    if question_type == "判断题":
        return f"【判断题】判断“{concept} 是 {chapter} 的核心考点之一”是否正确，并说明理由。"
    if question_type == "填空题":
        return f"【填空题】{chapter} 中与“{concept}”相关的核心结论是：____。"
    if question_type == "论述题":
        return f"【论述题】结合材料论述 {chapter} 中“{concept}”的作用和常见考法。"
    return f"【简答题】简述 {chapter} 中“{concept}”的定义、用途和常见考法。"


def make_answer(question_type: str, concept: str, advice: str) -> str:
    if question_type == "选择题":
        return f"参考答案：应选择最能体现“{concept}”定义、适用条件和边界的选项。复习提示：{advice}"
    if question_type == "计算题":
        return f"参考答案：先写出与“{concept}”相关公式，再代入条件分步求解。复习提示：{advice}"
    return f"参考答案：围绕“{concept}”说明核心概念、适用场景和易错点。复习提示：{advice}"
