# Second-Scorer Cold Review - 2026-05-12

Reviewer role: independent benchmark scorer.

Scope: cold review of the five draft seed benchmark entries. This review checks source quality, issue-class mapping, and whether each entry can be promoted from `draft` to `ready` for calibration.

## Summary

None of the five seed entries should be promoted to `ready` yet. All five are usable for workflow testing. Three have credible enough issue mappings to proceed toward scorer reconciliation after better surface reconstruction. Two need narrower issue definitions before calibration.

| Product | Decision | Why |
|---|---|---|
| `apple-maps-2012` | conditionally accepted, keep `draft` | Core data-quality trust issue is strong; transit and provenance issues need tighter source/surface support. |
| `govuk-verify-2016` | conditionally accepted, keep `draft` | Official evidence is strong; surface reconstruction is still too abstract for persona scoring. |
| `healthcare-gov-2013` | conditionally accepted, keep `draft` | Strong sources; must separate UX flow choices from infrastructure failure. |
| `snapchat-redesign-2018` | conditionally accepted, keep `draft` | IA and workflow-regression issues are plausible; needs screenshots or archived app captures. |
| `windows-8-2012` | conditionally accepted, keep `draft` | Strong UX critique, but current sources are mostly secondary reports of NN/g findings. |

## Cross-Cutting Findings

- The benchmark entries are good enough to test `uxpanel report` and `uxpanel score`.
- They are not yet good enough for persona calibration claims.
- Source cleanup was needed: inaccessible or weak public dependencies were replaced where possible.
- The current benchmark mixes interface flaws, data quality, and infrastructure failures. That is acceptable only if scoring notes keep those classes separate.
- The next review should add surface evidence: screenshots, archived pages, app-review excerpts, or primary reports.

## Product Reviews

### `apple-maps-2012`

Decision: conditionally accepted, keep `draft`.

Accepted mappings:

- `inaccurate-map-data` -> `data-quality-trust-break`
- `missing-transit-directions` -> `data-quality-trust-break`
- `alternative-app-recommendation` -> `trust-without-provenance`

Source notes:

- The Guardian and MacRumors/Wired sources are enough to establish public apology, incorrect data, missing features, and trust failure.
- The missing-transit issue should be scored as expected-utility removal inside a data/trust product, not as generic feature dissatisfaction.

Blocking gap before `ready`:

- Add a launch-surface artifact that shows the Maps UI or a sourced reconstruction of default replacement context.

### `govuk-verify-2016`

Decision: conditionally accepted, keep `draft`.

Accepted mappings:

- `difficulty-signing-up` -> `identity-verification-friction`
- `access-to-services-blocked` -> `service-unavailable-blocker`
- `vulnerable-users-affected` -> `vulnerable-user-access-barrier`

Source notes:

- Parliamentary and Public Accounts Committee sources are strong enough for ground truth.
- This is one of the better benchmark candidates because the issue is public-service access, not mere preference.

Blocking gap before `ready`:

- The `surface.md` needs a more concrete user-facing flow: provider choice, verification steps, failure state, and return-to-service behavior.

### `healthcare-gov-2013`

Decision: conditionally accepted, keep `draft`.

Accepted mappings:

- `account-before-shopping` -> `account-before-value`
- `account-creation-blocked` -> `service-unavailable-blocker`
- `waiting-and-retry-frustration` -> `loading-abandonment`

Source notes:

- ProPublica and GAO are acceptable sources for account-before-shopping and launch-scale reliability failures.
- The source cleanup replaced less stable public dependencies with GAO and ProPublica.

Blocking gap before `ready`:

- Scoring notes must distinguish intentional UX sequencing from system reliability. Otherwise personas may get credit for predicting an outage they could not infer from the surface.

### `snapchat-redesign-2018`

Decision: conditionally accepted, keep `draft`.

Accepted mappings:

- `stories-mixed-with-messages` -> `information-architecture-overload`
- `harder-to-find-friends` -> `navigation-discoverability`, after narrowing to friend-story destinations
- `rewatching-stories-cost` -> `interaction-cost-regression`

Source notes:

- TechCrunch and Guardian support user confusion, Stories moving into messaging contexts, petition-level backlash, and loss of familiar Story behavior.
- CNBC was removed as a dependency because it was not a good public source dependency in this environment.

Blocking gap before `ready`:

- Add screenshots or archived contemporary walkthroughs of the redesigned Friends/Stories surfaces.

### `windows-8-2012`

Decision: conditionally accepted, keep `draft`.

Accepted mappings:

- `dual-environment-overhead` -> `register-fighting`
- `hidden-charms` -> `hidden-feature-discoverability`
- `low-density-single-window-power-loss` -> `operator-density-undershoot`

Source notes:

- The issue classes are good tests for panel disagreement: operator-tool personas should react differently from brand or editorial personas.
- Current sources are mostly secondary coverage of usability expert findings. Good enough for draft, not enough for calibration-ready status.

Blocking gap before `ready`:

- Add primary NN/g source if available or direct screenshots/video of Charms, Start screen, and desktop transitions.

## Changes Made During Review

- Replaced weaker or inaccessible Apple Maps sources with Guardian, MacRumors, and Wired references.
- Replaced weaker HealthCare.gov sources with ProPublica and GAO references.
- Replaced CNBC dependency in Snapchat with TechCrunch and Guardian references.
- Narrowed Snapchat `harder-to-find-friends` wording to friend-story destination discoverability.
- Marked benchmark metadata reviewer as `second-scorer-cold-review-2026-05-12`.

## Remaining Work Before Calibration

1. Add stable launch-surface artifacts for every benchmark product.
2. Add second-scorer signoff at the issue level, not only class level.
3. Decide whether infrastructure-blocker issues should count in the same benchmark as intentional UX-design issues.
4. Run at least one real panel pass on each `ready` product.
5. Compare panel findings against known issue IDs, not only issue classes.
