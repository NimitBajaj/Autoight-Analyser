from setuptools import setup, find_packages

setup(
    name="Autoight-Analyser",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # Add your dependencies here, e.g.,
        # "ezdxf",
        # "pdfplumber",
        # "fpdf2",
    ],
    entry_points={
        "console_scripts": [
            # Add CLI entry points here if needed
        ],
    },
)