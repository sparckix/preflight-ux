# Benchmark Review Notes

Second-scorer cold review: `benchmark/SECOND_SCORER_REVIEW_2026-05-12.md`.

The five seed benchmark entries remain intentionally marked `draft`. They provide
enough structure to test the workflow, and they now have a second-scorer cold
review, but they should not be used for final persona calibration until surface
artifacts and scorer reconciliation are complete.

## Seed Entry Status

| Product | Current quality | Main strength | Main gap before `ready` |
|---|---|---|---|
| `apple-maps-2012` | medium | strong public evidence of trust/data-quality failure | add archived launch screenshots and stronger primary-source capture of missing transit expectations |
| `govuk-verify-2016` | high | parliamentary/public-audit evidence | reconstruct the exact user-facing verification surface more concretely |
| `healthcare-gov-2013` | high | official GAO evidence plus contemporary launch reporting | separate technical outage effects from intentional account-before-value flow |
| `snapchat-redesign-2018` | medium | clear contemporary user backlash around IA changes | add screen captures or release screenshots of the redesigned Friends/Stories surfaces |
| `windows-8-2012` | medium | strong usability-review evidence | add archived NN/g primary article or direct screenshots of Charms/Start/Desktop transitions |

## Promotion Checklist

Before changing `benchmark_status` from `draft` to `ready`:

- [ ] Launch surface is reconstructable without reading known issues.
- [ ] Every known issue maps to a taxonomy slug.
- [ ] Every severe issue has primary or multiple independent secondary sources.
- [ ] A second scorer agrees with the issue-class mapping.
- [ ] Notes distinguish UX failures from business, strategy, or infrastructure
      failures.

## Scorer Notes

Scorers should record:

- accepted issue mappings
- rejected issue mappings
- ambiguous source evidence
- false-positive traps likely to affect personas
- whether a benchmark should be excluded from calibration
