---
id: aisha-policy-researcher
type: user-type
name: Aisha
archetype: Policy researcher, domain outside corpus
populated: false
---

# Aisha — Policy Researcher

## Profile

38, federal policy researcher. Pasting a draft policy brief. Domain:
housing affordability. Outside the corpus the tool was trained on.

## Expectations on first encounter

- Cautious
- Reads explainer carefully (privacy, what the tool does, where the corpus
  comes from)
- Tests with a real brief before deciding

## Drop-off vulnerabilities

- **domain-mismatch-exhibit** — exhibit is from a startup case, has nothing
  to do with policy → trust break
- **no-domain-coverage-signal** — tool gives confident answer despite being
  outside its training domain → trust loss
- **honest-low-match-missing** — system never says "this is outside what
  we know"

## Behavioral patterns

- Pastes 1200-word housing voucher reform brief
- Result identifies the right structural pattern with a sharp question
- Exhibit comparison feels strained (different domain)
- Uses once
- Does not share with peers because case examples don't match her domain
- Would return if corpus expanded to policy

## Sharing behavior

- Internal team Slack: maybe
- Public: not until corpus is broader
- Researcher community: would mention if it had a policy-specific corpus

## What Aisha validates

- `honest_low_match` flag when corpus is outside her domain
- Domain-agnostic pattern recognition (the pattern works even when the
  exhibit doesn't)
- Privacy posture (no logging)

## What Aisha breaks

- Confident answer outside training domain
- Domain-mismatched exhibits
- No "I don't know this domain" signal

## Calibration notes

v0.1: validated qualitatively against the initial applied product surface. Drove the
"strip exhibit / threshold-gate" backlog flag.
Hit-rate slot: empty.
