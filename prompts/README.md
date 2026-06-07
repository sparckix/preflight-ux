# Prompt Templates

These prompts define the reproducible review workflow. Keep prompt versions
stable once benchmark runs reference them.

Recommended flow:

1. Run `expert-persona-review.v0.2.md` for UX-expert personas.
2. Run `user-type-review.v0.2.md` for user-type personas.
3. Use `panel-action-card.v0.2.md` as the action-card contract for findings
   that should become product work.
4. Run `normalize-findings.v0.2.md` to map raw findings to taxonomy slugs while
   preserving surface evidence, nearest confusers, validation paths, and stop or
   repair rules.
5. Run `synthesize-report.v0.2.md` to produce the product-facing report.

The v0.2 prompts reflect two lessons from internal prompt-evaluation work and
current provider guidance:

- passive prompt labels are weaker than typed, source-bound action artifacts
- structured receipts, nearest-confuser fields, and repair/stop rules make
  false positives easier to audit
- stable instructions should come before variable product context for prompt
  caching
- prompts should ask for concise evidence and decisions, not hidden
  chain-of-thought

Benchmark comparisons should also create baseline prompts through the CLI:

```bash
python3 -m uxpanel baseline --kind generic-critique --surface benchmark/products/<slug>/surface.md
python3 -m uxpanel baseline --kind heuristic-evaluation --surface benchmark/products/<slug>/surface.md
```

The generated `baseline-prompt.md` should be preserved with the run so baseline
scores can be audited against the exact prompt text.

Every run should record:

- prompt filename and version
- model name and version
- temperature
- product surface artifact
- persona ID
- baseline kind, when the run is a baseline
- date

Do not edit a prompt in place after it has been used for scored benchmark runs.
Create a new version instead.
