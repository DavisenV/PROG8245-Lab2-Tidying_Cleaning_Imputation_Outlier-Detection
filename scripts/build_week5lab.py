"""Build week5Lab.ipynb: the four section notebooks combined into one, in the handout's order.

The section notebooks in notebooks/ are the source of truth. This script copies
their cells into a single notebook in the project root, after an introduction
and a replicability check, and ends with the handout's submission checklist.

Run from the project root, then open week5Lab.ipynb and choose Restart & Run All:

    python scripts/build_week5lab.py

Only the standard library is used, so it adds nothing to requirements.txt.
"""

import json
import re
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT_ROOT / "week5Lab.ipynb"
INTRO = PROJECT_ROOT / "scripts" / "week5lab_intro.md"
CHECKLIST = PROJECT_ROOT / "scripts" / "week5lab_checklist.md"
SECTIONS = [
    "notebooks/pew.ipynb",
    "notebooks/billboard_section.ipynb",
    "notebooks/car_section.ipynb",
    "notebooks/diabetes.ipynb",
]
CELL_SEPARATOR = "<!-- new cell -->"


def markdown_cell(text):
    return {"cell_type": "markdown", "id": uuid.uuid4().hex[:8], "metadata": {}, "source": text.strip("\n")}


def markdown_cells_from(path):
    """Split a Markdown file into notebook cells at each CELL_SEPARATOR line."""
    return [markdown_cell(part) for part in path.read_text().split(CELL_SEPARATOR) if part.strip()]


def demote_headings(text):
    """Add one '#' to every Markdown heading outside fenced code blocks."""
    lines, in_fence = [], False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        elif not in_fence and re.match(r"#{1,5} ", line):
            line = "#" + line
        lines.append(line)
    return "\n".join(lines)


def section_cells(path):
    """Copy a section notebook's cells: keep its title as H1, nest everything else one level down."""
    cells = json.loads((PROJECT_ROOT / path).read_text())["cells"]
    copied = []
    for index, cell in enumerate(cells):
        source = "".join(cell["source"])
        if cell["cell_type"] == "markdown":
            if index == 0:
                title, _, rest = source.partition("\n")
                source = title + ("\n" + demote_headings(rest) if rest else "")
            else:
                source = demote_headings(source)
            source = source.replace("](../", "](")  # links are now relative to the project root
            copied.append({"cell_type": "markdown", "id": cell.get("id"), "metadata": {}, "source": source})
        else:
            copied.append({"cell_type": "code", "id": cell.get("id"), "metadata": {},
                           "execution_count": None, "outputs": [], "source": source})
    return copied


def build():
    cells = markdown_cells_from(INTRO)
    for path in SECTIONS:
        cells += section_cells(path)
    cells += markdown_cells_from(CHECKLIST)

    seen = set()
    for cell in cells:  # cell ids must be unique within one notebook
        while not cell["id"] or cell["id"] in seen:
            cell["id"] = uuid.uuid4().hex[:8]
        seen.add(cell["id"])

    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    OUTPUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n")
    print(f"Wrote {OUTPUT.relative_to(PROJECT_ROOT)} ({len(cells)} cells from {len(SECTIONS)} sections)")


if __name__ == "__main__":
    build()
