# Roadmap

This roadmap turns the current scaffold into a calibrated pre-ship UX risk
toolkit.

## Direction

Preflight UX should answer four questions:

1. Which issue classes can synthetic panels catch?
2. Which personas catch which classes?
3. How noisy are those personas?
4. Does the method improve shipped products before real users encounter the
   issues?

## Phase 0: Public Surface

Status: active for v0.1.

- clean README
- public spec
- public roadmap
- contribution guide
- literature review
- benchmark template
- issue taxonomy
- structural validator
- deployable BYOK web UI

Exit criteria:

- a new contributor can understand the method in 10 minutes
- a product repo can consume the report format without custom interpretation
- every public claim is scoped to the evidence available
- local checks and CI cover the public artifact path

## Phase 1: Benchmark Foundation

Goal: create enough ground truth to calibrate the first persona set.

Status: five draft seed entries added; scorer reconciliation and launch-surface
evidence still needed.

Deliverables:

- 5 benchmark products
- 6-10 issue classes with strong definitions
- source-quality rubric
- first scored benchmark run
- false-positive log
- generic LLM critique baseline for each ready benchmark

Product guidance:

- prefer narrow, interface-level failures over broad business failures
- include screenshots or faithful launch-surface descriptions
- require at least two independent sources for severe issues when possible
- avoid benchmark entries where the "UX issue" is mostly pricing, strategy,
  distribution, or market timing

## Phase 2: Calibration

Goal: turn personas into measured sensors.

Deliverables:

- persona by issue-class calibration matrix
- per-persona precision and recall
- severity-weighted panel score
- marginal contribution score for each persona
- abstention rules for noisy personas
- issue-ID scoring after issue-class scoring is stable
- heuristic-evaluation baseline for comparison

Key decision:

Remove or quarantine personas that are vivid but not reliable. More personas is
not progress unless they add measured marginal coverage.

## Phase 3: Runner, Web App, and Reports

Goal: make the toolkit operational for product repos.

Deliverables:

- CLI runner and report generator
- JSON schema for panel runs
- Markdown report generator
- prompt versioning
- model provenance logging
- deterministic validation of normalized findings
- browser review brief builder with BYOK model execution
- local JSON/Markdown export path from the web UI

Target command shape:

```bash
uxpanel run --surface ./surfaces/v1.md --panel panels/default.yaml --out runs/2026-05-12-applied-product
uxpanel score --benchmark benchmark/products/<slug> --run runs/<run-id>
uxpanel report --run runs/<run-id>
```

## Phase 4: Live Product Validation

Goal: test whether the method predicts real product friction.

Deliverables:

- pre-launch panel report for at least one live product
- shipped fixes linked to panel findings
- post-launch telemetry or research notes
- hit/miss/false-positive analysis
- public case study with uncertainty notes

## Phase 5: Research-Grade Evaluation

Goal: make the work publishable.

Deliverables:

- comparison against generic LLM critique
- comparison against human heuristic review where feasible
- comparison against heuristic-evaluation prompting
- multi-model consistency study
- issue-class reliability analysis
- public paper or technical report

## Current priorities

1. Harden the deployed BYOK web app around import, export, schema validation, and report generation.
2. Keep the local non-web Python/CLI simulation suite green as product features move.
3. Connect browser output to repo-native `run.json`, score, and Markdown report artifacts.
4. Promote benchmark entries from `draft` to `ready` after scorer review.
5. Add baseline runs for generic critique and heuristic-evaluation prompting.
6. Score predictions using `framework/scoring.md` and update persona calibration notes.
7. Delay research-paper work until the product loop is useful in real repos.

## Anti-roadmap

Do not spend time on:

- adding many new personas before benchmark pressure exists
- branding the toolkit as a startup before calibration exists
- synthetic interview transcript generation
- claims that panels replace user research
- marketing-site work before the product workflow is useful
