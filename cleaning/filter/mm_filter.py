"""Filter papers for multimodal subset (MM)."""

import re

# Core multimodal terms
CORE_KEYWORDS = [
    r"\bmultimodal\b",
    r"\bmulti[\-\s]modal\b",
    r"vision[\-\s]language",
    r"visual[\-\s]language",
    r"image[\-\s]text",
    r"text[\-\s]image",
    r"cross[\-\s]modal",
    r"multi[\-\s]modal\s+large\s+language",
    r"multimodal\s+large\s+language",
    r"\bMLLM\b",
    r"\bLMM\b",
    r"\bVLM\b",
]

# Model names
MODEL_KEYWORDS = [
    r"\bCLIP\b",
    r"\bOpenCLIP\b",
    r"\bSigLIP\b",
    r"\bALIGN\b",
    r"\bBLIP\b",
    r"\bBLIP[\-\s]?2\b",
    r"\bInstructBLIP\b",
    r"\bLLaVA\b",
    r"\bQwen[\-\s]?VL\b",
    r"\bInternVL\b",
    r"\bFlamingo\b",
    r"\bCogVLM\b",
    r"\bGemini\b",
    r"\bGPT[\-\s]?4[Vv]?\b",
]

# Task terms
TASK_KEYWORDS = [
    r"visual\s+question\s+answering",
    r"\bVQA\b",
    r"image\s+captioning",
    r"visual\s+grounding",
    r"phrase\s+grounding",
    r"image[\-\s]text\s+retrieval",
    r"text[\-\s]to[\-\s]image",
    r"image[\-\s]to[\-\s]text",
    r"vision[\-\s]language\s+pre[\-\s]?train",
]

ALL_KEYWORDS = CORE_KEYWORDS + MODEL_KEYWORDS + TASK_KEYWORDS
_PATTERNS = [re.compile(kw, re.IGNORECASE) for kw in ALL_KEYWORDS]


def is_mm_related(title: str, abstract: str) -> tuple[bool, list[str]]:
    """Check whether a paper is multimodal-related by keyword hit."""
    text = f"{title} {abstract}"
    matched = []
    for pattern, keyword in zip(_PATTERNS, ALL_KEYWORDS):
        if pattern.search(text):
            matched.append(keyword)
    return len(matched) > 0, matched


def _has_category(paper: dict, category: str) -> bool:
    raw = str(paper.get("Categories", "")).strip()
    if not raw:
        return False
    cats = [c.strip() for c in raw.split(";") if c.strip()]
    return category in cats


def filter_mm_papers(papers: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    MM subset rule:
    - Include all papers with cs.MM in Categories.
    - Include cs.CV papers only when multimodal keywords are hit.
    """
    matched = []
    annotated = []

    for paper in papers:
        title = str(paper.get("Title", ""))
        abstract = str(paper.get("Abstract", ""))
        text_hit, keywords = is_mm_related(title, abstract)
        is_mm_cat = _has_category(paper, "cs.MM")
        is_cv_cat = _has_category(paper, "cs.CV")
        include = is_mm_cat or (is_cv_cat and text_hit)

        paper_copy = dict(paper)
        paper_copy["_is_mm"] = include
        paper_copy["_mm_keywords"] = "; ".join(keywords) if keywords else ""
        annotated.append(paper_copy)

        if include:
            matched.append(paper_copy)

    return matched, annotated
