import importlib

mod = importlib.import_module("src.parsers.legend_extractor")
print("Loaded from:", mod.__file__)
print("parse_legend_terms available:", hasattr(mod, "parse_legend_terms"))