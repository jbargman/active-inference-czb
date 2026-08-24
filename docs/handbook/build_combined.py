"""Build the handbook as ONE document (Word + PDF) for sharing with a reviewer.

    python docs/handbook/build_combined.py

Concatenates chapters 00-14 in order into handbook_combined.md, then builds
word/handbook_combined.docx (revision marks colored, as in the per-chapter build)
and pdf/handbook_combined.pdf (revision marks stripped — the PDF pipeline has no
text coloring). The combined markdown is generated; edit the chapters, not it.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import build_pdf                                    # noqa: E402  docs/build_pdf.py
from build_handbook import build_docx, versioned    # noqa: E402


def main() -> None:
    chapters = sorted(HERE.glob("[0-9][0-9]_*.md"))
    parts = [c.read_text(encoding="utf-8") for c in chapters]
    combined = "\n\n---\n\n".join(parts)
    md = HERE / "handbook_combined.md"
    md.write_text(combined, encoding="utf-8")
    print("combined {} chapters -> {} ({} kB)".format(
        len(chapters), md.name, len(combined) // 1024))

    out = build_docx(md)
    print("docx:", out.name)

    stripped = re.sub(r"\{\{R\d+\}\}", "", combined)
    md_tmp = HERE / "_combined_nomarks.md"
    md_tmp.write_text(stripped, encoding="utf-8")
    pdf_out = HERE / "pdf" / "handbook_combined.pdf"
    try:
        build_pdf.build(str(md_tmp), str(pdf_out), "handbook combined")
    except PermissionError:
        pdf_out = versioned(pdf_out)
        build_pdf.build(str(md_tmp), str(pdf_out), "handbook combined")
    md_tmp.unlink()
    print("pdf: ", pdf_out.name)


if __name__ == "__main__":
    main()
