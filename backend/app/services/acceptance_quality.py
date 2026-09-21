"""Deterministic quality signals for LLM-first acceptance tests.

These checks intentionally measure usefulness and grounding signals rather than
requiring a fixed report schema.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


GENERIC_ADVICE = ("掌握重点", "加强理解", "多做练习", "查漏补缺")


@dataclass
class CanonicalQuality:
    source_terms_covered: set[str] = field(default_factory=set)
    missing_source_terms: set[str] = field(default_factory=set)
    generic_advice_count: int = 0
    repeated_paragraphs: int = 0
    has_observed_inferred_generated_labels: bool = False
    has_concrete_evidence: bool = False

    @property
    def acceptable(self) -> bool:
        return (
            not self.missing_source_terms
            and self.generic_advice_count <= 2
            and self.repeated_paragraphs == 0
            and self.has_concrete_evidence
        )


def evaluate_canonical_markdown(markdown: str, source_terms: list[str]) -> CanonicalQuality:
    text = markdown or ""
    paragraphs = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    normalized = [p.casefold() for p in paragraphs]
    counts = {p: normalized.count(p) for p in set(normalized)}
    terms = {term for term in source_terms if term and term.casefold() in text.casefold()}
    missing = {term for term in source_terms if term and term.casefold() not in text.casefold()}
    generic = sum(text.casefold().count(phrase.casefold()) for phrase in GENERIC_ADVICE)
    concrete = bool(re.search(r"\b(?:because|therefore|when|if|derive|algorithm|formula|步骤|因为|因此|条件|例题|实验)\b", text, re.I))
    labels = all(label in text for label in ("OBSERVED", "INFERRED", "GENERATED"))
    return CanonicalQuality(
        source_terms_covered=terms,
        missing_source_terms=missing,
        generic_advice_count=generic,
        repeated_paragraphs=sum(count - 1 for count in counts.values() if count > 1),
        has_observed_inferred_generated_labels=labels,
        has_concrete_evidence=concrete,
    )
