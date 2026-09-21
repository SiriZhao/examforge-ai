from typing import Literal

from app.schemas.review import OutputStyle, StudyGoal
from app.templates import exam, memory, practice, understanding

PromptMode = Literal["exam", "understanding", "memory", "practice"]

TEMPLATES: dict[PromptMode, str] = {
    "exam": exam.INSTRUCTION,
    "understanding": understanding.INSTRUCTION,
    "memory": memory.INSTRUCTION,
    "practice": practice.INSTRUCTION,
}


def get_prompt_template(study_goal: StudyGoal, output_style: OutputStyle) -> tuple[PromptMode, str]:
    if study_goal in {"memorization", "anki_focused"} or output_style == "anki_cards":
        mode: PromptMode = "memory"
    elif study_goal == "practice_heavy" or output_style == "practice_training":
        mode = "practice"
    elif study_goal in {"one_day_sprint", "three_day_sprint", "past_exam_focused"} or output_style == "sprint":
        mode = "exam"
    else:
        mode = "understanding"
    return mode, TEMPLATES[mode]
