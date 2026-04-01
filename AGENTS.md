# Content Optimizer

This is a toolkit for producing marketing and sales content for personal branding. This involves resumes (marketing), cover letters (sales), outreach messages (sales), and more.

## The career profile

The file `./career.md` (or alternatively at, `./canon.md` or `./identity.md`) contains the comprehensive career profile. This is the "universe of facts" or "a single source of truth" from which all content is derived. In addition to the typical resume content like bio, education, experiences, projects, and skills, it ALSO includes other details such as interests, passion, philosophy and writing style.

The career profile file is meant to be a lot more detailed than a resume. By design, any material you produce must be a curated selection from the career profile - depending on the opportunity.

## Resume Optimization Philosophy

Generate resumes that appear naturally written while being strategically optimized for both ATS systems and human recruiters. The recruiter should see a strong, well-rounded candidate whose background aligns with the role - not a document obviously tailored to match a job description.

### Summary Rules (strictly enforced)

The summary is a strict distillation of `career.md`. It is not a pitch. It is not an interpretation. It is not aspirational. Every word must come directly from what is written in `career.md` - nothing else.

- **Only use what is in `career.md`.** If a claim, skill, technology, or trait is not explicitly stated in `career.md`, it does not appear in the summary. Not even if it's implied. Not even if it would help the application. Not even if the job description asks for it.
- **No inflating years.** Use only the exact years of experience that can be counted from the entries in `career.md`. Do not round up, do not combine loosely related roles, do not estimate.
- **No borrowing from the JD.** Do not mirror the job description's language back as if it describes you. Skills and keywords that appear in the JD but not in `career.md` are off-limits.
- **No filler phrases.** "Proven track record", "passionate about", "deep expertise", "extensive experience", "strong background in", "results-driven" - all banned. State the fact, not the spin.
- **2-4 sentences, no more.** Lead with role + years of experience. Follow with 1-2 specific, verifiable strengths from `career.md`. Stop there.

### Selection & Impact Logic

- **Tag Prioritization:** Use the impact tags in `career.md` to match the job's core needs (e.g., prioritize `[Efficiency]` for automation-heavy roles or `[Scale]` for big data/infrastructure roles).
- **Project Relevance:** For Data Engineering or Backend roles, prioritize **BirdDex** and the **Pose Estimation REST API**. For Full-Stack or Web Development roles, prioritize **JobDetective** and **Project Demeter**. For AI/GenAI roles, prioritize **BirdDex**, **JobDetective**, and the **Pose Estimation REST API** - in that order. **JobDetective** is preferred over **Project Demeter** in all contexts due to its more complex, deliberate design (AI-assisted analysis pipeline, cloud deployment, analytics integration).
- **Education Placement:** For all 2026 applications, place the Monash University education entry above the Experience section to highlight the recent Australian qualification and immediate availability.
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

7. **Log to Notion:** After a successful resume generation, create an entry in the Job Applications Notion database.
   - Notion data source ID: `collection://05b8f656-6192-4eb2-aadb-52931bd380a4`
   - Properties to set:
     - `Company`: extracted from the job description
     - `Role`: the job title
     - `Status`: `"Prepared"` — NOT "Applied". The user applies manually; do not assume they have applied.
     - `Resume Version`: `file:///Users/hariharan.aditya/Documents/Claude/content-optimizer/output/<job-name>/<resume-filename>.pdf`
     - `Job Description`: `file:///Users/hariharan.aditya/Documents/Claude/content-optimizer/output/<job-name>/job-description.md`
   - Do NOT set `Date Applied` or `Gmail Thread ID` at this stage — those are only set when the user confirms they have applied (see "Mark as Applied" below).
   - If the application requires Australian citizenship or permanent residency and the user is not eligible, skip this step and notify the user instead (as per the Citizenship rule above).

8. **Mark as Applied (separate step):** When the user says something like "I applied to [Company]" or "mark [Company] as applied":
   - Search the Notion database for the matching row by Company name.
   - Update the row:
     - `Status`: `"Applied"`
     - `date:Date Applied:start`: today's date in ISO format (e.g. `2026-04-01`)
   - Search Gmail for a confirmation email using `gmail_search_messages` with query: `from:(*@<company-domain>) subject:(application OR received OR thank)` scoped to the last 3 days.
     - If a confirmation email is found, update `Gmail Thread ID` with the `threadId`.
     - If no confirmation is found, leave `Gmail Thread ID` blank — the daily task will try again next run.

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
