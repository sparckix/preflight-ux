# Contributing

Preflight UX welcomes contributions that make pre-ship UX risk review more
traceable, measurable, and useful in product work.

The project is intentionally conservative about claims. A contribution does not
need to prove the whole method. It should make one part of the method easier to
inspect, run, score, or improve.

## Useful Contributions

High-value contributions include:

- benchmark products with cited post-launch UX issues
- launch-surface reconstructions from public or permissioned sources
- issue-class definitions, aliases, and severity guidance
- scored runs against benchmark products
- misses and false-positive reports
- persona calibration notes
- schema validation and CLI improvements
- report-format improvements
- web UI improvements that preserve the BYOK and local-export posture

Low-value contributions include:

- adding personas without calibration pressure
- broad product retrospectives without a scorable UX issue
- synthetic interview transcripts
- generic UX advice that cannot be mapped to an issue class
- claims that panel output replaces real user research

## Project Principles

1. Evidence over plausibility. A finding that sounds right is still
   uncalibrated until it is scored or validated.
2. Personas are instruments, not characters. A persona is useful when it catches
   a measurable class of risk.
3. Misses matter. False positives and missed issues are part of the data.
4. Narrow claims age better than broad ones.
5. Real users outrank synthetic users. Observed behavior, accessibility testing,
   telemetry, support data, and user research supersede panel predictions.

## Development Setup

The repo has no required runtime dependencies for the core validator and CLI.

Run the local checks:

```bash
python3 tools/validate_repo.py
python3 -m uxpanel validate
python3 tests/simulate_local.py
node tests/simulate_web_static.mjs
node tests/simulate_web_logic.mjs
node tests/simulate_byok_api.mjs
```

Run a syntax check for the serverless API:

```bash
node --check api/panel.js
```

## Adding A Benchmark Product

Create the scaffold:

```bash
python3 -m uxpanel new-benchmark example-product-2026
```

Fill in:

- `benchmark/products/<slug>/description.md`
- `benchmark/products/<slug>/surface.md`
- `benchmark/products/<slug>/known-issues.yaml`
- `benchmark/products/<slug>/meta.yaml`

Benchmark entries should focus on documented UX failures, not general business
outcomes. If a product failed because of strategy, distribution, pricing, or
timing, include it only when there is a separable interface or product
experience issue.

Before marking a benchmark `ready`, make sure:

- the launch or pre-fix surface is recoverable
- every known issue has citations
- every issue maps to `taxonomy/issue-classes.yaml`
- severe issues have primary or multiple independent secondary sources when
  possible
- two scorers can reasonably agree on the issue mapping

## Adding An Issue Class

Add issue classes to `taxonomy/issue-classes.yaml`.

Each class should have:

- a stable slug
- a plain-language definition
- what counts
- what does not count
- severity guidance
- aliases or common phrasings

Prefer using an existing class unless the new class changes scoring in a
meaningful way.

## Adding Or Changing A Persona

Personas must follow the structure in `personas/README.md`.

Before adding a persona, answer:

- Which issue class should this persona catch?
- Which existing persona misses that class?
- What will this persona over-predict?
- What evidence is the persona allowed to use?
- How will the persona be calibrated?

Do not add a persona solely because the user type is interesting.

## Reporting Calibration Results

A calibration result should include:

- benchmark product slug
- surface version
- model, model version, and prompt version
- persona ID
- raw finding
- normalized issue class
- hit, miss, or false positive
- scorer notes

Keep raw outputs available so normalization decisions can be audited later.

## Data And Privacy

Do not include private user data, proprietary screenshots, unreleased product
details, interview transcripts, analytics exports, customer support tickets, or
secrets. Public benchmark entries should use public sources or explicitly
permissioned material.

## Pull Request Checklist

- [ ] Public claims are scoped to available evidence.
- [ ] New benchmark issues include citations.
- [ ] New issue classes are documented in the taxonomy.
- [ ] Persona changes update expected strengths, misses, and over-predictions.
- [ ] Raw and normalized findings remain auditable.
- [ ] Local checks pass.
- [ ] Synthetic output is not represented as real user research.
