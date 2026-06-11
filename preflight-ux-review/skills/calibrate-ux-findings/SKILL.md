---
name: calibrate-ux-findings
description: "Use when comparing UX risk findings against known product failures, benchmark issues, support evidence, telemetry, or scorer notes. Tracks hits, misses, false positives, precision, recall, and calibration limits."
---

# Calibrate UX Findings

Use this skill when predictions need to be checked against known outcomes.

The goal is calibration: identify what the review caught, missed, and
over-predicted.

## Inputs To Use

- Predicted findings
- Known issues or post-launch evidence
- Issue taxonomy, if supplied
- Severity labels and scorer notes, if supplied

If known issues are weakly sourced, mark the calibration as provisional.

## Repo-Backed Mode

If the current workspace is a Preflight UX checkout, or `PREFLIGHT_UX_REPO`
points to one, prefer the repository scoring artifacts:

- Confirm the checkout with bundled script
  `python3 scripts/preflight_ux.py locate`.
- Validate structure with `python3 scripts/preflight_ux.py validate`.
- Score a run with
  `python3 scripts/preflight_ux.py uxpanel score --run <run.json> --benchmark <benchmark-dir> --out <score.json>`.
- Compare score files with
  `python3 scripts/preflight_ux.py uxpanel compare-scores <score-a.json> <score-b.json>`.
- Use `calibration/false_positives.md`, `calibration/misses.md`, and scorer
  notes when they exist.
- Keep class-level CLI scores separate from human-reviewed issue-level scoring.

If no checkout is available, calculate the calibration manually from the supplied
findings and known issues, and state that repo scoring was not run.

## Scoring Levels

Use **class-level scoring** when only issue categories are reliable.

Use **issue-level scoring** when each known issue is specific enough to match
one prediction to one documented failure.

## Output Format

Return:

| Known issue | Issue class | Match | Prediction | Rationale |
|---|---|---|---|---|

Then summarize:

- Hits
- Misses
- False positives
- Ambiguous matches
- Precision, recall, and F1 when calculable
- Severity-weighted recall when severities are known
- Calibration limits

## Rules

- Do not give credit for predictions that were not inferable from the supplied surface.
- Do not hide false positives behind aggregate coverage.
- Count unsupported plausible predictions as false positives unless a scorer marks them ambiguous.
- Keep preliminary class-level scores separate from reviewed issue-level scores.
- Recommend prompt, persona, or taxonomy changes only after explaining the scoring evidence.
