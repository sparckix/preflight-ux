# Preflight UX Specification

## Product thesis

Preflight UX is a calibrated pre-ship critique system. It helps teams find
predictable UX risks before launch by running structured persona panels against
the same product surface, normalizing the findings into issue classes, and
measuring those predictions against real outcomes.

The product is not "AI user research." It is closer to an early warning system:
cheap enough to run on every meaningful product change, explicit about its
blind spots, and calibrated over time.

## User jobs

### Product builder

As a product builder, I want a fast pre-ship critique that tells me what a real
user is likely to misunderstand, mistrust, abandon, or fail to use, so I can fix
high-leverage issues before launch.

### Researcher

As a researcher, I want persona predictions to be traceable, scored, and
comparable against known outcomes, so I can distinguish useful simulation from
plausible fiction.

### Maintainer

As a maintainer, I want every persona, issue class, benchmark entry, and report
to follow a stable schema, so the toolkit can improve without drifting into
free-form prompting.

## Core concepts

### Product surface

The artifact being reviewed. It may be a URL, screenshot set, prototype, PR,
written spec, or captured flow. The same surface must be provided to every
persona in a run.

### Persona

A structured review lens. Personas can be UX experts or user types. Each persona
has a bounded contract:

- what it expects
- what it reliably surfaces
- what it tends to miss
- what evidence it should use
- how it has performed in benchmark runs

### Issue class

A canonical failure type, stored in `taxonomy/issue-classes.yaml`. Findings
must map to issue classes before scoring.

### Benchmark product

A product or product surface with documented post-launch UX issues. Benchmark
entries must include citations and enough launch-surface detail that a panel can
be run without exposing the known issues.

### Web preflight app

A deployable BYOK interface for product teams. The web app must build the same
structured packet as the CLI, disclose the request path, avoid server-side key
storage, and export local artifacts that can be checked into a product repo.

### Panel run

A set of persona predictions generated from one product surface under one run
configuration. A valid panel run records:

- product slug or surface ID
- model and model version
- prompt version
- date
- persona IDs
- input artifacts
- raw predictions
- normalized issue-class predictions

### Calibration matrix

The measured relationship between personas and issue classes. The target shape:

```text
persona_id x issue_class -> hit_rate, precision, severity_weighted_recall, false_positive_rate
```

### Baseline

A non-panel comparison run against the same surface. Early baselines should
include generic model critique and heuristic-evaluation prompting. Later
baselines may include browser agents, human heuristic review, and multi-model
consensus.

## Required report output

Every product-facing report should include:

1. executive summary
2. top risks
3. structured issue table
4. persona disagreements
5. recommended changes
6. confidence and uncertainty notes
7. validation plan
8. raw persona findings appendix

See `docs/REPORT_FORMAT.md`.

## Non-goals

- Replacing real user interviews
- Creating unvalidated personas for final decision-making
- Predicting product-market fit
- Simulating willingness to pay
- Producing synthetic interview quotes for stakeholder theater
- Claiming behavioral truth without real behavioral evidence

## Quality bar

A public claim is allowed only at the evidence level it has earned:

| Claim | Minimum evidence |
|---|---|
| "This persona often flags X" | repeated internal runs |
| "This persona reliably flags X" | benchmark score with acceptable precision |
| "The panel predicts real user issues" | post-launch validation |
| "This method outperforms baseline critique" | comparative study against human or LLM baselines |
| "This method is stronger than adjacent approaches" | replicated benchmark comparison with open artifacts |

## v0.2 acceptance criteria

The repo reaches v0.2 when it has:

- 5 benchmark products with cited known issues
- one complete scored benchmark run
- one generic critique baseline across the same benchmark surfaces
- populated issue-class taxonomy with owners and aliases
- report template used by at least one sibling product repo
- validator passing on all public artifacts

## v0.3 acceptance criteria

The repo reaches v0.3 when it has:

- 10-12 benchmark products
- per-persona calibration matrix
- severity-weighted panel scores
- false-positive analysis
- heuristic-evaluation baseline
- a minimal runner that emits normalized JSON and Markdown reports
- web import/export for review brief, run output, and repo-ready Markdown report
- schema validation shared by CLI and web flow

## v0.4 acceptance criteria

The repo reaches v0.4 when it has:

- live validation against at least one deployed product
- model-to-model consistency comparison
- documented cases where the panel was wrong
- public methodology note suitable for HCI/product-design review
