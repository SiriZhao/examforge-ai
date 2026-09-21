from __future__ import annotations
import re
from collections import Counter
from dataclasses import dataclass, field

@dataclass
class QualityReport:
    score: int
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)
    needs_repair: bool = False

def lint_study_unit(unit) -> QualityReport:
    fields = [*unit.must_know, *unit.key_points, *unit.formulas_or_methods, *unit.common_exam_angles, *unit.pitfalls]
    norm = [re.sub(r'\s+', ' ', x).strip().casefold() for x in fields if x.strip()]
    failures=[]; warnings=[]
    dup=sum(c-1 for c in Counter(norm).values() if c>1)
    joined=' '.join(norm)
    if dup: failures.append(f'duplicate_items:{dup}')
    if not fields: failures.append('empty_unit')
    if any(p in joined for p in ('根据上述内容','将在第','模型调用未完成','保留可恢复底稿')): failures.append('generic_or_recovery_text')
    if len(norm) >= 3 and len(set(norm)) / len(norm) < .7: failures.append('low_specificity')
    score=max(0, min(100, 100-25*len(failures)-min(20,dup*5)))
    return QualityReport(score, failures, warnings, {'duplication': dup/ max(len(norm),1)}, bool(failures))
