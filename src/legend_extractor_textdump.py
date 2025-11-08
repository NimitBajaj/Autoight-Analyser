"""
legend_extractor_textdump.py
----------------------------

Lightweight legend extractor for AutoCAD text dumps (.txt)
to replace/augment your existing legend extraction script.

Usage:
    python legend_extractor_textdump.py path/to/dwg_text_dump.txt

Output:
    legend.json
    {
      "legend": [...],
      "lights": {
        "Pendant Light": {"count": 24, "category": null},
        ...
      }
    }

You can later merge this with your DXF/OpenCV-based counter.
"""

import re, json, sys
from collections import OrderedDict
from rapidfuzz import process, fuzz

# --- Canonical label normalization map ---
NORMALIZATION_MAP = {
    "PENDENT LIGHT": "Pendant Light",
    "PENDANT LIGHT": "Pendant Light",
    "MAGNETIC TRACK LIGHT": "Magnetic Track Light",
    "COVE LIGHT": "Cove Light",
    "SLIM PROFILE(SURFACE MOUNTED)": "Slim Profile (Surface Mounted)",
    "SLIM PROFILE(surface mounted)": "Slim Profile (Surface Mounted)",
    "L-GROOVE \\PON EDGES": "L-Groove on Edges",
    "L-GROOVE ON EDGE S": "L-Groove on Edges",
    "L-GROOVE ON EDGES": "L-Groove on Edges",
    "CHIMNEY PIPE": "Chimney Pipe",
    "AC MACHINE": "AC Machine",
    "HALOGEN": "Halogen",
    "FAN POINT": "Fan Point",
    "BUTTON SPOT LIGHT": "Button Spot Light",
    "SWITCH BOARD": "Switch Board",
    "DOWN LIGHT": "Down Light",
    "GLAZER LIGHT": "Glazer Light",
}

# --- Helper functions ---
# def extract_text_from_token(s: str) -> str:
#     """Extract readable text from AutoCAD font/format tokens."""
#     m = re.search(r'\{[^}]*;([^}]*)\}', s)
#     if m:
#         return m.group(1).strip()
#     m2 = re.search(r'\\[A-Za-z0-9]+;(.+)', s)
#     if m2:
#         return m2.group(1).strip()
#     return s.strip()

# def extract_text_from_token(s: str) -> str:
#     """Extract readable text from AutoCAD font/format tokens (handles nested semicolons)."""
#     # Handles cases like: {\fISOCPEUR|b0|i0|c0|p34;\C131;Suspended Light}
#     if '{' in s and '}' in s:
#         inner = s[s.find('{') + 1 : s.rfind('}')]
#         # Take the text after the last semicolon (usually the visible label)
#         if ';' in inner:
#             inner = inner.split(';')[-1]
#         return inner.strip()
#     # Also handle \A1; or \C###; tokens outside braces
#     s = re.sub(r'\\[A-Za-z0-9]+;', '', s)
#     return s.strip()

def extract_text_from_token(s: str) -> str:
    """
    Extract readable text from AutoCAD font/format tokens.
    Handles nested braces, multiple semicolons, and embedded \P / \H / \A codes.
    """
    if not s:
        return ""
    
    # Case 1: Something like {\fISOCPEUR|b0|i0|c0|p34;\C131;Suspended\P;Light}
    if "{" in s and "}" in s:
        inner = s[s.find("{") + 1 : s.rfind("}")]
        # Remove font codes like \fISOCPEUR|...
        inner = re.sub(r'\\[A-Za-z0-9]+[;|]', ' ', inner)
        # Replace \P, \H, \A and other control sequences with spaces
        inner = re.sub(r'\\[PHAC]\d*\.?\d*[;]?', ' ', inner)
        # Take everything after the *last* semicolon, but keep if multiple words
        parts = [p.strip() for p in inner.split(';') if p.strip()]
        if parts:
            candidate = parts[-1]
            # Join split words like "Suspended" + "Light"
            candidate = candidate.replace("\\P", " ").replace("\\p", " ")
            candidate = re.sub(r'\s+', ' ', candidate).strip()
            return candidate

    # Case 2: Unbraced control codes like \A1;Suspended Light
    s = re.sub(r'\\[A-Za-z0-9]+;', ' ', s)
    s = re.sub(r'\\[PHAC]\d*\.?\d*[;]?', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def canonicalize_label(raw: str) -> str:
    """Normalize variants & apply fuzzy mapping."""
    if not raw:
        return None
    s = raw.strip().upper()
    s = re.sub(r'^[\d\.\)\- ]+', '', s)
    s = re.sub(r'[^A-Z0-9\s\-()/&]', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    if s in NORMALIZATION_MAP:
        return NORMALIZATION_MAP[s]
    if NORMALIZATION_MAP:
        choice, score, _ = process.extractOne(s, NORMALIZATION_MAP.keys(), scorer=fuzz.WRatio)
        if score >= 85:
            return NORMALIZATION_MAP[choice]
    return s.title()

def parse_legend_window(lines):
    """Extract legend entries between 'LEGEND' and next section marker."""
    start_idx = None
    for i, ln in enumerate(lines):
        if re.search(r'\blegend(s)?\b', ln, flags=re.IGNORECASE):
            start_idx = i
            break
    if start_idx is None:
        start_idx = max(0, len(lines) - 400)
    window = lines[start_idx : start_idx + 400]
    stop_markers = ["KEY PLAN", "NOTE", "DRAWN BY", "CHECKED BY", "REFERENCE"]
    # stop_markers = ["DRAWN BY", "CHECKED BY", "CLIENT", "PROJECT", "DATE", "SCALE"]

    cleaned = []
    for ln in window:
        if any(sm in ln.upper() for sm in stop_markers):
            break
        if not ln.strip():
            continue
        text = extract_text_from_token(ln)
        text = re.sub(r'\\[PH]\d*\.?\d*x?;?', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'^\s*\d{1,2}[\.\)]\s*', '', text)
        if not text:
            continue
        if re.search(r'\b(note|key plan|approval|drawing|scale)\b', text, flags=re.IGNORECASE):
            continue
        cleaned.append(text)
    return cleaned

def dedupe_and_normalize(rows):
    ordered = OrderedDict()
    for raw in rows:
        label = canonicalize_label(raw)
        if not label or label.upper().startswith("LEGEND"):
            continue
        if label not in ordered:
            ordered[label] = 0
    return list(ordered.keys())

def count_occurrences(text, labels):
    counts = {}
    for lbl in labels:
        occ = len(re.findall(re.escape(lbl), text, flags=re.IGNORECASE))
        counts[lbl] = occ if occ > 0 else None
    return counts

# --- Main function ---
# def extract_legend_from_textdump(path):
#     with open(path, "r", encoding="utf-8", errors="ignore") as f:
#         lines = [ln.rstrip("\n\r") for ln in f]
#     legend_lines = parse_legend_window(lines)
#     legend_labels = dedupe_and_normalize(legend_lines)
#     full_text = "\n".join(lines)
#     counts = count_occurrences(full_text, legend_labels)
#     lights = {lbl: {"count": counts[lbl], "category": None} for lbl in legend_labels}
#     result = {"legend": legend_labels, "lights": lights}
#     with open("legend.json", "w", encoding="utf-8") as outf:
#         json.dump(result, outf, indent=2)
#     print(f"✅ Extracted {len(legend_labels)} legend items → legend.json")
#     for i, l in enumerate(legend_labels, start=1):
#         print(f"{i:02d}. {l}  (count: {counts[l]})")

def extract_legend_from_textdump(path):
    """
    Read text dump, extract legend lines (existing logic), estimate counts,
    and ensure 'Suspended Light' is included/printed if present in the dump.
    """
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = [ln.rstrip("\n\r") for ln in f]

        legend_lines = parse_legend_window(lines)

    # dedupe and normalize (your existing function)
    legend_labels = dedupe_and_normalize(legend_lines)

    # Count occurrences (text-based estimate)
    full_text = "\n".join(lines)
    counts = count_occurrences(full_text, legend_labels)

    # --- HARDCODED SUSPENDED LIGHT CHECK (fallback) ---
    # Look for common variants of "Suspended Light" in the whole dump.
    suspended_patterns = [
        r'\bsuspended light\b',
        r'\bpended light\b',      # possible typo
        r'\bpendent light\b',     # common misspelling
        r'\bsuspend?ed\b.*\blight\b',  # flexible pattern
    ]
    suspended_count = 0
    for pat in suspended_patterns:
        suspended_count += len(re.findall(pat, full_text, flags=re.IGNORECASE))

    # If we found any occurrences, force the count and include it in legend_labels
    if suspended_count > 0:
        canonical = "Suspended Light"
        # ensure in legend_labels (preserve order: put near top if missing)
        if canonical not in legend_labels:
            legend_labels.insert(0, canonical)
        counts[canonical] = suspended_count

    # Build lights mapping (counts may be None for unknowns)
    lights = {lbl: {"count": counts.get(lbl), "category": None} for lbl in legend_labels}

    # Write the JSON result
    result = {"legend": legend_labels, "lights": lights}
    with open("legend.json", "w", encoding="utf-8") as outf:
        json.dump(result, outf, indent=2)

    # Print output: print everything as before, but also ensure Suspended Light printed only if count not None
    print(f"✅ Extracted {len(legend_labels)} legend items → legend.json\n")
    for i, l in enumerate(legend_labels, start=1):
        c = counts.get(l)
        # if user specifically only wants Suspended printed conditionally, you can uncomment the next lines:
        # if l == "Suspended Light":
        #     if c is not None:
        #         print(f"{i:02d}. {l}  (count: {c})")
        #     continue
        print(f"{i:02d}. {l}  (count: {c})")



# --- CLI ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python legend_extractor_textdump.py dwg_text_dump.txt")
        sys.exit(1)
    extract_legend_from_textdump(sys.argv[1])
