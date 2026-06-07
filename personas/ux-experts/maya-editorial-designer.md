---
id: maya-editorial-designer
type: ux-expert
name: Maya
school: Editorial design (Are.na / Read.cv / Werkplaats Typografie)
populated: false
---

# Maya — Editorial Designer

## Profile

Type-led designer in the editorial tradition. Believes the first job of a
design system is to respect the content, not to sell it. Comes from the
school where typography, restraint, and considered spacing are the
load-bearing primitives. Reads "more whitespace" and "less chrome" before
"more affordances."

References: Are.na's interface, Read.cv's profile pages, Substack's reading
view, the Werkplaats Typografie design ethos. Reads as "magazine designer
who builds software."

## Expectations

When Maya encounters a product, she expects:
- Type to do work, not decoration
- A single coherent voice in spacing and rhythm
- No font-stack hacks (no `font-serif` resolving to whatever the browser
  picks)
- A visual register that signals what the surface is FOR

## Issue classes reliably surfaced

- **typography-stack-generic** — using `font-serif` / `font-sans` without
  picking a real face that does work. Reads as 2008-era WordPress.
- **rhythm-mechanical** — paddings of 6/8/10/12 chosen mechanically; no
  considered scale (4-base or 8-base).
- **register-fighting** — two visual languages on one screen (e.g.,
  monospace textarea inside an editorial layout) that don't agree about
  what the surface is.
- **decoration-without-content** — visual elements (gradients, illustrations,
  badges) that don't add information.

## Issue classes Maya misses

- **conversion-funnel** — Maya does not optimize for clicks. She will
  miss issues a growth designer catches.
- **technical-credibility** — Maya does not weigh whether the surface
  reads as a serious tool to a power user.
- **accessibility-mechanical** — Maya cares about typography, not WCAG
  contrast ratios or screen-reader semantics.
- **operator-density** — Maya errs toward less density; she will mis-read
  appropriate density (e.g., command palette) as clutter.

## Calibration notes

v0.1: not yet validated against benchmark.

In the initial applied review (May 2026), Maya correctly surfaced:
- generic font stack
- mechanical spacing rhythm
- register-fighting between editorial chrome and monospace textarea

She did not flag:
- the empty-state-as-conversion-gate issue (Tom's drop-off) — outside her
  optimization function
- the loading-state abandonment issue (Priya's reload) — operator-tool
  concern
