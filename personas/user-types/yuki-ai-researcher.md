---
id: yuki-ai-researcher
type: user-type
name: Yuki
archetype: AI researcher, adversarial tester
populated: false
---

# Yuki — AI Researcher

## Profile

34, ML researcher. Will try to break the tool to see what's under the
hood. Audience for technical writeups.

## Expectations on first encounter

- Reads "no login, no logging" — okay, decent privacy posture
- Looks at backend model, retrieval design, similarity scores
- Tests with strawman, well-formed argument, gibberish
- Opens the network tab

## Drop-off vulnerabilities

- **opaque-retrieval** — can't see why an answer was retrieved → discounts
  trust
- **no-failure-mode-exposed** — tool gives confident output on adversarial
  input → posts negative
- **prompt-injection-vulnerable** — pastes "ignore previous instructions"
  → tool obeys → posts very negative

## Behavioral patterns

- Pastes strawman: gets correctly identified
- Pastes well-formed: gets `honest_low_match` (correct move)
- Pastes gibberish: gets closest match with low_match flag (acceptable)
- Opens network tab to find similarity scores

## Sharing behavior

- Twitter post: "X is doing the right thing on adversarial inputs" → 200
  likes, 50 visitors over 24 hours
- Or: "X is broken under [adversarial input]" → 500 likes, distribution
  collapse for the product

## What Yuki validates

- `honest_low_match` flag
- Visible similarity scores or confidence indicators
- Robust handling of adversarial inputs (prompt injection, gibberish,
  edge cases)
- Technical credibility in footer

## What Yuki breaks

- Confident outputs on gibberish
- Prompt injection success
- Hidden retrieval / no provenance
- Marketing-heavy framing

## Calibration notes

v0.1: validated qualitatively against the initial applied product surface. Yuki's
adversarial-robustness check is one of the issue classes the v0.1 panel
*missed*; the methodology piece flags it as a future addition.
Hit-rate slot: empty.
