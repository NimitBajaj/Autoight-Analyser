import re
from typing import List, Optional

BULLET_RE = re.compile(r"^\s*(\d+[\.\)]\s*|\-+\s*|\•\s*)")

# Common junk/notes that are not real legend symbols
STOPWORDS = {
    "LEGEND", "LEGENDS", "SWITCH", "BOTTOM OF SLAB", "BOTTOM OF BEAM",
    "BOB", "BOS", "BOMH", "BOEX", "BOC"
}

def _strip_acad_formatting(text: str) -> str:
    """Remove AutoCAD-specific formatting codes like {\fMistral|b0|...}."""
    # Drop {\f...} style
    text = re.sub(r"\{\\[^}]+\}", " ", text)
    # Drop formatting codes like \P, \L, \l, etc.
    text = re.sub(r"\\[A-Za-z0-9]+", " ", text)
    return text

def _extract_legend_chunk(text: str) -> Optional[str]:
    """If there's an explicit 'LEGEND' section, extract it."""
    m = re.search(r"(LEGEND[\s\S]+)", text, flags=re.IGNORECASE)
    return m.group(1) if m else None

def parse_legend_terms(raw_text: str) -> List[str]:
    """
    Return a deduplicated, clean list of legend items
    (e.g., ["Suspended Light", "Halogen", ...]).
    """
    clean = _strip_acad_formatting(raw_text)
    chunk = _extract_legend_chunk(clean) or clean  # fallback if no explicit section

    candidates: List[str] = []
    for part in re.split(r"[\n|,]+", chunk):
        part = BULLET_RE.sub("", part)
        token = part.strip(" :;-").strip()
        if not token:
            continue

        # Heuristic filters
        if token.upper() in STOPWORDS:
            continue
        if len(token) > 60:  # too long = likely not a symbol
            continue
        if not any(c.isalpha() for c in token):  # skip if no letters
            continue

        # New cleanup rules:
        low = token.lower()

        # Filters
        if token.upper() in STOPWORDS:
            continue
        if len(token) > 35:  # too long
            continue
        if len(token.split()) > 4:  # too many words = description not legend
            continue
        if not any(c.isalpha() for c in token):
            continue
        if "lvl" in low or "bob" in low or "bos" in low:
            continue
        if low.startswith(("+", "-", "{", "}")):
            continue
        if re.search(r"\d+'\s*\-\s*\d+'", low) or '"' in token:
            continue
        if re.search(r"\+91|\d{2,}[/-]\d{2,}", low):  # phone/date
            continue
        if any(w in low for w in ["date", "drawn by", "checked by", "client", "address", "scale", "project"]):
            continue
        if any(w in low for w in ["bedroom", "toilet", "kitchen", "floor", "lobby", "residence"]):
            continue

        if len(token) <= 2:
            continue

        # Skip address / section codes
        if re.match(r"^[A-Z0-9\-]+$", token):
            continue

        # Skip words like Wardrobe, Partition, Ref, Detail, Section
        if any(w in low for w in ["wardrobe", "partition", "ref", "detail", "section"]):
            continue

        if any(w in low for w in [
            "dlf", "south extension", "ground floor", "basement",
            "k-", "ref", "detail", "section"
        ]):
            continue
        candidates.append(token)


    # Normalize capitalization and dedupe while preserving order
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

# -------------------------------------------------------------------


if __name__ == "__main__":
    import sys, json
    text = sys.stdin.read()
    items = parse_legend_terms(text)
    print("---- PARSED LEGEND ITEMS ----")
    for it in items:
        print(" •", it)
    print(json.dumps(items, indent=2, ensure_ascii=False))


