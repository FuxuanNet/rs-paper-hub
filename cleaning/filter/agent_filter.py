"""Filter papers related to Agent / Autonomous Decision-Making in Remote Sensing."""

import re

# ============================================================
# Keyword lists
# ============================================================

# 核心概念关键词 — agent 直接表述（命中即入选）
CORE_KEYWORDS = [
    # Agent 直接表述
    r"\bagent\b",
    r"\bagents\b",
    r"\bagentic\b",
    r"multi[\-\s]?agent",
    r"LLM[\-\s]based\s+agent",
    r"LLM\s+agent",
    r"language\s+model\s+agent",
    r"autonomous\s+agent",
    r"intelligent\s+agent",
    r"AI\s+agent",
    # Agent 相关核心动词/名词
    r"tool[\-\s](?:use|using|usage|call|calling)",
    r"tool[\-\s]augmented",
    r"\bagentic\s+(?:workflow|pipeline|framework|system|reasoning)",
    # Autonomous reasoning / workflow (agent-like behavior)
    r"autonomous(?:ly)?\s+(?:explore|reason|plan|decide|construct).{0,40}(?:workflow|inference|path|pipeline)",
    r"(?:reasoning|autonomous)\s+workflow",
]

# 知名 Agent 框架/模型名（命中即入选）
MODEL_KEYWORDS = [
    r"\bReAct\b",
    r"\bAutoGPT\b",
    r"\bAuto[\-\s]GPT\b",
    r"\bBabyAGI\b",
    r"\bLangChain\b",
    r"\bAutoGen\b",
    r"\bCrewAI\b",
    r"\bMetaGPT\b",
    # RS-specific agent models
    r"\bRemoteAgent\b",
    r"\bGeoAgent\b",
    r"\bEarthAgent\b",
    r"\bMapAgent\b",
    r"\bGeoLLM[\-\s]Agent\b",
]

# 相关任务关键词 — 需要结合遥感/地理上下文
TASK_KEYWORDS = [
    # RL / decision in RS context
    r"reinforcement\s+learning.{0,60}(?:remote\s+sensing|satellite|aerial|UAV|drone|earth\s+observation|hyperspectral|geospatial)",
    r"(?:remote\s+sensing|satellite|aerial|UAV|drone|earth\s+observation|hyperspectral|geospatial).{0,60}reinforcement\s+learning",
    r"deep\s+reinforcement\s+learning.{0,60}(?:remote|satellite|aerial|UAV|drone|earth|band\s+selection|target|detection|navigation|scheduling)",
    r"(?:remote|satellite|aerial|UAV|drone|earth|band\s+selection|target|detection|navigation|scheduling).{0,60}deep\s+reinforcement\s+learning",
    # Autonomous decision / planning in RS
    r"autonomous.{0,30}(?:exploration|decision|planning|navigation|scheduling).{0,60}(?:remote|satellite|aerial|UAV|drone|earth)",
    r"(?:remote|satellite|aerial|UAV|drone|earth).{0,60}autonomous.{0,30}(?:exploration|decision|planning|navigation|scheduling)",
    # Task planning with LLM/AI
    r"task\s+planning.{0,40}(?:LLM|language\s+model|foundation\s+model|AI)",
    r"(?:LLM|language\s+model|foundation\s+model|AI).{0,40}task\s+planning",
]

# 全部合并
ALL_KEYWORDS = CORE_KEYWORDS + MODEL_KEYWORDS + TASK_KEYWORDS

# 预编译
_PATTERNS = [re.compile(kw, re.IGNORECASE) for kw in ALL_KEYWORDS]


def is_agent_related(title: str, abstract: str) -> tuple[bool, list[str]]:
    """
    Check if a paper is related to Agent / Autonomous Decision-Making.

    Args:
        title: Paper title
        abstract: Paper abstract

    Returns:
        (is_match, matched_keywords) - whether it matches and which keywords hit
    """
    text = f"{title} {abstract}"
    matched = []

    for pattern, keyword in zip(_PATTERNS, ALL_KEYWORDS):
        if pattern.search(text):
            matched.append(keyword)

    return len(matched) > 0, matched


def filter_agent_papers(papers: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Filter papers related to Agent / Autonomous Decision-Making.

    Returns:
        (matched_papers, all_papers_with_agent_flag)
        - matched_papers: only agent-related papers (with _agent_keywords field)
        - all_papers_with_agent_flag: all papers with _is_agent and _agent_keywords fields added
    """
    matched = []
    annotated = []

    for paper in papers:
        title = str(paper.get("Title", ""))
        abstract = str(paper.get("Abstract", ""))
        is_match, keywords = is_agent_related(title, abstract)

        paper_copy = dict(paper)
        paper_copy["_is_agent"] = is_match
        paper_copy["_agent_keywords"] = "; ".join(keywords) if keywords else ""
        annotated.append(paper_copy)

        if is_match:
            matched.append(paper_copy)

    return matched, annotated
