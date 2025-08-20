import ezdxf

def dump_all_entities(file_path: str, limit: int = 5000):
    doc = ezdxf.readfile(file_path)

    print("---- SCANNING ALL ENTITIES ----")

    def dump_entity(e, prefix=""):
        etype = e.dxftype()
        print(f"{prefix}{etype}")
        if hasattr(e.dxf, "text"):
            print(f"{prefix}   dxf.text: {e.dxf.text}")
        if hasattr(e, "text"):
            print(f"{prefix}   text: {e.text}")
        if hasattr(e.dxf, "value"):
            print(f"{prefix}   dxf.value: {e.dxf.value}")
        # catch-all: dump attributes dictionary
        try:
            for name in dir(e.dxf):
                if not name.startswith("_"):
                    val = getattr(e.dxf, name)
                    if isinstance(val, str) and val.strip():
                        print(f"{prefix}   dxf.{name}: {val}")
        except Exception:
            pass

    # Modelspace
    for i, e in enumerate(doc.modelspace()):
        dump_entity(e)
        if i > limit:
            break

    # Blocks
    for block in doc.blocks:
        print(f"\nBLOCK: {block.name}")
        for e in block:
            dump_entity(e, prefix="  ")

if __name__ == "__main__":
    dump_entities("data\\dwg_samples\\sample.dxf")