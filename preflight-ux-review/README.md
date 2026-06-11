# Preflight UX Review Plugin

Installable skills for structured UX risk review.

Skills:

- `catch-ux-risks`
- `calibrate-ux-findings`
- `write-ux-risk-report`

These skills are a distribution layer for the main Preflight UX method. They do
not replace the benchmark, CLI, schemas, or scoring artifacts in the repository.

The bundled `scripts/preflight_ux.py` helper locates a Preflight UX checkout via
the current workspace or `PREFLIGHT_UX_REPO`, then delegates to `python -m
uxpanel`.
