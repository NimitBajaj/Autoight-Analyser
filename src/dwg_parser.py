import ezdxf
import json
from pathlib import Path
from src.parsers.legend_extractor import parse_legend_terms


def collect_all_text(doc) -> list[str]:
    all_texts = []

    # Modelspace
    all_texts.extend([e.dxf.text for e in doc.modelspace().query("TEXT")])
    all_texts.extend([e.text for e in doc.modelspace().query("MTEXT")])

    # Blocks (including anonymous ones like *U10)
    for block in doc.blocks:
        for e in block.query("TEXT"):
            all_texts.append(e.dxf.text)
        for e in block.query("MTEXT"):
            all_texts.append(e.text)
        for e in block.query("ATTRIB"):
            all_texts.append(e.dxf.text)
        for e in block.query("ATTDEF"):
            all_texts.append(e.dxf.text)

    # Normalize
    return [t.strip() for t in all_texts if t and t.strip()]

def parse_dwg_with_legend(file_path: str, output_dir: str = "data/outputs") -> None:
    """
    Parse DWG/DXF file:
    - Count block inserts
    - Extract legend terms from MTEXT
    - Write both to a text file (human-readable)
    - Save block counts JSON for linker
    """
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()

    # --- Step 1: Count block inserts ---
    block_counts = {}
    for entity in msp.query("INSERT"):
        block_name = entity.dxf.name
        block_counts[block_name] = block_counts.get(block_name, 0) + 1

    # --- Step 2: Extract legend terms ---

    all_texts = collect_all_text(doc)
    raw_text = "\n".join(all_texts)

    legend_items = parse_legend_terms(raw_text)
    print("---- RAW MTEXT DUMP ----")
    print(raw_text[:1000])  # print first 1000 chars
    print("---- PARSED LEGEND ITEMS ----")
    print(legend_items)

    # --- Step 3: Write results ---
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # human-readable text file
    with open(output_path / "dwg_with_legend.txt", "w", encoding="utf-8") as f:
        f.write(">>> BLOCK COUNTS (raw)\n")
        for block, count in block_counts.items():
            f.write(f"{block}: {count}\n")

        f.write("\n>>> LEGEND (items)\n")
        for item in legend_items:
            f.write(f"{item}\n")

    # JSON for linker
    (output_path / "block_counts.json").write_text(
        json.dumps(block_counts, indent=2),
        encoding="utf-8"
    )

    print(f"✅ Outputs written to {output_path.resolve()}")

if __name__ == "__main__":
    # use forward slashes for safety
    parse_dwg_with_legend("data\\dwg_samples\\sample.dxf")

