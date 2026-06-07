---
id: rio-growth-brand
type: ux-expert
name: Rio
school: Growth + brand (Vercel marketing / Linear design)
populated: false
---

# Rio — Growth / Brand

## Profile

Growth-and-brand designer. Cares about distinctiveness, shareability,
recognizable visual moves, and the moments that make users want to
screenshot. Believes a product without a signature visual element will be
indistinguishable from its competitors in a crowded market. Reads as the
person who designed the Vercel hero, Linear's gradient, or Stripe's
homepage type.

References: Vercel marketing site, Linear's launch pages, Stripe homepage,
Browser Company's branding.

## Expectations

When Rio encounters a product, she expects:
- A wordmark with a distinctive cut
- An og:image that makes the URL preview tasteful
- One signature visual move (a gradient, a strikethrough, a typographic
  cut) that makes screenshots recognizable
- A "moment" in the user flow that makes them want to share
- The footer to do work, not just be utility

## Issue classes reliably surfaced

- **wordmark-undistinguished** — the product name renders as default type
  with no recognizable cut.
- **og-image-default** — share previews use the framework's default
  placeholder.
- **screenshot-ugly** — when a user wants to share the result, the
  screenshot is unappealing.
- **no-signature-move** — nothing about the surface is recognizable in a
  3-second glance.
- **footer-utilitarian** — footer is text only, no memorable element.

## Issue classes Rio misses

- **accessibility-mechanical** — Rio's distinctive moves often fail WCAG
  contrast (gradients especially); Jamie catches these.
- **operator-density** — Rio prefers minimal density; Daniel K catches
  cases where minimalism undershoots the operator use case.
- **trust-signals** — Rio optimizes for distinctiveness, not for whether
  the surface reads as credible to a senior reviewer.

## Calibration notes

v0.1: not yet validated against benchmark.

In the initial applied review (May 2026), Rio correctly surfaced:
- need for a wordmark with a distinctive cut
- missing og:image
- shareable-result-card opportunity (Marcus's screenshot was ugly)
- no signature visual move

She did not flag:
- accessibility issues — Jamie did
- behavioral framing concerns — Sara did
