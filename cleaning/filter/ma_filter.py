"""Filter papers for Multiagent Systems subset (MA)."""

import re

# Kept for explainability only; MA inclusion is category-driven.
ALL_KEYWORDS = [
    r"\bagent\b",
    r"\bagents\b",
    r"\bmulti[\-\s]?agent\b",
    r"\bagentic\b",
    r"autonomous\s+agent",
    r"LLM[\-\s]?agent",
    r"language\s+model\s+agent",
    r"\bAutoGen\b",
    r"\bCrewAI\b",
    r"\bLangChain\b",
]

_PATTERNS = [re.compile(kw, re.IGNORECASE) for kw in ALL_KEYWORDS]


def _has_category(paper: dict, category: str) -> bool:
    raw = str(paper.get("Categories", "")).strip()
    if not raw:
        return False
    cats = [c.strip() for c in raw.split(";") if c.strip()]
    return category in cats


def _match_keywords(title: str, abstract: str) -> list[str]:
    text = f"{title} {abstract}"
    matched = []
    for pattern, keyword in zip(_PATTERNS, ALL_KEYWORDS):
        if pattern.search(text):
            matched.append(keyword)
    return matched


def filter_ma_papers(papers: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    MA subset rule:
    - Include papers with cs.MA in Categories.
    - Keep keyword hits in metadata as explainability signal.
    """
    matched = []
    annotated = []

    for paper in papers:
        title = str(paper.get("Title", ""))
        abstract = str(paper.get("Abstract", ""))
        keywords = _match_keywords(title, abstract)
        include = _has_category(paper, "cs.MA")

        paper_copy = dict(paper)
        paper_copy["_is_ma"] = include
        paper_copy["_ma_keywords"] = "; ".join(keywords) if keywords else ""
        annotated.append(paper_copy)

        if include:
            matched.append(paper_copy)

    return matched, annotated
