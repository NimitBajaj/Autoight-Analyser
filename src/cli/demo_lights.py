import sys
import json
import re
from pathlib import Path

from src.dwg_parser import parse_dwg_with_legend
from src.parsers.legend_extractor import parse_legend_terms


def normalize_light_name(name: str) -> str:
    """Normalize common variations of light names."""
    name = name.strip().title()

    synonyms = {
        "Pendent Light": "Pendant Light",
        "Pendant Light": "Pendant Light",
        "Magnetic Track Light": "Magnetic Track Light",
        "Cove Light": "Cove Light",
        "Down Light": "Down Light",
        "Spot Light": "Spot Light",
        "Suspended Light": "Suspended Light",
    }

    return synonyms.get(name, name)


def categorize_light(name: str) -> str:
    """Assign each light type to a broad category."""
    n = name.lower()
    if "pendant" in n or "suspended" in n:
        return "Hanging"
    if "track" in n:
        return "Track"
    if "cove" in n:
        return "Indirect"
    if "spot" in n or "down" in n:
        return "Recessed"
    return "Other"


def count_lights_from_text(raw_text: str, legend_items) -> dict:
    """Robustly count light occurrences in the raw text."""
    counts = {}

    for item in legend_items:
        norm_item = normalize_light_name(item)
        if "light" not in norm_item.lower():
            continue  # only count lighting symbols

        # Flexible regex: match ignoring case & multiple spaces
        pattern = re.compile(r"\b" + re.escape(item) + r"\b", re.IGNORECASE)
        matches = pattern.findall(raw_text)
        if matches:
            counts[norm_item] = counts.get(norm_item, 0) + len(matches)

    return counts


def main():
    if len(sys.argv) < 3:
        print("Usage: python -m src.cli.demo_lights <input_dxf_or_txt> <output_json>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    # Step 1: Parse raw text from DWG/DXF
    if input_path.suffix.lower() == ".txt":
     raw_text = input_path.read_text(encoding="utf-8", errors="ignore")
    else:
     raw_text = parse_dwg_with_legend(input_path)

    # Step 2: Extract legend items
    legend_items = parse_legend_terms(raw_text)

    # Step 3: Count light occurrences
    raw_counts = count_lights_from_text(raw_text, legend_items)

    # Step 4: Normalize + categorize
    lights = {}
    for k, v in raw_counts.items():
        norm = normalize_light_name(k)
        lights[norm] = {
            "count": v,
            "category": categorize_light(norm),
        }

    # Step 5: Save final JSON
    out = {"legend": legend_items, "lights": lights}
    output_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    # Always save to a fixed location for reporting pipeline
    default_counts_path = Path("data/outputs/demo_lights.json")
    default_counts_path.parent.mkdir(parents=True, exist_ok=True)
    default_counts_path.write_text(json.dumps(lights, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"✅ Demo output written to {output_path}")
    print(f"✅ Counts also written to {default_counts_path} for reporting")

if __name__ == "__main__":
    main()
