# Benchmark Selection Guide

The benchmark is the credibility layer. A famous product failure is not
automatically a good benchmark entry. Prefer cases where the interface,
onboarding, accessibility, trust, or workflow issue is documented clearly enough
that a panel prediction can be scored.

## Inclusion criteria

A benchmark candidate should have:

- a recoverable launch or pre-fix surface
- at least one specific UX issue documented after launch
- public sources or permissioned internal evidence
- issue wording that maps to `taxonomy/issue-classes.yaml`
- enough detail to separate UX issues from strategy, pricing, distribution, or
  market timing

## Source-quality levels

### High

- primary postmortem, official audit, court/regulatory filing, or public
  incident report
- launch surface preserved by screenshots, archive, or video
- issue observed by users or measured in support/analytics/research
- specific enough to score hits and misses

### Medium

- credible secondary retrospectives
- partial surface reconstruction
- specific issue but incomplete severity evidence

### Low

- single blog post
- broad business retrospective
- vague complaints
- hard-to-reconstruct surface

Low-quality entries can be drafts, but they should not be used for calibration.

## Good candidates

Good benchmark candidates usually look like:

- "Users could not complete account creation because the flow required identity
  verification before browsing plans."
- "Screen reader users could not discover dynamically inserted results."
- "Users abandoned onboarding because progress and next steps were unclear."
- "The product presented confident AI output without provenance, causing trust
  failure for expert users."
- "Users wanted to share generated output, but the product lacked export or link
  affordances."

## Weak candidates

Weak benchmark candidates usually look like:

- "The product failed because people did not want it."
- "The company priced it wrong."
- "The brand was controversial."
- "The app launched too late."
- "Users did not like it" without a concrete surface-level failure.

## Candidate scoring checklist

Before adding a candidate, answer:

- Can a persona review the launch surface without seeing the known issue?
- Can the issue be mapped to an existing taxonomy slug?
- Would two independent scorers likely agree that a prediction matched the
  known issue?
- Is the issue narrow enough to avoid post-hoc rationalization?
- Is there enough evidence to assign severity?

## Benchmark diversity

The first 10 benchmark products should cover different failure modes:

- onboarding and empty states
- loading/progress feedback
- accessibility mechanics
- trust and provenance
- export/shareability
- domain mismatch
- AI-specific safety or out-of-distribution behavior
- navigation or information architecture

Do not overfit the benchmark to one product genre.

## Redaction and privacy

Public benchmark entries should use public evidence. If a benchmark comes from
internal product work:

- remove product names if needed
- remove private screenshots
- summarize behavior without exposing user data
- keep enough surface detail to make scoring possible

Never commit private user research data or proprietary product artifacts without
permission.
