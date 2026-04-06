"""
PDF page count checker.

Standalone script - run directly:
    uv run python cli/evals/page_count_check.py <pdf_path>

Output: JSON with page count and pass/fail (pass = exactly 1 page).
"""

import json
import sys
from pathlib import Path

from pypdf import PdfReader


def count_pages(pdf_path: str) -> int:
    """Count pages in a PDF file using pypdf."""
    reader = PdfReader(pdf_path)
    return len(reader.pages)


def check_page_count(pdf_path: str, expected: int = 1) -> dict:
    """Check if PDF has the expected number of pages."""
    path = Path(pdf_path)
    if not path.exists():
        return {
            "pdf_file": pdf_path,
            "pages": 0,
            "expected": expected,
            "pass": False,
            "error": f"File not found: {pdf_path}",
        }

    try:
        pages = count_pages(pdf_path)
        return {
            "pdf_file": pdf_path,
            "pages": pages,
            "expected": expected,
            "pass": pages == expected,
        }
    except Exception as e:
        return {
            "pdf_file": pdf_path,
            "pages": 0,
            "expected": expected,
            "pass": False,
            "error": str(e),
        }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cli/evals/page_count_check.py <pdf_path>", file=sys.stderr)
        sys.exit(2)

    result = check_page_count(sys.argv[1])
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["pass"] else 1)
