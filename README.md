# Preflight UX

Preflight UX is an open toolkit for pre-ship UX risk review. It runs structured
persona panels against the same product surface, normalizes findings into a
shared issue taxonomy, and keeps the raw evidence needed to score predictions
against known product outcomes.

The project is designed for teams that want faster early critique without
confusing model output for user research. A panel finding is a product-risk
hypothesis until it is validated by benchmark scoring, user observation,
telemetry, support data, or another real-world signal.

## What It Contains

- A persona library for expert and user-type review lenses.
- An issue taxonomy for common pre-ship UX risks.
- Benchmark scaffolds for products with documented post-launch UX issues.
- JSON schemas for review briefs, panel runs, findings, benchmark metadata, and
  scores.
- A small Python CLI for validation, benchmark scaffolding, run scaffolding,
  scoring, and report generation.
- A deployable BYOK web UI for building review briefs, attaching screenshots,
  running a panel through a user-provided model key, and exporting repo-ready
  artifacts.

## Current Status

This repository is an early public scaffold. The method is intentionally
evidence-scoped:

- The schemas, taxonomy, prompts, CLI, web UI, and structural checks are usable.
- Seed benchmark entries are draft examples until their launch surfaces and
  scorer reviews are complete.
- Personas are not benchmark-validated yet.
- Reports should be treated as decision support, not as validated user research.

The next credibility step is to promote benchmark entries from draft to ready,
run panels against them, and publish hits, misses, false positives, and
persona-by-issue-class calibration notes.

## Positioning

Preflight UX is adjacent to browser-agent usability testing, synthetic heuristic
evaluation, persona-conditioned UI/UX evaluation, and LLM simulation benchmarks.
It does not claim that LLM personas are new.

The project focuses on a different layer: an open, repo-native calibration loop
for deciding when synthetic UX critique is useful. The intended contribution is
the combination of shared issue classes, benchmark surfaces, normalized
predictions, scored misses and false positives, persona reliability notes, and
product-ready exports.

The open-source posture is part of the method. Prompts, schemas, taxonomy,
benchmark entries, redacted execution receipts, score files, and report
templates should be inspectable enough that contributors can challenge scoring
decisions and improve the calibration loop. Public run folders keep normalized
findings and redacted execution receipts; raw model transcripts are archived
outside the public artifact surface.

See `docs/POSITIONING.md` and `docs/EVALUATION_PROTOCOL.md`.

## Quick Start

Validate the repository:

```bash
python3 tools/validate_repo.py
python3 -m uxpanel validate
```

Create a benchmark entry:

```bash
python3 -m uxpanel new-benchmark example-product-2026
```

Inspect benchmark readiness and scored runs:

```bash
python3 -m uxpanel benchmark-status
```

Create a run scaffold:

```bash
python3 -m uxpanel run \
  --surface benchmark/products/example-product-2026/surface.md \
  --surface-type benchmark \
  --panel panels/default.yaml \
  --run-id example-product-2026-seed
```

Create a baseline scaffold for comparison:

```bash
python3 -m uxpanel baseline \
  --surface benchmark/products/example-product-2026/surface.md \
  --surface-type benchmark \
  --kind generic-critique \
  --run-id example-product-2026-generic-baseline
```

Generate a Markdown report from a run:

```bash
python3 -m uxpanel report \
  --run runs/example-product-2026-seed/run.json \
  --out reports/example-product-2026-seed.md
```

Score a run against known issues:

```bash
python3 -m uxpanel score \
  --run runs/example-product-2026-seed/run.json \
  --benchmark benchmark/products/example-product-2026 \
  --out calibration/example-product-2026-seed.score.json
```

Baseline runs use the same `run.json`, report, and score paths as panel runs.
Use them to compare the default panel against generic model critique or
heuristic-evaluation prompting on the same benchmark surface.

Compare score files:

```bash
python3 -m uxpanel compare-scores \
  calibration/example-product-2026-seed.score.json \
  calibration/example-product-2026-generic-baseline.score.json
```

Run a baseline artifact through subscription runtimes first, with API fallback,
and write normalized findings back to `run.json`:

```bash
python3 tools/run_baseline_agent.py \
  --run runs/example-product-2026-generic-baseline
```

Default runtime order is `codex,claude,anthropic,openai,gemini`. Subscription
CLIs are tried before API providers.

Run a panel artifact through the same subscription-first transport stack:

```bash
python3 -m uxpanel run \
  --surface benchmark/products/govuk-verify-2016/surface.md \
  --panel panels/public-service-access.yaml \
  --out runs/govuk-verify-2016-public-service-panel-v0-3 \
  --run-id govuk-verify-2016-public-service-panel-v0-3

python3 tools/run_panel_agent.py \
  --run runs/govuk-verify-2016-public-service-panel-v0-3
```

`tools/run_panel_agent.py` writes redacted runtime receipts and normalized
findings for each persona.

## Web UI

The web UI lives in `web/` with a serverless panel endpoint in `api/panel.js`.
It supports a strict bring-your-own-key flow:

- The user explicitly enables BYOK before running a panel.
- Provider keys are stored only in the user's browser localStorage.
- Keys and selected screenshots are sent to `/api/panel` only when the user
  clicks `Run panel`.
- The serverless function forwards the request to the selected provider and does
  not persist keys or screenshots.
- Generated output can be exported as `run.json`, review-brief JSON, raw
  Markdown, and a repo-ready report.

Supported provider adapters:

- Anthropic
- OpenAI
- Google Gemini

Run static and logic checks:

```bash
node tests/simulate_web_static.mjs
node tests/simulate_web_logic.mjs
node tests/simulate_byok_api.mjs
```

## Repository Map

```text
api/                 Serverless BYOK panel endpoint
benchmark/           Benchmark schema, templates, and draft seed entries
calibration/         Scores, misses, false positives, and persona matrices
docs/                Method, report, benchmark, and UI documentation
framework/           Scoring methodology
panels/              Persona panel definitions
personas/            Expert and user-type persona files
prompts/             Versioned prompts
reports/             Generated report examples
runs/                Panel run artifacts
schemas/             JSON schemas
taxonomy/            Canonical issue classes
tests/               Local simulation and regression checks
tools/               Structural validator
uxpanel/             Python CLI package
web/                 Browser UI
```

## Method Boundary

Preflight UX is meant to help teams ask better pre-ship questions:

- What will users misunderstand?
- Where might trust collapse?
- Which workflow is likely to be abandoned?
- Which issues recur across personas?
- Which predictions survive benchmark scoring?

It is not meant to replace usability testing, interviews, accessibility audits,
analytics, support analysis, or domain research. Real users outrank synthetic
predictions.

## Contributing

Contributions are most useful when they make the method more auditable:

- benchmark entries with cited post-launch issues
- launch-surface reconstructions
- issue-class improvements
- scored runs
- false-positive and miss analysis
- schema and validation improvements
- report-format improvements

See `CONTRIBUTING.md` for contribution rules and review expectations.

## Security And Data

Do not commit private user data, customer material, proprietary screenshots,
interview transcripts, analytics exports, support tickets, secrets, or
unreleased product details. See `SECURITY.md` for reporting and handling
guidance.

## License

MIT. See `LICENSE`.
