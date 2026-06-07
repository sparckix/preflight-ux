# Normalize Findings Prompt v0.2

You are normalizing raw Preflight UX findings into the canonical issue taxonomy.

You are not judging whether the finding is true. You are mapping a raw finding
to a stable issue class, preserving evidence, and making false-positive review
possible.

## Inputs

You will receive:

1. raw persona or baseline findings
2. the canonical issue taxonomy

## Rules

- Preserve the original finding text.
- Choose the closest taxonomy slug only when the mapping is defensible.
- Use aliases as hints, not as automatic matches.
- If two classes are plausible, choose the narrower class and record the
  nearest confuser.
- If no class fits, use `unmapped` and propose a candidate slug.
- Do not add severity unless the raw finding or evidence supports it.
- Do not collapse distinct findings unless they predict the same user-visible
  failure.
- Keep source-bound receipts. A normalized finding without surface evidence
  should be `confidence: low` or omitted.

## Output

Return YAML:

```yaml
findings:
  - id: finding-001
    persona: persona-id
    source: persona-id-or-baseline-source
    raw_finding: "Original finding text"
    issue_class: empty-state-confusion
    alternative_classes: []
    nearest_confuser: "trust-without-provenance"
    severity: severe
    confidence: medium
    evidence: "Surface evidence"
    recommendation: "Recommended change"
    validation_path: "How a product team should validate this"
    stop_or_repair_rule: "When to drop, defer, or revise this finding"
    normalization_notes: "Why this class fits"
```

Use `confidence: low | medium | high`.
Use either `persona` or `source`; use both only when both are meaningful.
