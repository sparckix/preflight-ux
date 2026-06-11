---
name: catch-ux-risks
description: "Use when reviewing a product surface, spec, screenshot, prototype, PR, or launch flow to catch UX risks before launch. Produces structured product-risk hypotheses, not user research claims."
---

# Catch UX Risks

Use this skill to review a product surface before launch.

The output is a product-risk artifact, not validated user research. Do not
invent user quotes, survey findings, or behavioral certainty.

## Inputs To Request Or Use

- Product surface: URL, screenshot, PR, prototype, spec, or flow description
- Target audience or primary user job
- Launch context or product stage
- Known constraints, if supplied

If the surface is thin, state the evidence limitation and keep confidence lower.

## Repo-Backed Mode

If the current workspace is a Preflight UX checkout, or `PREFLIGHT_UX_REPO`
points to one, prefer the repository artifacts over freeform review:

- Confirm the checkout with bundled script
  `python3 scripts/preflight_ux.py locate`.
- Validate repo structure with
  `python3 scripts/preflight_ux.py validate` when the task depends on repo
  artifacts.
- Use `panels/default.yaml` or a supplied panel file for review lenses.
- Use `taxonomy/issue-classes.yaml` for issue-class names.
- Use `schemas/report-finding.schema.json` for normalized finding shape.
- If the surface is already saved as Markdown, scaffold a run with
  `python3 scripts/preflight_ux.py uxpanel run --surface <surface.md> --surface-type spec --panel panels/default.yaml --run-id <slug>`.
- If the user wants a benchmark comparison rather than a product review,
  switch to the `calibrate-ux-findings` skill after findings are produced.

If no checkout is available, still perform the review using the structure below
and mention that repo validation was not run.

## Review Lenses

Look for concrete risks in these classes:

- comprehension: users cannot tell what to do, what changed, or why it matters
- trust: output, source, policy, data, or provenance is not credible enough
- workflow: the main task is blocked, slowed, hidden, or made harder
- recovery: errors, empty states, loading, fallback, or support paths are weak
- inclusion: users with higher support needs or fewer options are disadvantaged
- operator fit: density, shortcuts, navigation, or repeated-use flows are mismatched
- change regression: a redesign removes expected behavior or familiar structure

## Output Format

Return 5-10 findings as a table:

| Priority | Issue class | Risk hypothesis | Surface evidence | Recommendation | Confidence |
|---|---|---|---|---|---|

Then add:

- **Likely misses:** what this review may not catch
- **Validation plan:** how to test the highest-risk findings with real evidence
- **False-positive watch:** which findings are most likely to be over-predictions

## Rules

- Tie every finding to supplied surface evidence.
- Prefer specific task blockers over generic UX advice.
- Separate severity from confidence.
- Mark unsupported but plausible concerns as low confidence or omit them.
- Never claim the output proves real user behavior.
