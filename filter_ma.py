#!/usr/bin/env python3
"""Filter MA-related papers from cleaned data."""

import os
import json
import argparse
import logging
from collections import Counter

import pandas as pd

from cleaning.filter.ma_filter import filter_ma_papers
from cleaning.classifier import classify_papers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Filter MA-related papers")
    parser.add_argument("--input", type=str, default="output/papers.json")
    parser.add_argument("--output-dir", type=str, default="output")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    logger.info(f"Loading {args.input}...")
    with open(args.input, "r", encoding="utf-8") as f:
        papers = json.load(f)
    logger.info(f"Loaded {len(papers)} papers")

    matched, annotated = filter_ma_papers(papers)
    logger.info(f"MA-related papers: {len(matched)} / {len(papers)}")

    keyword_counter = Counter()
    for p in matched:
        for kw in p.get("_ma_keywords", "").split("; "):
            if kw:
                keyword_counter[kw] += 1
    logger.info("Top matched keywords:")
    for kw, count in keyword_counter.most_common(15):
        logger.info(f"  {kw}: {count}")

    if args.dry_run:
        classify_papers(matched)
        return

    classify_papers(matched)
    os.makedirs(args.output_dir, exist_ok=True)

    columns = [
        "PrimaryCategory", "Categories",
        "Category", "Type", "Subtype", "Date", "Month", "Year", "Institute",
        "Title", "abbr.", "Paper_link", "Abstract",
        "code", "Publication", "BibTex", "Authors", "_tasks",
    ]
    ma_papers = [{k: v for k, v in p.items() if k in columns} for p in matched]

    csv_path = os.path.join(args.output_dir, "papers_ma.csv")
    pd.DataFrame(ma_papers, columns=columns).fillna("").to_csv(csv_path, index=False, encoding="utf-8-sig")
    json_path = os.path.join(args.output_dir, "papers_ma.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(ma_papers, f, ensure_ascii=False, indent=2)
    annotated_path = os.path.join(args.output_dir, "papers_ma_annotated.json")
    with open(annotated_path, "w", encoding="utf-8") as f:
        json.dump(annotated, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
