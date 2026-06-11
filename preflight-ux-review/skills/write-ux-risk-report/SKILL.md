---
name: write-ux-risk-report
description: "Use when turning UX risk findings into an action-oriented report for a product team. Produces prioritized risks, recommendations, uncertainty notes, and validation plans."
---

# Write UX Risk Report

Use this skill to turn findings into a report a product team can act on.

## Repo-Backed Mode

If the current workspace is a Preflight UX checkout, or `PREFLIGHT_UX_REPO`
points to one, prefer generated repo artifacts:

- Confirm the checkout with bundled script
  `python3 scripts/preflight_ux.py locate`.
- Validate structure with `python3 scripts/preflight_ux.py validate`.
- Generate a report with
  `python3 scripts/preflight_ux.py uxpanel report --run <run.json> --out <report.md>`
  when a normalized run exists.
- Use `docs/REPORT_FORMAT.md` and `framework/scoring.md` for report structure
  and calibration language.
- If a score file exists, include hits, misses, false positives, and
  severity-weighted recall.

If no checkout is available, write the report manually in the format below and
state that repo validation/report generation was not run.

## Required Sections

1. Summary
2. Top risks
3. Structured findings
4. Meaningful disagreements or tradeoffs
5. Recommended changes
6. Confidence and uncertainty
7. Validation plan

## Top-Risk Table

| Priority | Issue class | Severity | Confidence | Recommended action |
|---|---|---|---|---|

Priority guidance:

- P0: likely abandonment, trust collapse, blocked core flow, or inaccessible core path
- P1: material comprehension, conversion, recovery, or repeat-use risk
- P2: polish, secondary workflow, or lower-confidence issue

## Structured Finding Shape

For each finding include:

- Issue class
- Risk hypothesis
- Evidence from the supplied surface
- Severity
- Confidence
- Recommendation
- Validation needed

## Rules

- Keep the report concrete and implementation-facing.
- Do not present simulated findings as user research.
- Include uncertainty where the surface evidence is incomplete.
- Include at least one validation path for each P0/P1 risk.
- If findings are benchmark-scored, include hits, misses, and false positives.
