import sys, json
from pathlib import Path
from src.parsers.legend_extractor import parse_legend_terms

def main():
    if len(sys.argv) < 3:
        print("Usage: python -m src.cli.extract_legend <input_txt> <output_json>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    raw_text = input_path.read_text(encoding="utf-8")

    print("---- RAW INPUT START ----")
    print(raw_text[:500])   # only show first 500 chars
    print("---- RAW INPUT END ----")

    legend_items = parse_legend_terms(raw_text)
    # 👇 add debug print here
    print("---- LEGEND ITEMS ----")
    for item in legend_items:
        print("  •", item)

    output_path.write_text(json.dumps(legend_items, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n✅ Wrote {len(legend_items)} legend items to {output_path}")

if __name__ == "__main__":
    main()

