# Preflight UX Action Card Prompt v0.2

Use this output contract when a panel finding should become a product action.

The card is designed to prevent plausible but ungrounded critique. Every action
must bind to supplied surface evidence, state the failure it predicts, name the
nearest confuser, and define a validation or repair path.

## Action Card

```yaml
id: action-001
issue_class: empty-state-confusion
source: persona-id-or-baseline-source
severity: minor | moderate | severe
confidence: low | medium | high
surface_evidence:
  - "Quoted or tightly paraphrased evidence from the supplied surface."
predicted_failure: "What may break, stated as a product-risk hypothesis."
nearest_confuser: "The plausible alternative explanation or adjacent issue class."
recommended_change: "The product change to make."
validation_path: "Telemetry, usability observation, support tag, accessibility test, or scorer review."
stop_or_repair_rule: "When to drop, defer, or revise this action."
```

## Rules

- Do not create an action card without surface evidence.
- Do not treat screenshots, URLs, or product notes as browsed content unless the
  evidence is explicitly visible or supplied.
- Prefer one specific change over a broad design principle.
- Use `nearest_confuser` to avoid over-crediting generic critique.
- Use `stop_or_repair_rule` to make false positives auditable.
- If evidence is weak, lower confidence or abstain.
