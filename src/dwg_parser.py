# src/parse_dwg_debug.py
import ezdxf
from pathlib import Path


def debug_parse_dwg(file_path: str, output_file: str = "data/outputs/dwg_debug.txt"):
    print(f"\n--- Parsing DWG: {file_path} ---\n")

    # Load DWG file
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()

    output_lines = []

    # 1. Block Inserts
    output_lines.append(">>> Block Inserts (symbols):")
    block_counts = {}
    for entity in msp.query("INSERT"):
        block_name = entity.dxf.name
        block_counts[block_name] = block_counts.get(block_name, 0) + 1
    for name, count in block_counts.items():
        output_lines.append(f"  {name}: {count}")

    # 2. TEXT objects
    output_lines.append("\n>>> TEXT objects:")
    for entity in msp.query("TEXT"):
        output_lines.append(f"  TEXT: {entity.dxf.text}")

    # 3. MTEXT objects
    output_lines.append("\n>>> MTEXT objects:")
    for entity in msp.query("MTEXT"):
        text = entity.text
        snippet = text.replace("\n", " ")
        output_lines.append(f"  MTEXT: {snippet}")

    # Write to file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    print(f"✅ Debug output written to: {output_path.resolve()}")

from legend_extractor import extract_legend_from_mtext

# Example subset from your DWG debug file
sample_mtext = [
    "01 SWITCH BOARD",
    "02 SUSPENDED LIGHT",
    "03 FAN POINT",
    "04 SPOT LIGHT"
]

legend = extract_legend_from_mtext(sample_mtext)
print("Extracted Legend:", legend)

if __name__ == "__main__":
    # Replace with your DWG file path
    debug_parse_dwg("data\\dwg_samples\\sample.dxf")
