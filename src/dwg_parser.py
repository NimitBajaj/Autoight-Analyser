from __future__ import annotations
import ezdxf
from pathlib import Path
import json

def parse_dwg_with_legend(dwg_path: str):
    """
    Parse DWG (via DXF conversion) for:
    - block counts
    - raw text entities (to capture legend items)
    """
    doc = ezdxf.readfile(dwg_path)
    msp = doc.modelspace()

    # Collect block references
    block_counts: dict[str, int] = {}
    for insert in msp.query("INSERT"):
        name = insert.dxf.name
        block_counts[name] = block_counts.get(name, 0) + 1

    # Collect text entities (MText + Text)
    texts: list[str] = []
    for entity in msp.query("MTEXT TEXT"):
        if entity.dxftype() == "MTEXT":
            texts.append(entity.text)
        elif entity.dxftype() == "TEXT":
            texts.append(entity.dxf.text)

    # --- Write outputs ---
    out_dir = Path("data/outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Block counts JSON
    block_out = out_dir / "block_counts.json"
    block_out.write_text(
        json.dumps(block_counts, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"✅ Wrote block counts to {block_out}")

    # 2. Raw MTEXT dump for legend parsing
    text_out = out_dir / "dwg_text_dump.txt"
    text_out.write_text("\n".join(texts), encoding="utf-8")
    print(f"✅ Wrote raw text dump to {text_out}")

if __name__ == "__main__":
    # Example run on sample file
    sample = Path("data\\dwg_samples\\sample.dxf")
    if sample.exists():
        parse_dwg_with_legend(str(sample))
    else:
        print("⚠️ Sample DXF not found. Place a file at data/dwg_samples/sample.dxf")

