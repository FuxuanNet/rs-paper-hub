"""Configuration for arXiv multimodal paper scraper."""

# Search parameters (tiered strategy)
# 1) Strict categories are fully included.
# 2) Gated category requires multimodal keyword hit.
STRICT_CATEGORIES = ["cs.MM", "cs.MA"]
GATED_CATEGORY = "cs.CV"
ALLOWED_PRIMARY_CATEGORIES = {"cs.CV", "cs.MM", "cs.MA"}

CV_MM_TERMS = [
    "multimodal",
    "multi-modal",
    "vision-language",
    "visual-language",
    "image-text",
    "text-image",
    "cross-modal",
    "vision language model",
    "multimodal large language model",
    "MLLM",
    "LMM",
    "VLM",
    "visual question answering",
    "image captioning",
    "visual grounding",
    "text-to-image",
    "image-to-text",
    # CV-side spatial intelligence (for retrieval scope in cs.CV)
    "spatial intelligence",
    "spatial reasoning",
    "3d scene understanding",
    "3d vision-language",
    "vision-language navigation",
    "visual navigation",
    "embodied multimodal",
]


def build_search_query() -> str:
    strict = " OR ".join(f"cat:{cat}" for cat in STRICT_CATEGORIES)
    cv_terms = " OR ".join(f'ti:"{term}" OR abs:"{term}"' for term in CV_MM_TERMS)
    gated = f"(cat:{GATED_CATEGORY} AND ({cv_terms}))"
    return f"({strict}) OR {gated}"


SEARCH_QUERY = build_search_query()

# Date range
START_YEAR = 2020
END_YEAR = 2026

# arXiv API settings
BATCH_SIZE = 100          # max results per API call
REQUEST_DELAY = 3.0       # seconds between requests (arXiv rate limit)
MAX_RETRIES = 5           # retry on transient errors

# Papers With Code API
PWC_API_BASE = "https://paperswithcode.com/api/v1"
PWC_REQUEST_DELAY = 1.0   # seconds between PWC API requests

# Output
OUTPUT_DIR = "output"
CSV_FILENAME = "papers.csv"
JSON_FILENAME = "papers.json"

# arXiv category full names
CATEGORY_NAMES = {
    "cs.CV": "Computer Vision",
    "cs.MA": "Multiagent Systems",
    "cs.AI": "Artificial Intelligence",
    "cs.LG": "Machine Learning",
    "cs.MM": "Multimedia",
    "cs.RO": "Robotics",
    "cs.NE": "Neural and Evolutionary Computing",
    "cs.IR": "Information Retrieval",
    "eess.IV": "Image and Video Processing",
    "eess.SP": "Signal Processing",
    "eess.AS": "Audio and Speech Processing",
    "physics.geo-ph": "Geophysics",
    "physics.ao-ph": "Atmospheric and Oceanic Physics",
    "stat.ML": "Machine Learning (Statistics)",
}
