<div align="center">

<img src="asset/logo.png" alt="RS-Paper-Hub" width="100">

# RS-Paper-Hub

**arXiv 多模态论文自动采集、清洗、MM 筛选与 MA 筛选工具**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![arXiv](https://img.shields.io/badge/source-arXiv-b31b1b.svg)](https://arxiv.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Website](https://img.shields.io/badge/website-rspaper.top-4f46e5.svg)](https://rspaper.top)
[![Team](https://img.shields.io/badge/team-ML4Sustain-green.svg?logo=github)](https://github.com/ML4Sustain)

[English](README.md) | [中文](README_zh.md)

</div>

---

## 概述

RS-Paper-Hub 自动从 arXiv 爬取多模态论文，提取结构化元数据，并提供一键式数据处理流水线，涵盖数据清洗、任务标签标注、MM 过滤、MA 过滤以及分类等功能。该库通过 GitHub Actions 每日更新（周一至周五，与 arXiv 公告时间表同步）。

### 核心功能

- **自动采集** — 通过 arXiv API 抓取论文，内置限流与重试
- **每日自动更新** — GitHub Actions 周一至周五 UTC 00:30（北京时间 08:30）自动抓取，与 arXiv 发布时间同步
- **默认增量** — 自动跳过已有论文，`--update` 抓取最近 7 天新论文
- **断点续传** — 进度保存在 `progress.json`，中断后自动恢复
- **一键处理** — `pipeline.py` 一条命令完成去重、清洗、分类、任务标注、MM 筛选、MA 筛选
- **自动去重** — Pipeline 按 `Paper_link` 自动去除重复论文
- **数据清洗** — 从摘要提取代码仓库链接，自动填充 `code` 字段
- **任务标注** — 自动标注 14 种多模态任务类型：MMCLS、ITR、VQA、IC、VG、OVOD、OVSEG、T2I、T2V、I2T、MRE、MDI、MAG、TAP
- **全量分类** — 所有论文自动标记为 `Method`、`Dataset`、`Survey`
- **MM 筛选** — 基于上下文感知的关键词规则筛选视觉语言模型相关论文（避免非 MM 跨模态/检索等误判）
- **MA 筛选** — 按 `cs.MA` 分类筛选多智能体系统论文，并保留关键词命中字段用于可解释性
- **三标签网页** — 浏览全部论文、MM 子集、MA 子集；支持搜索、多维图表筛选、中英双语切换
- **论文收藏** — 跨搜索收藏论文，统一查看或导出
- **BibTeX 批量导出** — 导出带时间戳的 `.bib` 文件，可选包含摘要
- **RSS/Atom 订阅** — 自动生成 Atom feed（全部 / MM / MA），支持 Zotero 订阅，每日更新最近 7 天论文
- **PDF 下载** — 批量下载，自动去重，按年份归档

---

## 快速开始

```bash
pip install -r requirements.txt

# 采集全部论文
python main.py

# 一键处理：清洗 + 分类 + 任务标注 + MM 筛选 + MA 筛选
python pipeline.py
```

---

## 日常更新

```bash
# 1. 抓取最新论文（最近 7 天，默认增量）
python main.py --update

# 2. 一键处理（去重 → 清洗 → 分类 → 任务标注 → MM 筛选 → MA 筛选 → 导出）
python pipeline.py
```

两条命令搞定。所有输出文件（`papers.csv/json`、`papers_mm.csv/json`、`papers_ma.csv/json`）自动更新。

> **注意：** `--incremental` 默认开启，已有论文会自动跳过。如需全量重新采集，请使用 `--no-incremental`。

---

## 使用说明

### 论文采集

```bash
# 全量采集（2020 至今）
python main.py

# 自定义年份范围
python main.py --start-year 2023 --end-year 2025

# 限制数量（测试用）
python main.py --max-results 100

# 增量模式（跳过已有论文）
python main.py --incremental

# 快速更新（最近 7 天）
python main.py --update

# 查看进度
python main.py --status
```

### 一键处理（推荐）

```bash
# 一键：清洗 + 分类 + 任务标注 + MM 筛选 + MA 筛选
python pipeline.py

# 自定义输入
python pipeline.py --input output/papers.json
```

`pipeline.py` 自动执行以下 9 个步骤（增量处理，已处理的论文自动跳过）：

1. **加载与去重** — 按 `Paper_link` 去除重复论文
2. **清洗** — 从摘要提取代码链接，填充 `code` 字段
3. **全量分类** — 为所有论文标记 Method / Dataset / Survey
4. **任务标注** — 标注 14 种任务类型（MMCLS, ITR, VQA, IC, VG, OVOD, OVSEG, T2I, T2V, I2T, MRE, MDI, MAG, TAP）
5. **保存** — 写入清洗后的 `papers.csv` + `papers.json`
6. **MM 筛选** — 按关键词匹配视觉语言模型相关论文，导出 `papers_mm.csv/json`
7. **MM 分类** — 细化 MM 子集分类
8. **MA 筛选与分类** — 按 `cs.MA` 分类筛选 MA 论文，导出 `papers_ma.csv/json`
9. **生成 Atom Feed** — 生成 `feed.xml`、`feed_mm.xml`、`feed_ma.xml`，包含最近 7 天论文

### 单独筛选工具

也可以单独运行各筛选脚本：

```bash
# 仅 MM 筛选
python filter_mm.py --input output/papers.json

# 仅 MA 筛选
python filter_ma.py --input output/papers.json

# 预览匹配结果（不保存）
python filter_mm.py --dry-run
python filter_ma.py --dry-run
```

### PDF 下载

```bash
# 采集并下载 PDF
python main.py --download

# 仅下载 PDF（基于已有数据，不重新采集）
python main.py --download-only
```

---

## 命令参数

### `main.py`

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--start-year` | 起始年份 | 2020 |
| `--end-year` | 结束年份 | 2026 |
| `--max-results` | 最大论文数量 | 无限制 |
| `--output-dir` | 输出目录 | `output` |
| `--update` | 快速更新（仅最近 7 天） | 关 |
| `--incremental` | 跳过已有论文 | **开** |
| `--no-incremental` | 禁用增量，全量重抓 | 关 |
| `--download` | 下载 PDF | 关 |
| `--download-only` | 仅下载 PDF（跳过采集） | 关 |
| `--with-code` | 查询 Papers With Code 代码链接 | 关 |
| `--status` | 显示进度并退出 | — |
| `-v, --verbose` | 详细日志 | 关 |

### `pipeline.py`

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--input` | 输入 JSON 文件 | `output/papers.json` |
| `--output-dir` | 输出目录 | `output` |

### `filter_mm.py` / `filter_ma.py`

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--input` | 输入 JSON 文件 | `output/papers.json` |
| `--output-dir` | 输出目录 | `output` |
| `--dry-run` | 预览匹配结果，不保存文件 | 关 |

---

## 输出字段

所有输出同时提供 **CSV** 和 **JSON** 两种格式。

| 字段 | 说明 | 示例 |
|------|------|------|
| `Category` | 论文类别 | Method, Dataset, Survey |
| `Type` | arXiv 主分类 | Computer Vision |
| `Subtype` | 其他分类 | Image and Video Processing |
| `Date` | 精确发布日期 | 2024-03-15 |
| `Month` | 发布月份 | 3 |
| `Year` | 发布年份 | 2024 |
| `Institute` | 第一作者机构 | （arXiv 数据有限，可能为空） |
| `Title` | 论文标题 | Hybrid Attention Network for... |
| `abbr.` | 标题中的缩写 | HMANet |
| `Paper_link` | arXiv 链接 | http://arxiv.org/abs/2301.12345 |
| `Abstract` | 摘要 | ... |
| `code` | 代码仓库链接 | https://github.com/... |
| `Publication` | 发表期刊/会议 | CVPR 2024 |
| `BibTex` | BibTeX 引用 | @article{...} |
| `Authors` | 作者列表 | Alice, Bob, Charlie |
| `_tasks` | 任务标签（分号分隔） | MMCLS;ITR;VQA |

---

## 任务标签

论文根据标题和摘要关键词自动标注任务类型：

| 标签 | 任务 | 示例 |
|------|------|------|
| **MMCLS** | 多模态分类 | 多模态分类、跨模态分类 |
| **VQA** | 视觉问答 | VQA、RSVQA |
| **IC** | 图像描述 | 图像描述生成 |
| **VG** | 视觉定位 | 视觉定位、短语定位 |
| **ITR** | 图文检索 | 跨模态检索 |
| **OVOD** | 开放词表检测 | 开放词表检测、零样本检测 |
| **OVSEG** | 开放词表分割 | 开放词表分割、零样本分割 |
| **T2I** | 文本生成图像 | text-to-image 生成 |
| **T2V** | 文本生成视频 | text-to-video 生成 |
| **I2T** | 图像生成文本 | image-to-text 生成 |
| **MRE** | 多模态推理 | 视觉语言推理 |
| **MDI** | 多模态对话与指令 | 多模态对话、指令微调 |
| **MAG** | 多模态智能体 | 多模态 Agent、视觉语言 Agent |
| **TAP** | 工具增强感知 | 工具调用、工具增强感知 |

---

## 项目结构

```
rs-paper-hub/
├── main.py              # 采集器命令行入口
├── pipeline.py          # 一键处理：清洗 + 分类 + 任务标注 + MM 筛选 + MA 筛选 + RSS
├── filter_mm.py         # 单独 MM 筛选脚本
├── filter_ma.py         # 单独 MA 筛选脚本
├── rss_generator.py     # Atom feed 生成器（Zotero 订阅）
├── config.py            # 搜索配置
├── scraper.py           # arXiv API 采集器
├── parser.py            # 元数据解析与 BibTeX 生成
├── downloader.py        # PDF 下载器（断点续传）
├── progress.py          # 进度追踪器
├── pwc_client.py        # Papers With Code 客户端
├── cleaning/
│   ├── abstract_cleaner.py   # 摘要链接提取
│   ├── classifier.py         # 论文分类器（Method/Dataset/Survey）
│   ├── task_tagger.py        # 任务标注（14 种多模态任务类型）
│   └── filter/
│       ├── mm_filter.py      # MM 关键词规则
│       └── ma_filter.py      # MA 分类规则（cs.MA）
├── .github/workflows/
│   └── daily-update.yml      # 每日 CI/CD 流水线（周一至周五，与 arXiv 同步）
├── index.html               # 交互式网页（三标签：全部 / MM / MA）
├── requirements.txt
└── output/
    ├── papers.csv/json              # 全部论文（已清洗 + 分类 + 标注）
    ├── papers_mm.csv/json          # MM 子集（含分类标签）
    ├── papers_mm_annotated.json    # 完整列表（带 MM 标注）
    ├── papers_ma.csv/json        # MA 子集（含分类标签）
    ├── papers_ma_annotated.json  # 完整列表（带 MA 标注）
    ├── feed.xml                     # Atom feed — 全部论文（最近 7 天）
    ├── feed_mm.xml                 # Atom feed — MM 论文（最近 7 天）
    ├── feed_ma.xml               # Atom feed — MA 论文（最近 7 天）
    └── progress.json                # 采集进度
```

---

## 搜索范围

搜索策略由 [`config.py`](config.py) 结构化配置生成：

- 严格收录分类：`cs.MM`、`cs.MA`
- 条件收录分类：`cs.CV`（仅标题/摘要命中多模态术语时纳入）

`SEARCH_QUERY` 由 `build_search_query()` 自动拼装，核心配置项为：

- `STRICT_CATEGORIES`
- `GATED_CATEGORY`
- `CV_MM_TERMS`

---

## 速率限制

| 操作 | 速率 | 说明 |
|------|------|------|
| 元数据查询 | ~3 秒/请求 | 每次返回最多 100 条 |
| PDF 下载 | ~3 秒/文件 | 遵守 arXiv 限制 |

**建议工作流**：先采集元数据（`python main.py`），确认无误后再单独下载 PDF（`python main.py --download-only`）。

---

## 网页可视化

```bash
python3 -m http.server 8080
```

打开 http://localhost:8080 即可查看，功能包括：

- **三数据标签** — 切换浏览全部论文、MM 子集、MA 子集
- **相关度搜索** — 标题匹配优先于摘要匹配
- **多维图表筛选** — 点击年份/类型/分类/任务柱状图即可筛选，支持多选
- **任务分布图** — 展示 Top 5 任务，其余可折叠查看
- **年份范围选择** — 单年或自定义范围
- **论文自动分类** — 所有论文自动标记（Method、Dataset、Survey）
- **论文收藏** — 跨搜索收藏论文，统一查看或导出
- **BibTeX 批量导出** — 导出带时间戳的 `.bib` 文件，可选包含摘要
- **今日新增标记** — 统计栏显示 `+N` 新增数量
- **Google Scholar 链接** — 一键搜索 Google Scholar
- **中英双语** — 支持中英文界面切换
- **移动端适配** — 可折叠筛选面板，响应式布局
- **LaTeX 渲染** — KaTeX 数学公式渲染

---

## RSS 订阅与 Zotero 集成

Pipeline 自动生成 [Atom](https://zh.wikipedia.org/wiki/Atom_(%E6%A0%87%E5%87%86)) feed，包含最近 7 天的论文，可直接用 Zotero 或其他 RSS 阅读器订阅。

| Feed | URL | 内容 |
|------|-----|------|
| 全部论文 | `https://rspaper.top/output/feed.xml` | 最近 7 天全部论文 |
| MM 论文 | `https://rspaper.top/output/feed_mm.xml` | MM 子集 |
| MA 论文 | `https://rspaper.top/output/feed_ma.xml` | MA 子集 |

### 在 Zotero 中订阅

1. 打开 Zotero → **文件** → **新建 Feed** → **从 URL**
2. 粘贴上方任一 feed URL
3. Zotero 将自动拉取新论文，包含标题、作者、摘要、arXiv 链接和代码链接

Feed 随每日 GitHub Actions 自动更新。

---

## 注意事项

- `Institute` 字段依赖 arXiv 的 affiliation 信息，大部分论文未提供
- 已下载的 PDF 和已采集的月份会被记录，重复运行不会重复处理
- `progress.json` 采用原子写入，中断不会损坏进度文件

---

## 引用

如果 RS-Paper-Hub 对您的研究或工作有所帮助，请考虑引用本仓库：

```bibtex
@software{rs_paper_hub,
  author       = {ML4Sustain},
  title        = {RS-Paper-Hub: A Curated Collection of Multimodal Papers from arXiv},
  year         = {2026},
  url          = {https://github.com/ML4Sustain/rs-paper-hub},
  note         = {Automated scraping, cleaning, classification, task tagging, MM filtering, and MA filtering pipeline for multimodal papers}
}
```

---

## License

MIT

