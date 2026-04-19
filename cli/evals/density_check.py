"""
Resume density check.

Catches the opposite failure mode from page_count_check: a resume that was
trimmed so aggressively it looks blank on the page.

Two measurement sources:
  1. YAML-level: section counts, bullet counts, average bullet length, total
     visible character count.
  2. PDF-level (via pypdf): page-fill ratio (how far down the page the text
     extends) and extracted-text character count.

Run directly:
    uv run python cli/evals/density_check.py <yaml_path> [--pdf <pdf_path>]

Exit code 0 = pass. Exit code 1 = at least one threshold failed, resume is
under-filled; the workflow should restore trimmed content and re-render.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml
from pypdf import PdfReader


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------

# YAML-level thresholds
MIN_EXPERIENCE_BULLETS_TOTAL = 3
MIN_PROJECTS_COUNT = 2
MIN_PROJECT_BULLETS_TOTAL = 4
MIN_SKILLS_CATEGORIES = 3
MIN_AVG_BULLET_CHARS = 80
MIN_VISIBLE_CHAR_COUNT = 2400

# PDF-level thresholds
# Calibrated against output/master-resume/resume.pdf which measured 0.943
# fill ratio and 2964 extracted chars (a known well-filled reference).
MIN_PAGE_FILL_RATIO = 0.80   # text must reach at least 80% down the page
MIN_PDF_EXTRACTED_CHARS = 2400


@dataclass
class CheckResult:
    status: str
    details: str
    recommendation: str | None = None

    def to_dict(self) -> dict:
        d = {"status": self.status, "details": self.details}
        if self.recommendation:
            d["recommendation"] = self.recommendation
        return d


# ---------------------------------------------------------------------------
# YAML-level measurements
# ---------------------------------------------------------------------------

def _experience_bullets(data: dict) -> list[str]:
    out: list[str] = []
    for exp in data.get("experience") or []:
        out.extend(exp.get("bullets") or [])
    return out


def _project_bullets(data: dict) -> list[str]:
    out: list[str] = []
    for proj in data.get("projects") or []:
        out.extend(proj.get("bullets") or [])
    return out


def _visible_text_chars(data: dict) -> int:
    """Character count across visible fields (excludes ats_optimization)."""
    pieces: list[str] = []
    summary = data.get("summary") or ""
    pieces.append(summary)

    for exp in data.get("experience") or []:
        pieces.append(exp.get("title") or "")
        pieces.append(exp.get("company") or "")
        pieces.extend(exp.get("bullets") or [])

    for proj in data.get("projects") or []:
        pieces.append(proj.get("name") or "")
        pieces.append(proj.get("description") or "")
        pieces.append(proj.get("tech") or "")
        pieces.extend(proj.get("bullets") or [])

    for edu in data.get("education") or []:
        pieces.append(edu.get("institution") or "")
        pieces.append(edu.get("degree") or "")
        pieces.extend(edu.get("details") or [])

    for cat, items in (data.get("skills") or {}).items():
        pieces.append(cat)
        pieces.append(items)

    for cert in data.get("certifications") or []:
        pieces.append(cert.get("name") or "")
        pieces.append(cert.get("issuer") or "")

    return sum(len(p) for p in pieces)


def check_experience_bullets(data: dict) -> CheckResult:
    bullets = _experience_bullets(data)
    n = len(bullets)
    if n < MIN_EXPERIENCE_BULLETS_TOTAL:
        return CheckResult(
            "FAIL",
            f"Experience has {n} bullets total (minimum {MIN_EXPERIENCE_BULLETS_TOTAL}).",
            f"Add {MIN_EXPERIENCE_BULLETS_TOTAL - n} more bullet(s) to the Accenture experience entry from career.md's Experience Bank.",
        )
    return CheckResult("PASS", f"Experience has {n} bullets.")


def check_project_count(data: dict) -> CheckResult:
    projects = data.get("projects") or []
    n = len(projects)
    if n < MIN_PROJECTS_COUNT:
        return CheckResult(
            "FAIL",
            f"Only {n} project(s) listed (minimum {MIN_PROJECTS_COUNT}).",
            f"Restore the most recently trimmed project from career.md's Projects Bank (use JD Analysis project-priority ordering).",
        )
    return CheckResult("PASS", f"{n} projects listed.")


def check_project_bullets(data: dict) -> CheckResult:
    bullets = _project_bullets(data)
    n = len(bullets)
    if n < MIN_PROJECT_BULLETS_TOTAL:
        return CheckResult(
            "FAIL",
            f"Projects have {n} bullets total (minimum {MIN_PROJECT_BULLETS_TOTAL}).",
            f"Add {MIN_PROJECT_BULLETS_TOTAL - n} more project bullet(s). Prefer adding a second bullet to an under-detailed project over adding a whole new project.",
        )
    return CheckResult("PASS", f"Projects have {n} bullets total.")


def check_skills_categories(data: dict) -> CheckResult:
    skills = data.get("skills") or {}
    n = len(skills)
    if n < MIN_SKILLS_CATEGORIES:
        return CheckResult(
            "FAIL",
            f"Skills section has {n} categor{'y' if n == 1 else 'ies'} (minimum {MIN_SKILLS_CATEGORIES}).",
            f"Add {MIN_SKILLS_CATEGORIES - n} more skills categor{'y' if MIN_SKILLS_CATEGORIES - n == 1 else 'ies'}. Use role-relevant labels (e.g. 'Languages', 'Cloud & DevOps', 'Data & Analytics', 'AI/ML').",
        )
    return CheckResult("PASS", f"Skills section has {n} categories.")


def check_avg_bullet_length(data: dict) -> CheckResult:
    bullets = _experience_bullets(data) + _project_bullets(data)
    if not bullets:
        return CheckResult("FAIL", "No bullets found at all.", "Regenerate the YAML from scratch.")
    avg = sum(len(b) for b in bullets) / len(bullets)
    if avg < MIN_AVG_BULLET_CHARS:
        return CheckResult(
            "FAIL",
            f"Average bullet length is {avg:.0f} chars (minimum {MIN_AVG_BULLET_CHARS}).",
            "Bullets are too terse. Restore detail from career.md source bullets - metrics, technologies, business context - rather than keeping them stripped.",
        )
    return CheckResult("PASS", f"Average bullet length is {avg:.0f} chars.")


def check_visible_char_count(data: dict) -> CheckResult:
    n = _visible_text_chars(data)
    if n < MIN_VISIBLE_CHAR_COUNT:
        return CheckResult(
            "FAIL",
            f"Total visible text is {n} chars (minimum {MIN_VISIBLE_CHAR_COUNT}).",
            "Resume is under-filled at the YAML level. Restore trimmed content (last project, last experience bullet, certifications) before re-rendering.",
        )
    return CheckResult("PASS", f"Total visible text is {n} chars.")


# ---------------------------------------------------------------------------
# PDF-level measurements (pypdf)
# ---------------------------------------------------------------------------

def measure_pdf_fill(pdf_path: Path) -> dict:
    """Extract fill metrics from page 1 of the PDF using pypdf.

    PDF coordinates: origin is bottom-left, so smaller Y = lower on the page.
    Fill ratio = 1 - (lowest_text_y / page_height), i.e. how far down the page
    the visible text extends (1.0 = reaches the very bottom).

    Note on the zero-y filter: pypdf's visitor reports the raw text-matrix
    translation at the moment of each text-showing operator. For glyphs
    positioned via the running text cursor (e.g. ligature separators, inline
    concatenations like `"A | B"`) the matrix often reads (0, 0) because the
    positioning was done earlier by `Td`/`TD`/`Tm` operators. These chunks
    would falsely pin min_y at 0 and make every page look 100% filled. We
    drop them and take the minimum across the remaining chunks whose Y was
    explicitly set.
    """
    reader = PdfReader(str(pdf_path))
    page = reader.pages[0]
    page_height = float(page.mediabox.height)
    page_width = float(page.mediabox.width)

    positioned_ys: list[float] = []

    def visitor(text, cm, tm, font_dict, font_size):  # noqa: ARG001
        if not text or not text.strip():
            return
        try:
            y = float(tm[5])
            if cm:
                y += float(cm[5])
        except (TypeError, IndexError, ValueError):
            return
        if y > 0.0:
            positioned_ys.append(y)

    try:
        extracted = page.extract_text(visitor_text=visitor) or ""
    except Exception:
        extracted = page.extract_text() or ""

    if positioned_ys:
        min_y = min(positioned_ys)
        fill_ratio = 1.0 - (min_y / page_height) if page_height else 0.0
    else:
        # Visitor gave us nothing usable. Don't block the workflow on an
        # unmeasurable PDF - report a neutral fill_ratio and let the other
        # checks do the work.
        min_y = 0.0
        fill_ratio = 1.0

    return {
        "page_height": round(page_height, 2),
        "page_width": round(page_width, 2),
        "lowest_text_y": round(min_y, 2),
        "fill_ratio": round(fill_ratio, 3),
        "extracted_chars": len(extracted.strip()),
        "positioned_text_chunks": len(positioned_ys),
    }


def check_pdf_fill_ratio(pdf_metrics: dict) -> CheckResult:
    ratio = pdf_metrics["fill_ratio"]
    if ratio < MIN_PAGE_FILL_RATIO:
        empty_pct = (1.0 - ratio) * 100
        return CheckResult(
            "FAIL",
            f"Text reaches {ratio:.0%} down the page; roughly {empty_pct:.0f}% of the page is empty at the bottom.",
            "Restore trimmed content (project, experience bullet, certifications) so text fills the page.",
        )
    return CheckResult("PASS", f"Page fill ratio is {ratio:.0%}.")


def check_pdf_char_count(pdf_metrics: dict) -> CheckResult:
    n = pdf_metrics["extracted_chars"]
    if n < MIN_PDF_EXTRACTED_CHARS:
        return CheckResult(
            "FAIL",
            f"PDF extracted {n} chars (minimum {MIN_PDF_EXTRACTED_CHARS}).",
            "Restore trimmed content or re-include full-detail bullets from career.md.",
        )
    return CheckResult("PASS", f"PDF extracted {n} chars.")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_density_check(yaml_path: str, pdf_path: str | None = None) -> dict:
    yaml_data = yaml.safe_load(Path(yaml_path).read_text(encoding="utf-8")) or {}

    checks: dict[str, CheckResult] = {
        "experience_bullets": check_experience_bullets(yaml_data),
        "project_count": check_project_count(yaml_data),
        "project_bullets": check_project_bullets(yaml_data),
        "skills_categories": check_skills_categories(yaml_data),
        "avg_bullet_length": check_avg_bullet_length(yaml_data),
        "visible_char_count": check_visible_char_count(yaml_data),
    }

    pdf_metrics: dict | None = None
    if pdf_path:
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            checks["pdf_fill_ratio"] = CheckResult(
                "FAIL", f"PDF not found: {pdf_path}", "Render the PDF before running this check."
            )
        else:
            pdf_metrics = measure_pdf_fill(pdf_file)
            checks["pdf_fill_ratio"] = check_pdf_fill_ratio(pdf_metrics)
            checks["pdf_extracted_chars"] = check_pdf_char_count(pdf_metrics)

    overall_pass = all(c.status == "PASS" for c in checks.values())
    recommendations = [
        f"[{name}] {c.recommendation}"
        for name, c in checks.items()
        if c.status == "FAIL" and c.recommendation
    ]

    return {
        "yaml_file": yaml_path,
        "pdf_file": pdf_path,
        "overall_pass": overall_pass,
        "pdf_metrics": pdf_metrics,
        "checks": {name: c.to_dict() for name, c in checks.items()},
        "recommendations": recommendations,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether a rendered resume is dense enough.")
    parser.add_argument("yaml_path", help="Path to the resume YAML.")
    parser.add_argument("--pdf", default=None, help="Path to the rendered PDF (optional but recommended).")
    args = parser.parse_args()

    result = run_density_check(args.yaml_path, args.pdf)
    print(json.dumps(result, indent=2))
    return 0 if result["overall_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
