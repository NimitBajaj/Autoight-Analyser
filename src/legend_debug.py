import ezdxf
from pathlib import Path

def dump_all_text(file_path: str, output_file: str = "data/outputs/legend_debug_full.txt"):
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()

    lines = []

    lines.append(">>> TEXT objects")
    for entity in msp.query("TEXT"):
        lines.append(f"TEXT: {repr(entity.dxf.text)}")

    lines.append("\n>>> MTEXT objects")
    for entity in msp.query("MTEXT"):
        lines.append(f"MTEXT: {repr(entity.text)}")

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ Full text dump written to {output_path.resolve()}")

if __name__ == "__main__":
    dump_all_text("data\dwg_samples\sample.dxf")