# Panel Report Format

Use this format when a product repo consumes a Preflight UX run.

## 1. Summary

One paragraph. State the product surface, panel, date, and highest-leverage
risks. Include a clear uncertainty note.

## 2. Top risks

| Priority | Issue class | Persona | Severity | Confidence | Recommended action |
|---|---|---|---|---|---|
| P0 | `empty-state-confusion` | `tom-random-visitor` | severe | medium | Add a live example result |

Priority guidance:

- **P0**: likely abandonment, trust collapse, or inaccessible core flow
- **P1**: material conversion, comprehension, or repeat-use risk
- **P2**: polish, brand, or secondary workflow issue

## 3. Structured findings

Each finding should be normalized:

```yaml
- id: finding-001
  issue_class: empty-state-confusion
  persona: tom-random-visitor
  predicted_behavior: "Closes the tab before pasting anything."
  evidence: "First viewport has an empty form and no example output."
  severity: severe
  confidence: medium
  recommendation: "Show a pre-filled example and resulting critique."
  validation_needed: true
  calibration:
    populated: false
    notes: "Persona not yet benchmark-calibrated."
```

## 4. Persona disagreements

List meaningful disagreements, not every difference in wording. Disagreement is
valuable when it reveals a tradeoff:

- brand distinctiveness versus accessibility
- density versus first-time comprehension
- provenance transparency versus simplicity
- export/save power use versus low-friction first use

## 5. Recommended changes

Group by implementation lane:

- copy/content
- layout/visual hierarchy
- interaction behavior
- accessibility
- trust/provenance
- export/shareability
- instrumentation/validation

## 6. Confidence and uncertainty

Every report must include:

- what the panel is probably good at for this product
- what the panel is likely to miss
- which findings need real-user validation
- any evidence limitations in the supplied surface

## 7. Validation plan

Define how product teams will check the findings:

- analytics event
- session replay or usability observation
- support-ticket tag
- user interview question
- A/B or before/after comparison
- manual accessibility test

## 8. Appendix

Include redacted execution receipts and state whether raw model text was
archived. Raw model transcripts are useful for auditing normalization decisions,
but they do not need to sit in the public report path.
