from __future__ import annotations
import re
from typing import List

FORMAT_BRACE_RE = re.compile(r"\{[^{}]*\}")               # strip {...} formatting chunks
ESCAPE_TAG_RE   = re.compile(r"\\[A-Za-z0-9\.]+;?")       # \P \H0.7x; \C131; \A1; etc.
MULTI_SPACE_RE  = re.compile(r"\s+")
BULLET_RE       = re.compile(r"^\s*(\d{1,2}\.)\s*")       # 01. / 1. numbering

LEGEND_ANCHORS  = (
    "LEGENDS:-", "LEGENDS:", "LEGEND:-", "LEGEND:",  # common variants
)

STOP_WORDS = (
    "NOTE", "DRAWN BY", "CHECKED BY", "TYPICAL FLOOR",
    "FIRST FLOOR", "STILT FLOOR", "KEY PLAN", "STANDARD"
)

def _strip_acad_formatting(text: str) -> str:
    """Remove AutoCAD MText formatting noise."""
    # remove braced runs like {\fFont;...} or {\A1;...}
    text = FORMAT_BRACE_RE.sub(" ", text)
    # remove escape tags like \P (paragraph), \H, \C, \W, etc.
    text = ESCAPE_TAG_RE.sub(" ", text)
    # convert explicit \P that may still linger without ; to a line break
    text = text.replace("\\P", "\n")
    # collapse whitespace
    text = MULTI_SPACE_RE.sub(" ", text)
    # normalize hyphens
    text = text.replace("–", "-").replace("—", "-")
    return text.strip()

def _extract_legend_chunk(clean: str) -> str | None:
    """Extract lines between LEGEND(S) anchor and the next stop marker."""
    lines = clean.splitlines()
    chunk_lines: list[str] = []
    capturing = False
    for line in lines:
        uline = line.strip().upper()
        if not capturing and any(a in uline for a in LEGEND_ANCHORS):
            capturing = True
            continue
        if capturing:
            if any(uline.startswith(sw) for sw in STOP_WORDS):
                break
            chunk_lines.append(line)
    return "\n".join(chunk_lines) if chunk_lines else None

def parse_legend_terms(raw_text: str) -> List[str]:
    """
    Return a deduplicated, clean list of legend items (e.g., ["Suspended Light", "Halogen", ...]).
    """
    clean = _strip_acad_formatting(raw_text)
    chunk = _extract_legend_chunk(clean) or clean  # fallback

    candidates: List[str] = []
    for part in re.split(r"[\n|,]+", chunk):
        part = BULLET_RE.sub("", part)   # drop "01." etc.
        token = part.strip(" :;-").strip()
        if not token:
            continue
        if token.upper() in {"LEGENDS", "LEGEND", "SWITCH", "BOTTOM OF SLAB", "BOTTOM OF BEAM", "BOB", "BOS", "BOMH", "BOEX", "BOC"}:
            continue
        if len(token) <= 40 and any(c.isalpha() for c in token):
            candidates.append(token)

    # Normalize capitalization and dedupe while preserving order
    seen = set()
    out: List[str] = []
    for t in candidates:
        norm = re.sub(r"\s+", " ", t).strip()
        norm = norm[:1].upper() + norm[1:]
        if norm.lower() not in seen:
            seen.add(norm.lower())
            out.append(norm)
    return out

if __name__ == "__main__":
    import sys, json
    text = sys.stdin.read()
    print("---- LEGEND CHUNK ----")
    print(_extract_legend_chunk(_strip_acad_formatting(text)))
    print("---- PARSED ITEMS ----")
    print(json.dumps(parse_legend_terms(text), indent=2, ensure_ascii=False))

