# Scoring Framework

This framework evaluates persona predictions against benchmark ground truth.
The goal is not to prove that a persona is "right" in general. The goal is to
measure where it is useful, where it is noisy, and where it should abstain.

## Inputs

For a benchmark product:

- `truth`: issue-class records from `benchmark/products/<slug>/known-issues.yaml`
- `predictions[persona]`: normalized issue-class predictions from a panel run
- `severity[issue]`: `minor`, `moderate`, or `severe`
- `run_meta`: model, prompt version, date, input artifact IDs, and scorer

## Per-persona metrics

```text
hits       = predictions[persona] ∩ truth
misses     = truth \ predictions[persona]
false_pos  = predictions[persona] \ truth

precision  = |hits| / |predictions[persona]|
recall     = |hits| / |truth|
f1         = 2 * precision * recall / (precision + recall)
coverage   = |predictions[persona]| / |truth|
```

If `predictions[persona]` is empty, precision is undefined and should be
reported as `null`, not `0`.

## Severity-weighted recall

Not all misses are equal. Use severity weights:

```text
minor    = 1
moderate = 2
severe   = 4
```

Then:

```text
severity_weighted_recall =
  sum(weight(issue) for issue in hits) /
  sum(weight(issue) for issue in truth)
```

This prevents a persona that catches many minor issues from looking better than
a persona that catches fewer but more consequential issues.

## False-positive rate

```text
false_positive_rate = |false_pos| / |predictions[persona]|
```

A persona that predicts every possible issue can achieve high recall while being
uselessly noisy. False positives should be reviewed by issue class.

## Panel-level metrics

For a panel of N personas:

```text
panel_predictions = union(predictions[persona] for persona in panel)
panel_hits        = panel_predictions ∩ truth
panel_false_pos   = panel_predictions \ truth

panel_precision   = |panel_hits| / |panel_predictions|
panel_recall      = |panel_hits| / |truth|
```

Panel quality is not the average persona score. It is the smallest set of
personas that catches important issues without overwhelming the product team.

## Marginal persona contribution

For persona `p` in panel `P`:

```text
marginal_hits(p) = hits(P) - hits(P without p)
```

Report both count and severity-weighted contribution. Personas with low marginal
contribution and high false positives should be removed or scoped down.

## Stability

Run stability matters because LLM outputs can vary by model, prompt, and time.
For important benchmark runs, record:

- model
- model version or snapshot
- prompt version
- temperature
- run date
- surface artifact hash or URL

Recommended stability check:

```text
same persona + same surface + same prompt + same model, repeated 3 times
```

Track agreement on normalized issue classes. If a persona only catches an issue
intermittently, calibration should reflect that.

## Calibration rules

Issue classes in a persona's "reliably surfaced" list should meet all of these:

- recall >= 0.60 on that class across benchmark products where the class appears
- precision >= 0.50 for that class
- at least two benchmark opportunities, unless marked provisional

Move an issue class to "misses" or "provisional" when:

- recall < 0.40
- false-positive rate > 0.50
- the persona detects the issue only under overly leading prompts

## Scorer discipline

Scoring should preserve three layers:

1. raw persona output
2. normalized issue-class mapping
3. hit/miss/false-positive judgment

Do not let a model silently generate, normalize, and grade its own output.
Human scorer review is required until the normalization pipeline itself is
validated.

## What this framework does not measure yet

- user-segment prevalence
- business impact
- implementation cost
- time-to-fix
- causal lift after remediation
- novel issue discovery outside the taxonomy

Those can be added after the basic benchmark is populated.
