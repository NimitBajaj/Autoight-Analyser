from __future__ import annotations
import re
from typing import List

# --- regexes to strip AutoCAD formatting ---
FORMAT_BRACE_RE = re.compile(r"\{[^{}]*\}")               # strip {...} formatting chunks
ESCAPE_TAG_RE   = re.compile(r"\\[A-Za-z0-9\.]+;?")       # \P \H0.7x; \C131; \A1; etc.
MULTI_SPACE_RE  = re.compile(r"\s+")
BULLET_RE       = re.compile(r"^\s*(\d{1,2}\.)\s*")       # 01. / 1. numbering

# --- filters ---
SKIP_PATTERNS = re.compile(
    r"\d{3,}|"                # phone numbers, long digit sequences
    r"NOTE|DRAWN BY|CHECKED BY|DATE|SCALE|" 
    r"GROUND FLOOR|FIRST FLOOR|TYPICAL FLOOR|BASEMENT|DLF|SOUTH EX",
    re.I,
)
FIXTURE_KEYWORDS = {
    "LIGHT", "FAN", "PELMET", "COVE", "PIPE", "SOCKET", "SWITCH", "DUCT", "CHIMNEY"
}

LEGEND_ANCHORS  = (
    "LEGENDS:-", "LEGENDS:", "LEGEND:-", "LEGEND:",  # common variants
)

# -------------------------------------------------------------------

def _strip_acad_formatting(text: str) -> str:
    """Remove AutoCAD MText formatting noise."""
    text = FORMAT_BRACE_RE.sub(" ", text)
    text = ESCAPE_TAG_RE.sub(" ", text)
    text = text.replace("\\P", "\n")
    text = MULTI_SPACE_RE.sub(" ", text)
    text = text.replace("–", "-").replace("—", "-")
    return text.strip()

def _extract_legend_chunk(clean: str) -> str | None:
    """Pull the shortest chunk that looks like the legend block after an anchor."""
    idx = min((clean.upper().find(a) for a in LEGEND_ANCHORS if a in clean.upper()), default=-1)
    if idx == -1:
        return None
    tail = clean[idx:]
    stops = ["NOTE :", "DRAWN BY", "CHECKED BY", "TYPICAL FLOOR", "FIRST FLOOR", "STILT FLOOR", "KEY PLAN"]
    stop_positions = [tail.upper().find(s) for s in stops if s in tail.upper()]
    stop_positions = [p for p in stop_positions if p >= 0]
    end = min(stop_positions) if stop_positions else len(tail)
    return tail[:end]

REJECT_KEYWORDS = [
    "date", "drawn", "checked", "scale", "client", "project", "address", "plan",
    "north", "south", "east", "west", "key", "legend", "revision", "dwg", "floor",
    "false ceiling", "typical", "provision", "framing", "kitchen", "pdr", "toilet",
    "bedroom", "lobby", "living", "scale", "ceiling electrical"
]

# Accept only if these hints are present
KEEP_HINTS = [
    "light", "pelmet", "pipe", "duct", "grill", "mirror",
    "profile", "machine", "fan", "switch", "chandelier"
]


def parse_legend_terms(raw_text: str) -> List[str]:
    lines = raw_text.splitlines()
    candidates: List[str] = []

    for line in lines:
        token = re.sub(r"{.*?}", " ", line)  # strip CAD formatting
        token = re.sub(r"\\[A-Za-z0-9]+", " ", token)  # strip escape codes
        token = token.strip()

        if not token or token.startswith(";"):  # skip empty or CAD comment
            continue

        # skip too long lines (likely descriptive notes)
        if len(token.split()) > 6:
            continue

        # reject boilerplate words
        if any(kw in token.lower() for kw in REJECT_KEYWORDS):
            continue

        # only keep if it has one of our hints
        if not any(h in token.lower() for h in KEEP_HINTS):
            continue

        # normalize
        token = " ".join(w.capitalize() for w in token.split())

        candidates.append(token)

    # dedupe while preserving order
    seen = set()
    result = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            result.append(c)

    return result
# -------------------------------------------------------------------

if __name__ == "__main__":
    import sys, json
    text = sys.stdin.read()
    items = parse_legend_terms(text)
    print("---- PARSED LEGEND ITEMS ----")
    for it in items:
        print(" •", it)
    print(json.dumps(items, indent=2, ensure_ascii=False))


