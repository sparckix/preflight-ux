# Schemas

Machine-readable contracts for public artifacts.

Current schemas:

- `persona.schema.json` — persona frontmatter
- `issue-classes.schema.json` — taxonomy file
- `known-issues.schema.json` — benchmark ground truth
- `meta.schema.json` — benchmark metadata
- `panel-run.schema.json` — normalized panel or baseline run output
- `report-finding.schema.json` — structured report finding
- `score.schema.json` — class-level or reviewed benchmark score output,
  including panel/baseline metadata when present

The local validator does lightweight structural checks without requiring JSON
Schema dependencies. Future CLI work should validate these schemas directly.

- `review-brief.schema.json` describes web-generated review brief exports.
