import json, sys
from pathlib import Path
from src.linking.legend_linker import link_legend_to_blocks

def main():
    if len(sys.argv) < 4:
        print("Usage: python -m cli.link_legend <legend.json> <block_counts.json> <out_json>")
        sys.exit(1)
    legend_json = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    block_counts = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    items = legend_json.get("legend_items", [])
    results = link_legend_to_blocks(items, block_counts)
    payload = [
        {
            "legend_item": r.legend_item,
            "best_block": r.best_block,
            "score": round(r.score, 3),
            "candidates": [(n, round(s, 3)) for n, s in r.candidates]
        }
        for r in results
    ]
    Path(sys.argv[3]).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote mapping suggestions for {len(payload)} legend items")

if __name__ == "__main__":
    main()
