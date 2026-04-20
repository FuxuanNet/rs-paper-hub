<div align="center">

<img src="asset/logo.png" alt="RS-Paper-Hub" width="100">

# RS-Paper-Hub

**A curated collection of multimodal papers from arXiv, with automated scraping, cleaning, task tagging, MM filtering, and MA filtering.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![arXiv](https://img.shields.io/badge/source-arXiv-b31b1b.svg)](https://arxiv.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Website](https://img.shields.io/badge/website-rspaper.top-4f46e5.svg)](https://rspaper.top)
[![Team](https://img.shields.io/badge/team-ML4Sustain-green.svg?logo=github)](https://github.com/ML4Sustain)

[English](README.md) | [中文](README_zh.md) | [Live Demo](https://rspaper.top)

</div>

---

## Overview

RS-Paper-Hub automatically scrapes multimodal papers from arXiv, extracts structured metadata, and provides a one-click pipeline for data cleaning, task tagging, MM filtering, MA filtering, and classification. Updated daily via GitHub Actions (Mon–Fri, synced with arXiv announcement schedule).

### Key Features

- **Tiered arXiv Retrieval** — Fully includes `cs.MM` and `cs.MA`; includes `cs.CV` only when multimodal terms are matched
- **Daily Automated Updates** — GitHub Actions fetches the latest papers (last 7 days) Mon–Fri at 00:30 UTC (08:30 Beijing Time), aligned with arXiv's announcement schedule
- **Incremental Pipeline** — Only new papers go through cleaning, classification, and tagging; existing data is preserved
- **Task Tagging** — Auto-tags papers with 14 multimodal task types: MMCLS, ITR, VQA, IC, VG, OVOD, OVSEG, T2I, T2V, I2T, MRE, MDI, MAG, TAP
- **Paper Classification** — Labels papers as `Method`, `Dataset`, or `Survey` based on title keywords
- **MM Filtering** — Keyword-based filtering for Vision-Language Model related papers with context-aware rules (avoids false positives from non-MM cross-modal or retrieval terms)
- **MA Filtering** — Category-based filtering for Multiagent Systems papers (`cs.MA`), with keyword hits retained for explainability
- **Three-Tab Web Viewer** — Browse All Papers, MM subset, or MA subset; with search, multi-dimensional chart filtering, task/category/year filters, Google Scholar links, and mobile-friendly UI
- **Paper Collection** — Collect papers across multiple searches into a personal collection, then view or export them together
- **BibTeX Batch Export** — Export filtered results, current page, custom range, or collection as timestamped `.bib` file with optional abstracts
- **Code Discovery** — Automatically extracts code repository URLs from abstracts
- **RSS/Atom Feeds** — Auto-generated Atom feeds (All / MM / MA) for Zotero subscription, updated daily with the last 7 days of papers
- **PDF Download** — Batch download with deduplication, organized by year

---

## Quick Start

```bash
pip install -r requirements.txt

# Scrape all papers
python main.py

# One-click: clean + classify + tag tasks + filter MM + filter MA
python pipeline.py
```

---

## Daily Workflow

```bash
# 1. Grab latest papers (last 7 days, incremental by default)
python main.py --update

# 2. Run full pipeline (deduplicate → clean → classify → tag → filter MM & MA → export)
python pipeline.py
```

That's it. All output files (`papers.csv/json`, `papers_mm.csv/json`, `papers_ma.csv/json`) are updated in place.

> **Note:** `--incremental` is enabled by default — existing papers are always skipped. Use `--no-incremental` to force a full re-fetch.

---

## Usage

### Scraping

```bash
# Full scrape
python main.py

# Custom year range
python main.py --start-year 2023 --end-year 2025

# Limit results (for testing)
python main.py --max-results 100

# Quick update (latest 7 days)
python main.py --update

# Check progress
python main.py --status
```

### Pipeline (Recommended)

```bash
# One-click: clean + classify + tag tasks + filter MM + filter MA
python pipeline.py

# Custom input
python pipeline.py --input output/papers.json
```

`pipeline.py` runs the following 9 steps (incrementally — each step skips already-processed papers):

1. **Load & Deduplicate** — Remove duplicate papers by `Paper_link`
2. **Clean** — Extract code URLs from abstracts, fill `code` field
3. **Classify** — Label every paper as Method / Dataset / Survey (title-based)
4. **Tag Tasks** — Assign task labels (MMCLS, ITR, VQA, IC, VG, OVOD, OVSEG, T2I, T2V, I2T, MRE, MDI, MAG, TAP)
5. **Save** — Write cleaned `papers.csv` + `papers.json`
6. **Filter MM** — Include `cs.MM`, and include `cs.CV` papers only when MM keywords are matched
7. **Classify MM** — Refine categories for MM subset, export `papers_mm.csv/json`
8. **Filter & Classify MA** — Select papers by `cs.MA` category and classify the subset, export `papers_ma.csv/json`
9. **Generate Atom Feeds** — Produce `feed.xml`, `feed_mm.xml`, `feed_ma.xml` with the last 7 days of papers

### Standalone Filter Scripts

```bash
# MM filter only
python filter_mm.py --input output/papers.json

# MA filter only
python filter_ma.py --input output/papers.json

# Preview without saving (dry-run)
python filter_mm.py --dry-run
python filter_ma.py --dry-run
```

### PDF Download

```bash
# Scrape + download
python main.py --download

# Download only (from existing data)
python main.py --download-only
```

---

## CLI Reference

### `main.py`

| Flag | Description | Default |
|------|-------------|---------|
| `--start-year` | Start year | 2020 |
| `--end-year` | End year | 2026 |
| `--max-results` | Max papers to fetch | unlimited |
| `--output-dir` | Output directory | `output` |
| `--update` | Quick update (latest 7 days) | off |
| `--no-incremental` | Disable incremental, re-fetch all | off |
| `--incremental` | Skip existing papers | **on** |
| `--download` | Download PDFs | off |
| `--download-only` | Download PDFs only (skip scraping) | off |
| `--with-code` | Query Papers With Code for repos | off |
| `--status` | Show progress and exit | — |
| `-v, --verbose` | Verbose logging | off |

### `pipeline.py`

| Flag | Description | Default |
|------|-------------|---------|
| `--input` | Input JSON file | `output/papers.json` |
| `--output-dir` | Output directory | `output` |

### `filter_mm.py` / `filter_ma.py`

| Flag | Description | Default |
|------|-------------|---------|
| `--input` | Input JSON file | `output/papers.json` |
| `--output-dir` | Output directory | `output` |
| `--dry-run` | Preview matches without saving | off |

---

## Output Schema

All outputs are available in both **CSV** and **JSON** format.

| Field | Description | Example |
|-------|-------------|---------|
| `Category` | Paper category | Method, Dataset, Survey |
| `Type` | arXiv primary category | Computer Vision |
| `Subtype` | Secondary categories | Image and Video Processing |
| `Date` | Exact publication date | 2024-03-15 |
| `Month` | Publication month | 3 |
| `Year` | Publication year | 2024 |
| `Title` | Paper title | Hybrid Attention Network for... |
| `abbr.` | Abbreviation from title | HMANet |
| `Paper_link` | arXiv URL | http://arxiv.org/abs/2301.12345 |
| `Abstract` | Full abstract | ... |
| `code` | Code repository URL | https://github.com/... |
| `Publication` | Venue (journal/conference) | CVPR 2024 |
| `BibTex` | BibTeX citation | @article{...} |
| `Authors` | Author list | Alice, Bob, Charlie |
| `_tasks` | Task tags (semicolon-separated) | MMCLS;ITR;VQA |

---

## Task Tags

Papers are automatically tagged with multimodal task types based on title and abstract keyword matching:

| Tag | Task | Examples |
|-----|------|----------|
| **MMCLS** | Multimodal Classification | multimodal classification, cross-modal classification |
| **VQA** | Visual Question Answering | VQA, RSVQA |
| **IC** | Image Captioning | image captioning, caption generation |
| **VG** | Visual Grounding | visual grounding, phrase grounding |
| **ITR** | Image-Text Retrieval | cross-modal retrieval |
| **OVOD** | Open-Vocabulary Object Detection | open-vocabulary object detection, zero-shot OD |
| **OVSEG** | Open-Vocabulary Segmentation | open-vocabulary segmentation, zero-shot segmentation |
| **T2I** | Text-to-Image Generation | text-to-image generation |
| **T2V** | Text-to-Video Generation | text-to-video generation |
| **I2T** | Image-to-Text Generation | image-to-text generation |
| **MRE** | Multimodal Reasoning | vision-language reasoning |
| **MDI** | Multimodal Dialogue & Instruction | multimodal dialog, instruction tuning |
| **MAG** | Multimodal Agent | multimodal agent, vision-language agent |
| **TAP** | Tool-Augmented Perception | tool use, tool-augmented perception |

---

## Project Structure

```
rs-paper-hub/
├── main.py              # Scraper CLI entry point
├── pipeline.py          # One-click: clean + classify + tag + filter MM & MA + RSS
├── filter_mm.py         # Standalone MM filter script
├── filter_ma.py         # Standalone MA filter script
├── rss_generator.py     # Atom feed generator for Zotero
├── config.py            # Search configuration
├── scraper.py           # arXiv API scraper
├── parser.py            # Metadata parser & BibTeX generation
├── downloader.py        # PDF downloader with resume support
├── progress.py          # Progress tracker
├── pwc_client.py        # Papers With Code client
├── cleaning/
│   ├── abstract_cleaner.py   # Abstract URL extraction
│   ├── classifier.py         # Paper classifier (Method/Dataset/Survey)
│   ├── task_tagger.py        # Task tagging (14 multimodal task types)
│   └── filter/
│       ├── mm_filter.py      # MM keyword rules
│       └── ma_filter.py      # MA category rule (cs.MA)
├── .github/workflows/
│   └── daily-update.yml      # Daily CI/CD pipeline (Mon-Fri, synced with arXiv)
├── index.html               # Interactive web viewer (3 tabs: All / MM / MA)
├── requirements.txt
└── output/
    ├── papers.csv/json              # All papers (cleaned + classified + tagged)
    ├── papers_mm.csv/json          # MM subset with categories
    ├── papers_mm_annotated.json    # Full list with MM flags
    ├── papers_ma.csv/json        # MA subset with categories
    ├── papers_ma_annotated.json  # Full list with MA flags
    ├── feed.xml                     # Atom feed — all papers (last 7 days)
    ├── feed_mm.xml                 # Atom feed — MM papers (last 7 days)
    ├── feed_ma.xml               # Atom feed — MA papers (last 7 days)
    └── progress.json                # Scraping progress
```

---

## Search Scope

Search uses a tiered strategy defined in [`config.py`](config.py):

- Strict categories: `cs.MM`, `cs.MA`
- Gated category: `cs.CV` (must match multimodal terms in title/abstract)

`SEARCH_QUERY` is composed automatically by `build_search_query()` from:

- `STRICT_CATEGORIES`
- `GATED_CATEGORY`
- `CV_MM_TERMS`

---

## Web Viewer

Visit [rspaper.top](https://rspaper.top) or run locally:

```bash
python3 -m http.server 8080
```

Features include:

- **Three data tabs** — Switch between All Papers, MM subset, and MA subset
- **Quick date filters** — "Today" and "This Week" buttons with red badge counts
- **Relevance-ranked search** — Title matches prioritized over abstract matches
- **Multi-dimensional chart filtering** — Click year/type/category/task bars to filter, multi-select supported
- **Task distribution chart** — Top 5 tasks shown with collapsible remaining tasks
- **Year range selection** — Single year or custom range via dropdown
- **Paper classification** — All papers labeled as Method, Dataset, or Survey
- **Paper collection** — Collect papers across multiple searches, then view or export them together
- **BibTeX batch export** — Export filtered results, current page, custom range, or collection as timestamped `.bib` file with optional abstracts
- **New papers panel** — Side panel showing today's and this week's papers
- **Google Scholar links** — One-click search on Google Scholar for each paper
- **Bilingual UI** — Switch between English and Chinese
- **Mobile-friendly** — Responsive layout with collapsible filters and wrapping navigation
- **LaTeX rendering** — Math formulas rendered via KaTeX

> **Note:** Category and task labels are rule-based and may contain inaccuracies. We are continuously improving them. This does not affect tracking the latest research trends.

---

## RSS Feeds & Zotero Integration

The pipeline automatically generates [Atom](https://en.wikipedia.org/wiki/Atom_(web_standard)) feeds containing the last 7 days of papers. These feeds are designed for Zotero but work with any feed reader.

| Feed | URL | Content |
|------|-----|---------|
| All Papers | `https://rspaper.top/output/feed.xml` | All recent papers |
| MM Papers | `https://rspaper.top/output/feed_mm.xml` | MM subset |
| MA Papers | `https://rspaper.top/output/feed_ma.xml` | MA subset |

### Subscribe in Zotero

1. Open Zotero → **File** → **New Feed** → **From URL**
2. Paste one of the feed URLs above
3. Zotero will automatically pull new papers with title, authors, abstract, arXiv link, and code URL

Feeds are updated daily alongside the main pipeline via GitHub Actions.

---

## Rate Limits

| Operation | Rate | Note |
|-----------|------|------|
| Metadata query | ~3s / request | Returns up to 100 results per request |
| PDF download | ~3s / file | Respect arXiv rate limits |

**Recommended workflow**: scrape metadata first (`python main.py`), then download PDFs separately (`python main.py --download-only`).

---

## Citation

If you find RS-Paper-Hub useful in your research or work, please consider citing this repository:

```bibtex
@software{rs_paper_hub,
  author       = {ML4Sustain},
  title        = {RS-Paper-Hub: A Curated Collection of Multimodal Papers from arXiv},
  year         = {2026},
  url          = {https://rspaper.top},
  note         = {Automated scraping, cleaning, classification, task tagging, MM filtering, and MA filtering pipeline for multimodal papers}
}
```

---

## License

MIT

