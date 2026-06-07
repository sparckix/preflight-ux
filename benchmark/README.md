# Benchmark

The benchmark is the core product asset. It turns synthetic UX critique from
plausible commentary into a measurable method.

Each benchmark entry contains a product surface as it appeared at launch and a
ground-truth set of documented post-launch UX issues. Personas are run against
the launch surface without seeing the known issues. Their predictions are then
normalized to issue classes and scored.

## Status

The current public benchmark set contains five draft product entries with cited
known issues. Scores are preliminary class-level checks until a human scorer
reviews hits, misses, and false positives.

## Directory layout

```text
benchmark/
  README.md
  products/
    _template/
      description.md
      surface.md
      known-issues.yaml
      meta.yaml
```

Copy `_template/` for each new product.

## Required files

### `description.md`

One paragraph explaining what the product did at launch, who it was for, and
which surface is being benchmarked.

Do not include known issues in this file.

### `surface.md`

A faithful reconstruction of the launch surface. Acceptable inputs:

- screenshots
- archived pages
- launch videos
- public demos
- written reconstructions with citations

The surface should contain enough detail that every persona reviews the same
artifact.

### `known-issues.yaml`

Ground truth issues, one record per issue:

```yaml
issues:
  - id: unique-slug
    class: empty-state-confusion
    description: "One-sentence issue description."
    severity: minor | moderate | severe
    surfaced_by: "first-time users"
    sources:
      - title: "Source title"
        url: "https://example.com/postmortem"
        date: "2026-01-01"
    notes: "Optional scorer notes."
```

### `meta.yaml`

Product and source metadata:

```yaml
slug: product-slug
product_name: "Product Name"
launch_date: "YYYY-MM-DD"
surface_version: "launch"
benchmark_status: draft | ready | scored
source_quality: low | medium | high
reviewer: "name"
notes: ""
```

## Source-quality rubric

Use `source_quality: high` when:

- the launch surface is well preserved
- known issues are documented by primary sources or multiple independent
  secondary sources
- the issue is specific enough to map to the taxonomy
- severity can be inferred from behavior, business impact, or user reports

Use `source_quality: medium` when evidence is credible but incomplete.

Use `source_quality: low` for drafts, single-source retrospectives, or broad
case studies where product strategy and UX issues are hard to separate.

## Product selection guidance

Prefer:

- narrow interface-level failures
- onboarding failures
- accessibility failures
- trust/provenance failures
- documented conversion or abandonment issues
- launch surfaces with screenshots or archived artifacts

Avoid, unless separable:

- broad business failures
- pricing-only issues
- market timing failures
- distribution failures
- brand controversies without interface evidence

## Issue taxonomy

Canonical issue classes live in `taxonomy/issue-classes.yaml`. Benchmark issues
must use those slugs. If a known issue cannot be mapped, propose a taxonomy
addition in the same change.

The seed taxonomy is drawn from an initial applied review and standard HCI
literature. It should evolve under benchmark pressure, not by brainstorming.

## Validation protocol

For each benchmark product:

1. Provide each persona with `description.md` and `surface.md` only.
2. Collect raw persona predictions.
3. Normalize predictions to `taxonomy/issue-classes.yaml`.
4. Compare normalized predictions to `known-issues.yaml`.
5. Score hits, misses, false positives, severity-weighted recall, and marginal
   persona contribution.
6. Update persona calibration notes only after scorer review.

## Near-term benchmark backlog

The repo currently includes five draft seed entries:

- `apple-maps-2012`
- `govuk-verify-2016`
- `healthcare-gov-2013`
- `snapchat-redesign-2018`
- `windows-8-2012`

These are starting points for calibration work. They still need scorer review
before being treated as `ready`. See `benchmark/REVIEW_NOTES.md`.

Future v0.2 candidates should be selected for source quality, not fame.
Historical examples can be useful, but many mix UX issues with strategy or
distribution.

Candidate categories:

- government service launch failures with public audits
- consumer onboarding failures with public retrospectives
- accessibility remediations with documented before/after issues
- AI products with documented trust, provenance, or out-of-distribution failures
- collaboration tools with archived launch UX critiques

The v0.2 target is 5 strong entries, not 20 weak ones.
