# Personas

Personas are structured review lenses. They are not fictional users whose
statements should be treated as research evidence.

Each persona exists to catch specific issue classes, miss other issue classes,
and become more or less trusted as benchmark evidence accumulates.

## Directory layout

```text
personas/
  ux-experts/   expert critique lenses
  user-types/   audience and workflow archetypes
```

## Required frontmatter

```yaml
---
id: unique-slug
type: ux-expert | user-type
name: Short Human Name
populated: false
---
```

The `id` must be stable. Do not rename a persona once benchmark runs reference
it unless you also provide a migration note.

## Required sections

Every persona should include:

- profile
- expectations
- issue classes reliably surfaced
- issue classes missed
- calibration notes

User-type personas should also include:

- drop-off vulnerabilities
- behavioral patterns
- sharing behavior
- what the persona validates
- what the persona breaks

## Persona contract

A good persona states:

- what evidence it is allowed to use
- what it is likely to over-predict
- which issue classes it should abstain from
- how its claims will be scored

The persona should not be optimized for literary richness. It should be
optimized for calibrated issue detection.

## v0.1 personas

UX experts:

- `maya-editorial-designer` — editorial/type-led design
- `daniel-k-operator-tool` — dense operator tools
- `sara-ux-researcher` — behavioral UX research
- `jamie-accessibility` — accessibility and inclusion
- `rio-growth-brand` — growth, brand, and shareability

User types:

- `priya-mba-deadline` — deadline-driven student
- `marcus-junior-consultant` — heavy AI user in consulting workflow
- `elena-founder-skeptical` — technical founder with low tolerance for fluff
- `greg-pe-partner` — senior reviewer with low AI trust
- `aisha-policy-researcher` — researcher outside the original corpus domain
- `yuki-ai-researcher` — adversarial technical tester
- `tom-random-visitor` — contextless visitor from a social link

These were seeded from an initial applied review. Their calibration notes are
qualitative until benchmark runs populate hit rates.

## Adding or changing personas

Before adding a persona, check:

1. Does it add a measurable issue-class coverage gap?
2. Does it overlap with an existing persona?
3. What false positives will it likely create?
4. What benchmark products could validate it?

Prefer editing an existing persona over adding a new one unless the new persona
has a clear scoring role.
