import json
import sys
from pathlib import Path
from rapidfuzz import fuzz

# Only keep lighting-related legend terms
LIGHT_KEYWORDS = {"light", "lamp", "track", "pendent", "pendant", "spot", "cove", "halogen", "chandelier"}

def is_lighting_item(item: str) -> bool:
    """Check if a legend item is lighting-related by keyword."""
    low = item.lower()
    return any(kw in low for kw in LIGHT_KEYWORDS)

def count_lights(legend_items, dwg_lines, threshold=80):
    """Fuzzy match legend items against DWG text lines and count occurrences."""
    counts = {}
    for legend in legend_items:
        if not is_lighting_item(legend):
            continue  # skip non-light symbols

        count = 0
        for line in dwg_lines:
            score = fuzz.token_sort_ratio(legend.lower(), line.lower())
            if score >= threshold:
                count += 1
        if count > 0:
            counts[legend] = count
    return counts


def main(text_dump_path: str, legend_json_path: str, output_json_path: str):
    # Load text dump
    dump_path = Path(text_dump_path)
    text_lines = dump_path.read_text(encoding="utf-8").splitlines()

    # Load legend items
    legend_items = json.loads(Path(legend_json_path).read_text(encoding="utf-8"))

    # Count lighting symbols
    counts = count_lights(legend_items, text_lines)

    # Save results
    out_path = Path(output_json_path)
    out_path.write_text(json.dumps(counts, indent=2, ensure_ascii=False), encoding="utf-8")

    # Print results
    print("---- LIGHT COUNTS ----")
    for k, v in counts.items():
        print(f"  • {k}: {v}")
    print(f"\n✅ Wrote {len(counts)} light counts to {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python -m src.cli.extract_lights <dwg_text_dump.txt> <legend_items.json> <output.json>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])