"""
Resume YAML validator.

Standalone script - run directly:
    uv run python cli/evals/resume_eval.py <yaml_path> [--career career.md]

Checks:
    1. Pydantic schema validation
    2. Banned phrase scan
    3. Em dash detection
    4. Passive voice heuristic
    5. Summary sentence count (2-4)
    6. Skill cross-reference against career.md
    7. Year arithmetic validation
"""

import json
import re
import sys
from pathlib import Path

# Ensure project root is on sys.path for standalone execution
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import yaml


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BANNED_PHRASES = [
    "proven track record",
    "passionate about",
    "deep expertise",
    "extensive experience",
    "strong background in",
    "results-driven",
    "proven experience",
    "strong understanding",
    "demonstrated ability",
    "well-versed",
    "cutting-edge",
    "state-of-the-art",
    "best-in-class",
    "world-class",
    "synergy",
    "synergies",
    "holistic",
]

PASSIVE_STARTERS = [
    "was ", "were ", "has been ", "had been ", "have been ",
    "is being ", "are being ", "was being ", "were being ",
    "been ", "being ", "got ", "gets ", "getting ",
    "responsible for ", "tasked with ", "involved in ",
    "assisted with ", "helped with ", "participated in ",
]

# Technologies / tools that can appear in career.md (extracted at runtime)
_TECH_PATTERN = re.compile(
    r"\b(?:Python|Java|SQL|ABAP|Kotlin|JavaScript|TypeScript|Vue[\s.]?3|React|"
    r"AWS|CDK|Lambda|S3|RDS|CloudFront|PostgreSQL|MySQL|Firebase|Firestore|"
    r"Docker|Kubernetes|FastAPI|ONNX|YOLO|TensorFlow|Locust|PostGIS|GTFS|"
    r"Hono|Vite|Tailwind|PrimeVue|SendGrid|Resend|Tableau|NewsAPI|"
    r"SAP\s*BW|HANA|S/4HANA|MATLAB|Simulink|"
    r"Git|Agile|DevOps|REST|API|HTTP|OAuth|"
    r"BeautifulSoup|Foursquare|cvxopt|MPPT)\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_all_text(data: dict) -> list[str]:
    """Recursively extract all string values from nested dicts/lists."""
    texts: list[str] = []
    if isinstance(data, str):
        texts.append(data)
    elif isinstance(data, dict):
        for v in data.values():
            texts.extend(_extract_all_text(v))
    elif isinstance(data, list):
        for item in data:
            texts.extend(_extract_all_text(item))
    return texts


def _extract_bullets(data: dict) -> list[str]:
    """Extract all bullet-point strings from experience and projects."""
    bullets: list[str] = []
    for exp in data.get("experience", []):
        bullets.extend(exp.get("bullets", []))
    for proj in data.get("projects", []):
        bullets.extend(proj.get("bullets", []) or [])
    return bullets


def _load_career(career_path: Path) -> str:
    return career_path.read_text(encoding="utf-8")


def _count_sentences(text: str) -> int:
    """Rough sentence count based on period/exclamation/question marks."""
    sentences = re.split(r'[.!?]+', text.strip())
    return len([s for s in sentences if s.strip()])


def _parse_years(career_text: str) -> dict[str, float]:
    """Extract experience date-ranges and compute years."""
    results = {}
    # Match patterns like "Aug 2019 - Jan 2024"
    pattern = re.compile(
        r"(\w{3,9}\s+\d{4})\s*[-–—]\s*(\w{3,9}\s+\d{4})",
    )
    from datetime import datetime
    for match in pattern.finditer(career_text):
        start_str, end_str = match.group(1), match.group(2)
        for fmt in ("%B %Y", "%b %Y"):
            try:
                start = datetime.strptime(start_str, fmt)
                end = datetime.strptime(end_str, fmt)
                years = (end - start).days / 365.25
                results[f"{start_str} - {end_str}"] = round(years, 1)
                break
            except ValueError:
                continue
    return results


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_schema(data: dict) -> dict:
    """Validate against ResumeSchema."""
    try:
        from cli.schemas.resume import ResumeSchema
        ResumeSchema.model_validate(data)
        return {"status": "PASS", "details": "Schema valid"}
    except Exception as e:
        return {"status": "FAIL", "details": str(e)}


def check_banned_phrases(data: dict) -> dict:
    """Scan all text for banned filler phrases."""
    all_text = " ".join(_extract_all_text(data)).lower()
    found = [p for p in BANNED_PHRASES if p in all_text]
    if found:
        return {"status": "FAIL", "details": f"Banned phrases found: {found}"}
    return {"status": "PASS", "details": "No banned phrases"}


def check_em_dashes(data: dict) -> dict:
    """Detect em dashes and en dashes."""
    all_text = " ".join(_extract_all_text(data))
    em_count = all_text.count("—")
    en_count = all_text.count("–")
    if em_count + en_count > 0:
        return {
            "status": "FAIL",
            "details": f"Found {em_count} em dashes and {en_count} en dashes. Use ' - ' instead.",
        }
    return {"status": "PASS", "details": "No em/en dashes found"}


def check_passive_voice(data: dict) -> dict:
    """Check bullet starts for passive voice patterns."""
    bullets = _extract_bullets(data)
    passive_bullets = []
    for b in bullets:
        lower = b.strip().lower()
        for starter in PASSIVE_STARTERS:
            if lower.startswith(starter):
                passive_bullets.append(b[:80] + "..." if len(b) > 80 else b)
                break
    if passive_bullets:
        return {"status": "FAIL", "details": f"Passive voice bullets: {passive_bullets}"}
    return {"status": "PASS", "details": "All bullets use active voice"}


def check_summary_length(data: dict) -> dict:
    """Verify summary is 2-4 sentences."""
    summary = data.get("summary", "")
    if not summary:
        return {"status": "PASS", "details": "No summary (optional field)"}
    count = _count_sentences(summary)
    if count < 2 or count > 4:
        return {"status": "FAIL", "details": f"Summary has {count} sentences (expected 2-4)"}
    return {"status": "PASS", "details": f"Summary has {count} sentences"}


def _extract_all_text_excluding_ats(data: dict) -> list[str]:
    """Extract all text from YAML but EXCLUDE the ats_optimization field.

    The ats_optimization field intentionally contains JD-borrowed keywords
    for ATS matching and should NOT be validated against career.md.
    """
    texts: list[str] = []
    if isinstance(data, dict):
        for k, v in data.items():
            if k == "ats_optimization":
                continue  # Skip ATS field - it's allowed to have JD keywords
            texts.extend(_extract_all_text_excluding_ats(v))
    elif isinstance(data, str):
        texts.append(data)
    elif isinstance(data, list):
        for item in data:
            texts.extend(_extract_all_text_excluding_ats(item))
    return texts


def check_skills_against_career(data: dict, career_text: str) -> dict:
    """Verify every mentioned technology in VISIBLE content exists in career.md.

    Note: ats_optimization is excluded - it intentionally mirrors JD keywords
    for ATS matching and is rendered as invisible text in the PDF.
    """
    visible_text = " ".join(_extract_all_text_excluding_ats(data))
    yaml_techs = set(m.lower() for m in _TECH_PATTERN.findall(visible_text))
    career_lower = career_text.lower()

    missing = []
    for tech in yaml_techs:
        search_term = tech.strip()
        if search_term not in career_lower:
            missing.append(tech)

    if missing:
        return {"status": "FAIL", "details": f"Skills not found in career.md (visible content): {missing}"}
    return {"status": "PASS", "details": f"All {len(yaml_techs)} visible skills verified"}


def check_year_arithmetic(data: dict, career_text: str) -> dict:
    """Validate year claims in summary against career.md date ranges."""
    summary = data.get("summary", "")
    if not summary:
        return {"status": "PASS", "details": "No summary to check"}

    # Find year claims like "4+ years" or "5 years"
    year_claims = re.findall(r"(\d+)\+?\s*years?", summary, re.IGNORECASE)
    experience_years = _parse_years(career_text)

    if not year_claims or not experience_years:
        return {"status": "PASS", "details": "No year claims or no parseable dates"}

    max_years = max(experience_years.values()) if experience_years else 0
    issues = []
    for claim in year_claims:
        claimed = int(claim)
        if claimed > max_years:
            issues.append(
                f"Claimed {claimed}+ years but max career range is {max_years:.1f} years"
            )

    if issues:
        return {"status": "FAIL", "details": "; ".join(issues)}
    return {"status": "PASS", "details": f"Year claims valid (max career range: {max_years:.1f}y)"}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_all_checks(yaml_path: str, career_path: str = "career.md") -> dict:
    """Run all validation checks and return structured report."""
    yaml_data = yaml.safe_load(Path(yaml_path).read_text(encoding="utf-8"))
    career_text = _load_career(Path(career_path))

    checks = {
        "schema_validation": check_schema(yaml_data),
        "banned_phrases": check_banned_phrases(yaml_data),
        "em_dashes": check_em_dashes(yaml_data),
        "passive_voice": check_passive_voice(yaml_data),
        "summary_length": check_summary_length(yaml_data),
        "skill_cross_reference": check_skills_against_career(yaml_data, career_text),
        "year_arithmetic": check_year_arithmetic(yaml_data, career_text),
    }

    overall_pass = all(c["status"] == "PASS" for c in checks.values())

    return {
        "yaml_file": yaml_path,
        "overall_pass": overall_pass,
        "checks": checks,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validate resume YAML")
    parser.add_argument("yaml_path", help="Path to the YAML file to validate")
    parser.add_argument(
        "--career", default="career.md", help="Path to career.md (default: career.md)"
    )
    args = parser.parse_args()

    result = run_all_checks(args.yaml_path, args.career)
    print(json.dumps(result, indent=2))

    sys.exit(0 if result["overall_pass"] else 1)
