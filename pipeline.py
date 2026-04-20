#!/usr/bin/env python3
"""
One-click pipeline: clean all data + filter MM/MA + classify.

Usage:
    python pipeline.py                # Process output/papers.json
    python pipeline.py --input x.json # Custom input
"""

import os
import json
import argparse
import logging
from collections import Counter

import pandas as pd

from cleaning.abstract_cleaner import clean_abstract
from cleaning.filter.mm_filter import filter_mm_papers
from cleaning.filter.ma_filter import filter_ma_papers
from cleaning.classifier import classify_papers
from cleaning.task_tagger import tag_all_papers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

ALL_COLUMNS = [
    "PrimaryCategory", "Categories",
    "Category", "Type", "Subtype", "Date", "Month", "Year", "Institute",
    "Title", "abbr.", "Paper_link", "Abstract",
    "code", "Publication", "BibTex", "Authors", "_tasks",
]

SUBSET_COLUMNS = ALL_COLUMNS

LEGACY_OUTPUT_FILES = [
    "papers_vlm.csv",
    "papers_vlm.json",
    "papers_vlm_annotated.json",
    "papers_agent.csv",
    "papers_agent.json",
    "papers_agent_annotated.json",
    "feed_vlm.xml",
    "feed_agent.xml",
]


def save(papers: list[dict], csv_path: str, json_path: str, columns: list[str]):
    """Save papers to CSV + JSON, NaN replaced with empty string."""
    df = pd.DataFrame(papers, columns=columns).fillna("")
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    clean = [
        {k: ("" if pd.isna(p.get(k, "")) else p.get(k, "")) for k in columns}
        for p in papers
    ]
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(clean, f, ensure_ascii=False, indent=2)

    logger.info(f"  -> {csv_path} ({len(papers)} rows)")
    logger.info(f"  -> {json_path}")


def remove_legacy_outputs(output_dir: str):
    """Delete legacy VLM/Agent output files from previous versions."""
    removed = []
    for filename in LEGACY_OUTPUT_FILES:
        path = os.path.join(output_dir, filename)
        if os.path.exists(path):
            os.remove(path)
            removed.append(filename)
    if removed:
        logger.info("Removed legacy outputs: " + ", ".join(removed))


def run(input_path: str, output_dir: str):
    logger.info(f"Loading {input_path}...")
    with open(input_path, "r", encoding="utf-8") as f:
        papers = json.load(f)
    logger.info(f"Loaded {len(papers)} papers")

    remove_legacy_outputs(output_dir)

    before = len(papers)
    seen = {}
    for p in papers:
        link = p.get("Paper_link", "")
        seen[link if link else id(p)] = p
    papers = list(seen.values())
    if len(papers) < before:
        logger.info(f"  Deduplicated: {before} -> {len(papers)} ({before - len(papers)} duplicates removed)")

    for p in papers:
        p.setdefault("PrimaryCategory", "")
        p.setdefault("Categories", "")

    need_code = [p for p in papers if not p.get("code") or str(p["code"]) in ("", "nan")]
    if need_code:
        logger.info(f"[1/9] Cleaning abstracts & extracting code URLs ({len(need_code)}/{len(papers)})...")
        code_filled = 0
        for p in need_code:
            clean_abstract(p)
            if p.get("code") and str(p["code"]) not in ("", "nan"):
                code_filled += 1
        logger.info(f"  Code field filled from abstract: {code_filled}")
    else:
        logger.info("[1/9] Code extraction: all papers already have code field, skipped")

    need_classify = [p for p in papers if not p.get("Category")]
    if need_classify:
        logger.info(f"[2/9] Classifying papers ({len(need_classify)}/{len(papers)})...")
        classify_papers(need_classify)
    else:
        logger.info("[2/9] Classification: all papers already classified, skipped")

    need_tasks = [p for p in papers if "_tasks" not in p]
    if need_tasks:
        logger.info(f"[3/9] Tagging tasks ({len(need_tasks)}/{len(papers)})...")
        tag_all_papers(need_tasks)
    else:
        logger.info("[3/9] Task tagging: all papers already tagged, skipped")

    all_cat_counter = Counter(p.get("Category", "Other") for p in papers)
    for cat, count in all_cat_counter.most_common():
        logger.info(f"  {cat}: {count}")

    logger.info("[4/9] Saving cleaned dataset...")
    save(
        papers,
        os.path.join(output_dir, "papers.csv"),
        os.path.join(output_dir, "papers.json"),
        ALL_COLUMNS,
    )

    logger.info("[5/9] Filtering MM-related papers...")
    mm_matched, mm_annotated = filter_mm_papers(papers)
    logger.info(f"  MM-related: {len(mm_matched)} / {len(papers)}")

    logger.info("[6/9] Classifying MM papers...")
    classify_papers(mm_matched)

    mm_cat_counter = Counter(p.get("Category", "Other") for p in mm_matched)
    for cat, count in mm_cat_counter.most_common():
        logger.info(f"  {cat}: {count}")

    logger.info("Saving MM outputs...")
    save(
        mm_matched,
        os.path.join(output_dir, "papers_mm.csv"),
        os.path.join(output_dir, "papers_mm.json"),
        SUBSET_COLUMNS,
    )
    mm_annotated_path = os.path.join(output_dir, "papers_mm_annotated.json")
    with open(mm_annotated_path, "w", encoding="utf-8") as f:
        json.dump(mm_annotated, f, ensure_ascii=False, indent=2)
    logger.info(f"  -> {mm_annotated_path}")

    logger.info("[7/9] Filtering MA-related papers...")
    ma_matched, ma_annotated = filter_ma_papers(papers)
    logger.info(f"  MA-related: {len(ma_matched)} / {len(papers)}")

    logger.info("[8/9] Classifying MA papers...")
    classify_papers(ma_matched)

    ma_cat_counter = Counter(p.get("Category", "Other") for p in ma_matched)
    for cat, count in ma_cat_counter.most_common():
        logger.info(f"  {cat}: {count}")

    logger.info("Saving MA outputs...")
    save(
        ma_matched,
        os.path.join(output_dir, "papers_ma.csv"),
        os.path.join(output_dir, "papers_ma.json"),
        SUBSET_COLUMNS,
    )
    ma_annotated_path = os.path.join(output_dir, "papers_ma_annotated.json")
    with open(ma_annotated_path, "w", encoding="utf-8") as f:
        json.dump(ma_annotated, f, ensure_ascii=False, indent=2)
    logger.info(f"  -> {ma_annotated_path}")

    logger.info("[9/9] Generating Atom feeds...")
    from rss_generator import generate_feeds
    generate_feeds(papers, mm_matched, ma_matched, output_dir, site_url="https://rspaper.top")

    logger.info("=" * 50)
    logger.info(f"Done! Total: {len(papers)} | MM: {len(mm_matched)} | MA: {len(ma_matched)}")
    logger.info(f"  papers.csv/json          - all {len(papers)} papers (cleaned)")
    logger.info(f"  papers_mm.csv/json       - {len(mm_matched)} MM papers (with Category)")
    logger.info(f"  papers_mm_annotated.json - full list with MM flags")
    logger.info(f"  papers_ma.csv/json       - {len(ma_matched)} MA papers (with Category)")
    logger.info(f"  papers_ma_annotated.json - full list with MA flags")


def main():
    parser = argparse.ArgumentParser(description="One-click: clean + filter + classify")
    parser.add_argument(
        "--input", type=str, default="output/papers.json",
        help="Input JSON file (default: output/papers.json)"
    )
    parser.add_argument(
        "--output-dir", type=str, default="output",
        help="Output directory (default: output)"
    )
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    run(args.input, args.output_dir)


if __name__ == "__main__":
    main()
