"""Safe, synthetic fixtures used by LLM-first acceptance tests."""

FIXTURES = {
    "concept": [
        ("c1.txt", "## Memory hierarchy\nCache locality reduces average access time because temporal and spatial locality reuse nearby data."),
        ("c2.txt", "## Virtual memory\nPages map virtual addresses to physical frames; a page fault loads a missing page from storage."),
    ],
    "formula": [
        ("f1.txt", "## Bayes theorem\nP(A|B)=P(B|A)P(A)/P(B). The denominator normalizes posterior probability."),
        ("f2.txt", "## Linear regression\nThe normal equation beta=(X^T X)^-1 X^T y assumes invertibility; regularization changes the solution."),
    ],
    "programming": [
        ("p1.py", "## Binary search\nMaintain low and high bounds. Invariant: the target, if present, remains in the interval.\n```python\nmid=(low+high)//2\n```"),
        ("p2.py", "## Debugging\nAn off-by-one error occurs when the upper bound is treated as both inclusive and exclusive."),
    ],
    "lab": [
        ("l1.txt", "## Enzyme assay\nMeasure absorbance after incubation. The control estimates background signal; temperature changes reaction rate."),
        ("l2.txt", "## Error analysis\nRandom error affects repeatability; systematic calibration error shifts every measurement."),
    ],
    "exam": [
        ("exam.txt", "OBSERVED past exam: derive the normal equation (10 points); explain the effect of regularization (6 points)."),
    ],
    "long": [(f"chapter-{i}.txt", f"## Chapter {i}\nDistinct source region {i}: concept_{i} and evidence_{i}.") for i in range(1, 9)],
}
