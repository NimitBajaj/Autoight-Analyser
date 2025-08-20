import json, sys
from pathlib import Path
from src.parsers.legend_extractor import parse_legend_terms
import sys
print(">>> Using parse_legend_terms from:", sys.modules.get("parsers.legend_extractor"))

def main():
    if len(sys.argv) < 3:
        print("Usage: python -m cli.extract_legend <dwg_text_dump.txt> <out_json>")
        sys.exit(1)
    inp, outp = Path(sys.argv[1]), Path(sys.argv[2])
    text = inp.read_text(encoding="utf-8", errors="ignore")
    items = parse_legend_terms(text)
    outp.write_text(json.dumps({"legend_items": items}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(items)} legend items to {outp}")

if __name__ == "__main__":
    main()
