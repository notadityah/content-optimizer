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
    8. No ATS keyword payload
    9. No adjacent / JD-only tools in visible content
    10. Recruiter positioning checks
    11. Verified JD keyword opportunity scan
    12. Metric drift detection
    13. Bullet reuse warning
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
    r"Docker|Kubernetes|FastAPI|Postman|ONNX|YOLO|TensorFlow|Locust|PostGIS|GTFS|"
    r"Hono|Vite|Tailwind|PrimeVue|SendGrid|Resend|Tableau|NewsAPI|"
    r"SAP\s*BW|HANA|S/4HANA|MATLAB|Simulink|"
    r"Git|Agile|DevOps|REST|API|HTTP|OAuth|"
    r"BeautifulSoup|Foursquare|cvxopt|MPPT)\b",
    re.IGNORECASE,
)

ADJACENT_TOOL_TERMS = [
    "Airflow",
    "Ansible",
    "Azure",
    "BigQuery",
    "Databricks",
    "dbt",
    "GCP",
    "Google Cloud",
    "GraphQL",
    "Kafka",
    "LangChain",
    "LangGraph",
    "LlamaIndex",
    "Looker",
    "Power BI",
    "PowerBI",
    "Pulumi",
    "RabbitMQ",
    "Redshift",
    "Snowflake",
    "Spark",
    "Spring",
    "Spring Boot",
    "Terraform",
]

ROLE_FAMILIES = {
    "data": [
        "data engineer",
        "etl",
        "data platform",
        "analytics engineer",
        "data analyst",
        "business intelligence",
    ],
    "software": [
        "software engineer",
        "backend",
        "full-stack",
        "full stack",
        "developer",
        "frontend",
        "platform engineer",
    ],
    "ai": [
        "ai engineer",
        "ml engineer",
        "machine learning",
        "genai",
        "computer vision",
        "data scientist",
    ],
}

STRENGTHENING_KEYWORDS = [
    "ABAP",
    "Agile",
    "API",
    "AWS",
    "AWS CDK",
    "CloudFront",
    "Computer Vision",
    "Confluence",
    "data modelling",
    "data quality",
    "data validation",
    "data warehouse",
    "Docker",
    "ETL",
    "FastAPI",
    "Git",
    "HANA",
    "HANA Calculation Views",
    "incident",
    "Jira",
    "Kubernetes",
    "Lambda",
    "Machine Learning",
    "MySQL",
    "ONNX Runtime",
    "PostGIS",
    "Postman",
    "PostgreSQL",
    "Python",
    "REST",
    "REST API",
    "S3",
    "SAP BW on HANA",
    "ServiceNow",
    "SQL",
    "stakeholder",
    "Tableau",
    "technical risk",
    "testing",
    "TypeScript",
    "Vue 3",
    "YOLO",
]

NUMERIC_CLAIM_PATTERN = re.compile(
    r"\b\d+(?:\.\d+)?\+?(?:\s*(?:hours/month|registered users|species|engineers|workstreams|pipelines|discrepancies|users|months|years|GPA|WAM|%))?",
    re.IGNORECASE,
)

REUSE_WARNING_THRESHOLD = 12


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
    """Extract all text from YAML but exclude the deprecated ats_optimization field."""
    texts: list[str] = []
    if isinstance(data, dict):
        for k, v in data.items():
            if k == "ats_optimization":
                continue
            texts.extend(_extract_all_text_excluding_ats(v))
    elif isinstance(data, str):
        texts.append(data)
    elif isinstance(data, list):
        for item in data:
            texts.extend(_extract_all_text_excluding_ats(item))
    return texts


def _visible_text(data: dict) -> str:
    """Return text a recruiter can see in resume sections."""
    visible_sections = {
        "summary": data.get("summary"),
        "education": data.get("education"),
        "experience": data.get("experience"),
        "projects": data.get("projects"),
        "skills": data.get("skills"),
        "certifications": data.get("certifications"),
    }
    return " ".join(_extract_all_text(visible_sections))


def _has_term(text: str, term: str) -> bool:
    return re.search(r"\b" + re.escape(term) + r"\b", text, re.IGNORECASE) is not None


def _term_in_text(text: str, term: str) -> bool:
    """Case-insensitive term match with light handling for slash/space variants."""
    if _has_term(text, term):
        return True
    if "/" in term:
        spaced = term.replace("/", " ")
        if _has_term(text, spaced):
            return True
    return False


def _normalise_for_reuse(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _numeric_token_in_text(token: str, text: str) -> bool:
    escaped = re.escape(token.lower())
    return re.search(rf"(?<![\d.]){escaped}(?![\d.])", text.lower()) is not None


def _infer_role_family(data: dict, yaml_path: str | None = None, jd_text: str | None = None) -> str:
    haystack_parts = [
        yaml_path or "",
        (data.get("meta") or {}).get("subject") or "",
        (data.get("meta") or {}).get("keywords") or "",
        jd_text or "",
    ]
    haystack = " ".join(haystack_parts).lower()
    for family, signals in ROLE_FAMILIES.items():
        if any(signal in haystack for signal in signals):
            return family
    return "unknown"


def check_skills_against_career(data: dict, career_text: str) -> dict:
    """Verify every mentioned technology in VISIBLE content exists in career.md.

    Note: ats_optimization is excluded here because it has its own hard-fail
    check. It should not be populated.
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


def check_no_ats_keyword_payload(data: dict) -> dict:
    """Fail resumes that still carry a standalone ATS keyword stuffing field."""
    basics = data.get("basics") or {}
    payload = (basics.get("ats_optimization") or "").strip()
    if payload:
        return {
            "status": "FAIL",
            "details": "basics.ats_optimization is populated. Move role-relevant verified terms into skills/bullets and leave this field empty.",
        }
    return {"status": "PASS", "details": "No ATS keyword payload present"}


def check_adjacent_tools_absent(data: dict, career_text: str, jd_text: str | None = None) -> dict:
    """Block adjacent / JD-only tools from recruiter-visible content."""
    visible = _visible_text(data)
    career_lower = career_text.lower()
    jd_lower = (jd_text or "").lower()
    found = []

    for term in ADJACENT_TOOL_TERMS:
        in_visible = _has_term(visible, term)
        in_career = term.lower() in career_lower
        in_jd = term.lower() in jd_lower if jd_text else True
        if in_visible and not in_career and in_jd:
            found.append(term)

    if found:
        return {
            "status": "FAIL",
            "details": f"Adjacent or JD-only tools in visible content: {sorted(set(found))}. Use skills-map.md concepts and name only verified tools.",
        }
    return {"status": "PASS", "details": "No adjacent/JD-only tools in visible content"}


def check_role_specific_positioning(data: dict, yaml_path: str | None = None, jd_text: str | None = None) -> dict:
    """Check that projects and first experience bullets tell the right story."""
    family = _infer_role_family(data, yaml_path, jd_text)
    projects = [p.get("name", "") for p in data.get("projects") or []]
    project_text = " | ".join(projects)
    exp_bullets = []
    for exp in data.get("experience") or []:
        exp_bullets.extend(exp.get("bullets") or [])
    first_three = " ".join(exp_bullets[:3])

    issues = []
    if family == "data":
        if "15+" not in first_three or "etl" not in first_three.lower():
            issues.append("data roles should lead experience with 15+ ETL pipeline scope")
        if not any(token.lower() in first_three.lower() for token in ["SQL", "HANA", "SAP BW", "data"]):
            issues.append("data roles should surface SQL, HANA, SAP BW, or data quality work in the first experience bullets")
        if "BirdDex" not in project_text or "Pose Estimation" not in project_text:
            issues.append("data/backend roles should prioritise BirdDex and Pose Estimation REST API projects")
    elif family == "software":
        required_any = [
            "AWS",
            "REST",
            "API",
            "backend",
            "full-stack",
            "serverless",
            "production",
            "release",
            "technical risk",
            "Agile",
            "DevOps",
            "testing",
        ]
        if not any(token.lower() in first_three.lower() for token in required_any):
            issues.append("software roles should surface backend/cloud/API delivery in the first experience bullets")
        if projects and projects[0] not in {"JobDetective", "BirdDex"}:
            issues.append("software roles should lead projects with JobDetective or BirdDex")
    elif family == "ai":
        expected = ["BirdDex", "JobDetective", "Pose Estimation"]
        missing = [name for name in expected[:2] if name not in project_text]
        if missing:
            issues.append(f"AI/ML roles should prioritise {', '.join(expected)}; missing {', '.join(missing)}")

    if issues:
        return {"status": "FAIL", "details": "; ".join(issues)}
    return {"status": "PASS", "details": f"Role-specific positioning OK ({family})"}


def check_hireability_metrics(data: dict) -> dict:
    """Ensure the first experience bullets show scope, ownership, and impact quickly."""
    exp_bullets = []
    for exp in data.get("experience") or []:
        exp_bullets.extend(exp.get("bullets") or [])
    first_three = " ".join(exp_bullets[:3])
    metric_signals = ["15+", "8+", "50+", "40 hours/month"]
    ownership_signals = ["Led", "Partnered", "owned", "ownership", "stakeholder", "release"]

    metrics_hit = [signal for signal in metric_signals if signal.lower() in first_three.lower()]
    ownership_hit = [signal for signal in ownership_signals if signal.lower() in first_three.lower()]

    if len(metrics_hit) < 2:
        return {
            "status": "FAIL",
            "details": f"First three experience bullets include only {metrics_hit or 'no'} core impact metrics. Lead with at least two of 15+, 8+, 50+, 40 hours/month.",
        }
    if not ownership_hit:
        return {
            "status": "FAIL",
            "details": "First three experience bullets do not show ownership/stakeholder/release responsibility.",
        }
    return {
        "status": "PASS",
        "details": f"First three experience bullets show impact ({metrics_hit}) and ownership ({ownership_hit[:2]})",
    }


def check_verified_jd_keyword_opportunities(data: dict, career_text: str, jd_text: str | None = None) -> dict:
    """Report JD keywords that are verified by career.md but missing from the resume.

    This is deliberately advisory. A one-page resume should not stuff every
    possible keyword, but the generator should consider adding high-value
    verified terms through real bullets, skills, projects, or metadata.
    """
    if not jd_text:
        return {"status": "PASS", "details": "No JD supplied; keyword opportunity scan skipped"}

    visible = _visible_text(data)
    career_lower = career_text.lower()

    verified_terms = []
    for term in STRENGTHENING_KEYWORDS:
        if not _term_in_text(jd_text, term):
            continue
        if term.lower() not in career_lower:
            continue
        if any(_term_in_text(term, adjacent) for adjacent in ADJACENT_TOOL_TERMS):
            continue
        verified_terms.append(term)

    present = [term for term in verified_terms if _term_in_text(visible, term)]
    missing = [term for term in verified_terms if term not in present]

    if missing:
        return {
            "status": "PASS",
            "details": (
                "Verified JD keywords missing from visible resume; consider adding the strongest ones "
                f"through career.md-backed bullets/skills/meta: {missing[:8]}"
            ),
            "present_verified_keywords": present,
            "missing_verified_keywords": missing,
        }
    return {
        "status": "PASS",
        "details": f"All {len(verified_terms)} verified JD keyword opportunities are represented",
        "present_verified_keywords": present,
        "missing_verified_keywords": [],
    }


def check_numeric_claims_against_career(data: dict, career_text: str) -> dict:
    """Fail rewritten bullets that introduce unsupported numeric claims."""
    visible = _visible_text(data)
    career_lower = career_text.lower()
    claims = sorted(set(m.group(0).strip() for m in NUMERIC_CLAIM_PATTERN.finditer(visible)))
    unsupported = []

    for claim in claims:
        # Plain "3" should not fail when it is part of "3.063" in career.md,
        # so compare the exact extracted token first, then its bare number.
        claim_lower = claim.lower()
        if _numeric_token_in_text(claim_lower, career_lower):
            continue
        bare = re.match(r"\d+(?:\.\d+)?\+?", claim)
        if bare and _numeric_token_in_text(bare.group(0).lower(), career_lower):
            continue
        unsupported.append(claim)

    if unsupported:
        return {
            "status": "FAIL",
            "details": f"Numeric claims not found in career.md: {unsupported}. Revert to exact career-backed metrics.",
        }
    return {"status": "PASS", "details": f"All {len(claims)} numeric claims are career-backed"}


def check_bullet_reuse_warning(data: dict, applied_root: str = "applied") -> dict:
    """Warn when current bullets are highly reused across past applied resumes."""
    bullets = [b for b in _extract_bullets(data) if len(b) >= 80]
    if not bullets:
        return {"status": "PASS", "details": "No long bullets to compare for reuse"}

    root = Path(applied_root)
    if not root.exists():
        return {"status": "PASS", "details": "No applied archive found; bullet reuse warning skipped"}

    try:
        from pypdf import PdfReader
    except Exception as exc:
        return {"status": "PASS", "details": f"pypdf unavailable; bullet reuse warning skipped ({exc})"}

    archive_texts = []
    for pdf in root.glob("*/*.pdf"):
        if "cover" in pdf.name.lower():
            continue
        try:
            text = " ".join(page.extract_text() or "" for page in PdfReader(str(pdf)).pages)
        except Exception:
            continue
        archive_texts.append(_normalise_for_reuse(text))

    repeated = []
    for bullet in bullets:
        needle = _normalise_for_reuse(bullet)[:120]
        if len(needle) < 60:
            continue
        count = sum(1 for text in archive_texts if needle in text)
        if count >= REUSE_WARNING_THRESHOLD:
            repeated.append({"bullet_start": bullet[:110], "resume_count": count})

    if repeated:
        return {
            "status": "PASS",
            "details": "Warning: some bullets are heavily reused across applied resumes; consider career-backed rewriting for variety.",
            "reused_bullets": repeated[:5],
        }
    return {"status": "PASS", "details": "No heavily reused bullets detected"}


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

def run_all_checks(yaml_path: str, career_path: str = "career.md", jd_path: str | None = None) -> dict:
    """Run all validation checks and return structured report."""
    yaml_data = yaml.safe_load(Path(yaml_path).read_text(encoding="utf-8"))
    career_text = _load_career(Path(career_path))
    jd_text = Path(jd_path).read_text(encoding="utf-8") if jd_path else None

    checks = {
        "schema_validation": check_schema(yaml_data),
        "banned_phrases": check_banned_phrases(yaml_data),
        "em_dashes": check_em_dashes(yaml_data),
        "passive_voice": check_passive_voice(yaml_data),
        "summary_length": check_summary_length(yaml_data),
        "skill_cross_reference": check_skills_against_career(yaml_data, career_text),
        "year_arithmetic": check_year_arithmetic(yaml_data, career_text),
        "no_ats_keyword_payload": check_no_ats_keyword_payload(yaml_data),
        "adjacent_tools_absent": check_adjacent_tools_absent(yaml_data, career_text, jd_text),
        "role_specific_positioning": check_role_specific_positioning(yaml_data, yaml_path, jd_text),
        "hireability_metrics": check_hireability_metrics(yaml_data),
        "verified_jd_keyword_opportunities": check_verified_jd_keyword_opportunities(yaml_data, career_text, jd_text),
        "numeric_claims_against_career": check_numeric_claims_against_career(yaml_data, career_text),
        "bullet_reuse_warning": check_bullet_reuse_warning(yaml_data),
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
    parser.add_argument(
        "--jd", default=None, help="Optional job description path for JD-only tool checks"
    )
    args = parser.parse_args()

    result = run_all_checks(args.yaml_path, args.career, args.jd)
    print(json.dumps(result, indent=2))

    sys.exit(0 if result["overall_pass"] else 1)
