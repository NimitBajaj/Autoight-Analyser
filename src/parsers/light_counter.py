"""
DEPRECATED MODULE

This module has been replaced by the new text-based legend extractor
(see `extract_legend.py`), which now handles light detection and counting
more robustly.

Keeping this file only for reference — will be removed in a later version.
"""


import json
import re
from typing import Dict, List

LIGHT_KEYWORDS = ["light", "lamp", "track", "pendant", "spot", "cove", "down"]

def is_light_item(item: str) -> bool:
    low = item.lower()
    return any(k in low for k in LIGHT_KEYWORDS)

def count_lights(raw_text: str, legend_items: List[str]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in legend_items:
        if not is_light_item(item):
            continue
        pattern = re.compile(re.escape(item), flags=re.IGNORECASE)
        matches = pattern.findall(raw_text)
        if matches:
            counts[item] = len(matches)
    return counts