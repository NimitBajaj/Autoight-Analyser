# src/legend_extractor.py

import re

def extract_legend_from_mtext(mtext_list: list) -> dict:
    """
    Parse MTEXT lines into a {code: description} dictionary.
    Example: "01 SWITCH BOARD" -> {"01": "SWITCH BOARD"}
    """
    legend = {}
    pattern = re.compile(r"^(\d+)\s+(.*)$")  # matches "01 SWITCH BOARD"

    for text in mtext_list:
        if not text:
            continue
        line = text.strip()
        match = pattern.match(line)
        if match:
            code, desc = match.groups()
            legend[code] = desc.strip()

    return legend