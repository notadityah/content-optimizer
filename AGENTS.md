# Content Optimizer

This is a toolkit for producing marketing and sales content for personal branding. This involves resumes (marketing), cover letters (sales), outreach messages (sales), and more.

## The career profile

The file `./career.md` (or alternatively at, `./canon.md` or `./identity.md`) contains the comprehensive career profile. This is the "universe of facts" or "a single source of truth" from which all content is derived. In addition to the typical resume content like bio, education, experiences, projects, and skills, it ALSO includes other details such as interests, passion, philosophy and writing style.

The career profile file is meant to be a lot more detailed than a resume. By design, any material you produce must be a curated selection from the career profile - depending on the opportunity.

## Resume Optimization Philosophy

Generate resumes that appear naturally written while being strategically optimized for both ATS systems and human recruiters. The recruiter should see a strong, well-rounded candidate whose background aligns with the role - not a document obviously tailored to match a job description.

### Selection & Impact Logic

- **Tag Prioritization:** Use the impact tags in `career.md` to match the job's core needs (e.g., prioritize `[Efficiency]` for automation-heavy roles or `[Scale]` for big data/infrastructure roles).
- **Project Relevance:** For Data Engineering or Backend roles, prioritize **BirdDex** and the **Pose Estimation REST API**. For Full-Stack or Web Development roles, prioritize **JobDetective** and **Project Demeter**. For AI/GenAI roles, prioritize **BirdDex**, **JobDetective**, and the **Pose Estimation REST API** - in that order. **JobDetective** is preferred over **Project Demeter** in all contexts due to its more complex, deliberate design (AI-assisted analysis pipeline, cloud deployment, analytics integration).
- **Education Placement:** For all 2026 applications, place the Monash University education entry above the Experience section to highlight the recent Australian qualification and immediate availability.
- **The "Monash Gap" Strategy:** Since the candidate just completed a Master of IT in late 2025, the AI must explicitly frame the 2024 - 2025 period as an intentional career pivot to the Australian market through higher education.
- **Citizenship:** If the application requires me to have permanent residency or be an australian citizen, just tell me and stop doing anything else.

## Repository Structure

```
./
├── career.md                      # Career profile - source of truth
├── opportunities/                 # Temporary YAML files (deleted after render)
│
├── cli/                           # Python CLI package
│   ├── schemas/
│   │   ├── resume.py              # ResumeSchema (Pydantic)
│   │   └── cover_letter.py        # CoverLetterSchema (Pydantic)
│   ├── app.py                     # CLI commands
│   └── core.py                    # Rendering & compilation logic
│
├── templates/
│   ├── resume/
│   │   ├── primary.tex.j2         # Default Jinja template
│   │   └── original/              # Reference LaTeX files
│   └── cover-letter/
│       ├── primary.tex.j2
│       └── original/
│
└── output/                        # Per-job output folders
    └── <job-name>/                # e.g. aws-data-engineer/
        ├── job-description.md     # Saved job description
        ├── resume.pdf             # Final resume
        └── cover-letter.pdf       # Final cover letter
```

## Content Types

The kinds of content you will be asked to generate falls into two buckets

### Structured (PDF Pipeline)

**Resume, Cover Letter** — requires precise formatting, strict schema.

The user will specify:

- Which opportunity file
- Generate both resume and cover letter
- Which template (defaults to primary)

Your job:

1. **Setup:** Create `./output/<job-name>/` folder. Save the job description as `./output/<job-name>/job-description.md`.
2. **Read:** `career.md` + opportunity + `./cli/schemas/<entity>.py` + `./templates/<entity>/<template>.tex.j2`
3. **Produce:** YAML matching the schema → save to `./opportunities/<name>.yaml`
4. **Render:** Run CLI command, outputting PDFs to the job folder.
5. **Validate (resume only):** Check that the resume PDF is exactly **one page**. If it exceeds one page, iterate by removing the least relevant content and re-rendering until it fits on a single page. Also check that all the points are validated with `career.md` if anything is exaggerated or lies, correct it.
6. **Clean up:** Delete the temporary YAML files from `./opportunities/` and `.tex` files from `./output/` after successful PDF generation.

```zsh
# Render YAML → PDF
uv run python -m cli render resume <yaml> [-t template] [-o output/<job-name>/resume.pdf]
uv run python -m cli render cover-letter <yaml> [-t template] [-o output/<job-name>/cover-letter.pdf]

# Re-compile after manual .tex edits
uv run python -m cli re-render <tex> [-o output.pdf]
```

Defaults:

- `-t` defaults to `primary`
- `-o` should always target `./output/<job-name>/`

### Freeform (Text/Markdown)

**Outreach emails, LinkedIn messages, application Q&A, anything else** — strategic content, simple output.

No schema, no CLI. Just produce well-crafted text derived from career.md.

## Writing Style

**Pronuciation:** Never use em dashes (—). Always use ' - ' (space-hyphen-space) instead.
**Voice:** Use strictly active voice (e.g., "Architected," "Engineered," "Spearheaded") instead of passive phrases like "Was responsible for".
**Localization:** Use Australian English spelling (e.g., "Optimisation", "Modelling", "Analysing") for prose, while maintaining standard US technical terminology (e.g., "SQL Optimization").
**Hierarchy:** Prioritize points from highest impact to lowest impact. When trimming for space, remove the lowest impact "Additional Projects" first.
