from __future__ import annotations

import argparse
import re
from pathlib import Path

from pypdf import PdfReader


def ingest(pdf_path: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    extracted_path = output_dir / "AstroDOc.extracted.txt"
    cleaned_path = output_dir / "AstroDOc.cleaned.txt"
    llm_path = output_dir / "AstroDOc.llm.txt"

    reader = PdfReader(str(pdf_path))
    page_text = [(p.extract_text() or "") for p in reader.pages]
    extracted = "\n\n".join(page_text)
    cleaned = re.sub(r"[ \t]+", " ", re.sub(r"\n{3,}", "\n\n", extracted.replace("\r", "\n")))
    llm_text = re.sub(r"\s+", " ", extracted).strip()

    extracted_path.write_text(extracted, encoding="utf-8")
    cleaned_path.write_text(cleaned, encoding="utf-8")
    llm_path.write_text(llm_text, encoding="utf-8")

    print(f"pages={len(reader.pages)}")
    print(f"extracted_chars={len(extracted)} -> {extracted_path}")
    print(f"cleaned_chars={len(cleaned)} -> {cleaned_path}")
    print(f"llm_chars={len(llm_text)} -> {llm_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest AstroDoc PDF into LLM-ready knowledge files.")
    parser.add_argument("pdf", type=Path, help="Path to AstroDOc PDF")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("app/knowledge"),
        help="Output directory for extracted knowledge files",
    )
    args = parser.parse_args()

    if not args.pdf.exists():
        print(f"PDF not found: {args.pdf}")
        return 1

    ingest(args.pdf, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

