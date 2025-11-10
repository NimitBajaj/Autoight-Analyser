import re
import json
from typing import List, Optional
from collections import Counter
from rapidfuzz import process, fuzz

BULLET_RE = re.compile(r"^\s*(\d+[\.\)]\s*|\-+\s*|\•\s*)")

STOPWORDS = {
    "LEGEND", "LEGENDS", "SWITCH", "BOTTOM OF SLAB", "BOTTOM OF BEAM",
    "BOB", "BOS", "BOMH", "BOEX", "BOC"
}

# Canonical light categories
CANONICAL_LIGHTS = [
    "Pendant Light",
    "Magnetic Track Light",
    "Cove Light",
    "Down Light",
    "Halogen",
    "Button Spot Light",
    "Glazer Light"
]

SYNONYMS = {
    "PENDENT LIGHT": "Pendant Light",
    "PENDANT LIGHT": "Pendant Light",
    "SUSPENDED LIGHT": "Pendant Light",
    "HANGING LIGHT": "Pendant Light",
    "MAGNETIC TRACK LIGHT": "Magnetic Track Light",
    "COVE LIGHT": "Cove Light",
    "DOWNLIGHT": "Down Light",
    "DOWN LIGHT": "Down Light",
    "HALOGEN": "Halogen",
    "SPOT LIGHT": "Button Spot Light",
    "BUTTON SPOT LIGHT": "Button Spot Light",
    "GLAZER LIGHT": "Glazer Light",
}


# -------------------- Helpers --------------------

def _strip_acad_formatting(text: str) -> str:
    text = re.sub(r"\{\\[^}]+\}", " ", text)
    text = re.sub(r"\\[A-Za-z0-9]+", " ", text)
    return text

def _extract_legend_chunk(text: str) -> Optional[str]:
    m = re.search(r"(LEGEND[\s\S]+)", text, flags=re.IGNORECASE)
    return m.group(1) if m else None

def normalize_light_name(token: str) -> Optional[str]:
    token_up = token.strip().upper()

    # direct synonym map
    if token_up in SYNONYMS:
        return SYNONYMS[token_up]

    # fuzzy match
    match, score, _ = process.extractOne(
        token, CANONICAL_LIGHTS, scorer=fuzz.token_sort_ratio
    )
    if score >= 80:
        return match
    return None


# -------------------- Core Parsers --------------------

def parse_legend_terms(raw_text: str) -> List[str]:
    clean = _strip_acad_formatting(raw_text)
    chunk = _extract_legend_chunk(clean) or clean

    candidates: List[str] = []
    for part in re.split(r"[\n|,]+", chunk):
        part = BULLET_RE.sub("", part)
        token = part.strip(" :;-").strip()
        if not token:
            continue

        low = token.lower()

        # heuristic filters
        if token.upper() in STOPWORDS:
            continue
        if len(token) > 35:
            continue
        if len(token.split()) > 4:
            continue
        if not any(c.isalpha() for c in token):
            continue
        if "lvl" in low or "bob" in low or "bos" in low:
            continue
        if low.startswith(("+", "-", "{", "}")):
            continue
        if '"' in token or re.search(r"\d{2,}[/-]\d{2,}", low):
            continue
        if any(w in low for w in [
            "date", "drawn by", "checked by", "client", "address", "scale", "project"
        ]):
            continue
        if any(w in low for w in [
            "bedroom", "toilet", "kitchen", "floor", "lobby", "residence"
        ]):
            continue
        if len(token) <= 2:
            continue
        if re.match(r"^[A-Z0-9\-]+$", token):
            continue
        if any(w in low for w in ["wardrobe", "partition", "ref", "detail", "section"]):
            continue
        if any(w in low for w in [
            "dlf", "south extension", "ground floor", "basement", "k-"
        ]):
            continue

        candidates.append(token)

    seen = set()
    out: List[str] = []
    for t in candidates:
        norm = re.sub(r"\s+", " ", t).strip()
        norm = norm[:1].upper() + norm[1:] if norm else ""
        if not norm:
            continue
        if norm.lower() not in seen:
            seen.add(norm.lower())
            out.append(norm)

    return out


def count_light_mentions(raw_text: str) -> dict:
    counts = Counter()
    for line in raw_text.splitlines():
        norm = normalize_light_name(line)
        if norm:
            counts[norm] += 1
    return dict(counts)


# -------------------- CLI --------------------

if __name__ == "__main__":
    import sys
    in_path, out_path = sys.argv[1], sys.argv[2]

    raw_text = open(in_path, "r", encoding="utf-8").read()

    legend_items = parse_legend_terms(raw_text)
    light_counts = count_light_mentions(raw_text)

    # save legends
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(legend_items, f, indent=2, ensure_ascii=False)

    # save light counts separately
    with open("data/outputs/light_counts.json", "w", encoding="utf-8") as f:
        json.dump(light_counts, f, indent=2, ensure_ascii=False)

    print("---- LEGEND ITEMS ----")
    for it in legend_items:
        print(" •", it)
    print(f"\n✅ Wrote {len(legend_items)} legend items to {out_path}")
    print(f"✅ Wrote light counts to data/outputs/light_counts.json")



