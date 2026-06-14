from app.services.chapter_extractor import is_bad_unit_title
from app.services.concept_extractor import extract_formulas
from app.services.frequency_analyzer import high_frequency_points
from app.services.text_quality import (
    clean_formula_text,
    clean_topic_list,
    looks_like_formula_fragment,
    safe_download_filename,
)


FORMULA_FRAGMENTS = [
    "2 ( ) 2[ ( ) ( )] 2u du□",
    "22 2( ) [ ( )] .9D X E X E X= -",
    "0 =1%V9",
    "1 +1",
    "2 3,",
    "500 之间的概率。（",
    "P(X≥k)",
]


def test_formula_fragments_are_not_unit_titles() -> None:
    for value in FORMULA_FRAGMENTS:
        assert looks_like_formula_fragment(value) or is_bad_unit_title(value)
        assert is_bad_unit_title(value)


def test_formula_fragments_are_preserved_as_content() -> None:
    text = "随机变量的方差公式：D(X)=E[X^2]-[E(X)]^2\n2 ( ) 2[ ( ) ( )] 2u du□"
    formulas = extract_formulas(text, limit=5)

    assert any("D(X)" in item or "E[X" in item for item in formulas)
    assert clean_formula_text("2 ( ) 2[ ( ) ( )] 2u du□")


def test_bad_high_frequency_topic_names_are_filtered() -> None:
    values = ["每题", "的值", "其他", "未知", "系主任 出卷人", "则袋中白球的", "2 ( ) 2[ ( ) ( )] 2u du□", "随机变量", "概率密度"]

    assert clean_topic_list(values, limit=10) == ["随机变量", "概率密度"]


def test_high_frequency_points_do_not_show_formula_noise() -> None:
    points = high_frequency_points(
        {
            "2 ( ) 2[ ( ) ( )] 2u du□": [
                type("Question", (), {"keywords": ["每题", "概率密度", "P(X≥k)"]})(),
            ]
        }
    )

    assert points == ["重要专题 1: 概率密度"]


def test_safe_download_filename_keeps_course_name_and_cleans_illegal_chars() -> None:
    assert safe_download_filename("概率论", "复习资料包", "md") == "概率论_复习资料包.md"
    assert safe_download_filename("概率论", "Anki卡片", "csv") == "概率论_Anki卡片.csv"
    assert safe_download_filename('Python:/期末*考试?', "复习资料包", "pdf") == "Python期末考试_复习资料包.pdf"
