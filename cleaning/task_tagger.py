"""Tag papers with multimodal task labels based on title and abstract keywords."""

import re
import logging
from collections import Counter

logger = logging.getLogger(__name__)

TASK_DEFINITIONS: dict[str, tuple[str, list[str]]] = {
    "MMCLS": ("Multimodal Classification", [
        r"multimodal\s+classification",
        r"vision[\-\s]language\s+classification",
        r"cross[\-\s]modal\s+classification",
    ]),
    "ITR": ("Image-Text Retrieval", [
        r"image[\-\s]text\s+retrieval",
        r"text[\-\s]image\s+retrieval",
        r"cross[\-\s]modal\s+retrieval",
    ]),
    "VQA": ("Visual Question Answering", [
        r"\bVQA\b",
        r"visual\s+question\s+answering",
        r"multimodal\s+question\s+answering",
    ]),
    "IC": ("Image Captioning", [
        r"image\s+captioning",
        r"caption\s+generation",
        r"vision[\-\s]language\s+generation",
    ]),
    "VG": ("Visual Grounding", [
        r"visual\s+grounding",
        r"phrase\s+grounding",
        r"referring\s+expression",
    ]),
    "OVOD": ("Open-Vocabulary Object Detection", [
        r"open[\-\s]vocabulary\s+object\s+detection",
        r"open[\-\s]world\s+object\s+detection",
        r"zero[\-\s]shot\s+object\s+detection",
    ]),
    "OVSEG": ("Open-Vocabulary Segmentation", [
        r"open[\-\s]vocabulary\s+segmentation",
        r"open[\-\s]world\s+segmentation",
        r"zero[\-\s]shot\s+segmentation",
    ]),
    "T2I": ("Text-to-Image Generation", [
        r"text[\-\s]to[\-\s]image",
        r"text[\-\s]conditioned\s+image\s+generation",
        r"prompt[\-\s]to[\-\s]image",
    ]),
    "T2V": ("Text-to-Video Generation", [
        r"text[\-\s]to[\-\s]video",
        r"text[\-\s]conditioned\s+video\s+generation",
    ]),
    "I2T": ("Image-to-Text Generation", [
        r"image[\-\s]to[\-\s]text",
        r"image\s+description\s+generation",
        r"vision\s+to\s+language",
    ]),
    "MRE": ("Multimodal Reasoning", [
        r"multimodal\s+reasoning",
        r"vision[\-\s]language\s+reasoning",
        r"cross[\-\s]modal\s+reasoning",
    ]),
    "MDI": ("Multimodal Dialogue & Instruction", [
        r"multimodal\s+dialog",
        r"visual\s+dialog",
        r"visual\s+instruction\s+tuning",
        r"instruction[\-\s]following",
    ]),
    "MAG": ("Multimodal Agent", [
        r"multimodal\s+agent",
        r"vision[\-\s]language\s+agent",
        r"agentic\s+multimodal",
    ]),
    "TAP": ("Tool-Augmented Perception", [
        r"tool[\-\s]augmented",
        r"tool[\-\s]use",
        r"perception[\-\s]action\s+loop",
        r"test[\-\s]time\s+tool\s+use",
    ]),
}

TASK_NAMES: dict[str, str] = {abbr: name for abbr, (name, _) in TASK_DEFINITIONS.items()}
_COMPILED_TASKS: dict[str, list[re.Pattern]] = {
    abbr: [re.compile(kw, re.IGNORECASE) for kw in keywords]
    for abbr, (_, keywords) in TASK_DEFINITIONS.items()
}


def tag_tasks(title: str, abstract: str) -> list[str]:
    """Match a paper's title+abstract against all task patterns."""
    text = f"{title} {abstract}"
    matched = []
    for abbr, patterns in _COMPILED_TASKS.items():
        if any(p.search(text) for p in patterns):
            matched.append(abbr)
    return matched


def tag_all_papers(papers: list[dict]) -> None:
    """Annotate each paper in-place with a `_tasks` field (semicolon-separated)."""
    counter: Counter = Counter()
    for p in papers:
        title = str(p.get("Title", ""))
        abstract = str(p.get("Abstract", ""))
        tasks = tag_tasks(title, abstract)
        p["_tasks"] = ";".join(tasks) if tasks else ""
        counter.update(tasks)

    logger.info(f"Task tagging complete: {sum(1 for p in papers if p.get('_tasks'))} / {len(papers)} papers tagged")
    for task, count in counter.most_common():
        logger.info(f"  {task} ({TASK_NAMES[task]}): {count}")
