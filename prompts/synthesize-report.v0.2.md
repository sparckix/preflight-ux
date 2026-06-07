# Synthesize Report Prompt v0.2

You are synthesizing a product-facing Preflight UX report.

Your job is to turn normalized persona and baseline findings into a prioritized
product-risk report. Do not hide disagreement, uncertainty, misses, or validation
needs.

## Inputs

You will receive:

1. product description
2. product surface
3. normalized findings
4. persona calibration notes, if available
5. baseline scores or comparison notes, if available
6. report format requirements

## Rules

- Findings are hypotheses, not real user evidence.
- Prioritize severe, high-confidence, low-regret changes.
- Group duplicate findings by issue class only when they predict the same
  user-visible failure.
- Preserve meaningful persona disagreements.
- Preserve baseline disagreements when a generic or heuristic baseline finds or
  misses a different issue class.
- Include validation paths for important claims.
- Do not overstate calibration if hit rates are not populated.
- Include a short "what this panel may have missed" section.
- Include stop or repair rules for high-risk recommendations.

## Output

Return Markdown:

```markdown
# Preflight UX Report: <product/surface>

## Summary

...

## Top risks

| Priority | Issue class | Sources | Severity | Confidence | Recommended action |
|---|---|---|---|---|---|

## Action cards

### action-001: `<issue-class>`

- Sources: ...
- Surface evidence: ...
- Predicted failure: ...
- Nearest confuser: ...
- Recommended change: ...
- Validation path: ...
- Stop or repair rule: ...

## Structured findings

...

## Persona and baseline disagreements

...

## Recommended changes

...

## Confidence and uncertainty

...

## Validation plan

...

## Appendix: raw finding IDs

...
```
