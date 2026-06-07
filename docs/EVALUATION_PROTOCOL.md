# Evaluation Protocol

This protocol defines the evidence needed before Preflight UX makes strong
claims about predictive value, persona reliability, or performance against
baselines.

## Evaluation Questions

The first evaluation should answer:

1. Which known UX issues are recovered from the launch or pre-fix surface?
2. Which issue classes are over-predicted?
3. Which personas add unique coverage?
4. How often does the panel produce plausible but unsupported findings?
5. Does the panel outperform simpler baselines on the same surfaces?

## Benchmark Requirements

A benchmark product is ready for scoring when it has:

- a recoverable launch or pre-fix surface
- at least one documented post-launch UX issue
- citations for each known issue
- issue classes mapped to `taxonomy/issue-classes.yaml`
- severity labels with scorer notes
- enough surface detail to run the panel without exposing known issues
- second-scorer review for issue mappings

Draft benchmark entries can test tooling. They should not support performance
claims.

## Baselines

Every scored benchmark should include at least these baselines:

### Generic LLM Critique

Prompt a current model to critique the product surface without personas,
taxonomy, or panel structure.

Purpose: measure whether the panel adds value over ordinary model critique.

Create the scaffold:

```bash
python3 -m uxpanel baseline \
  --surface benchmark/products/<slug>/surface.md \
  --surface-type benchmark \
  --kind generic-critique \
  --run-id <slug>-generic-critique
```

### Heuristic-Evaluation Prompt

Prompt a current multimodal model to evaluate the surface against a known
heuristic checklist, such as visibility of system status, match to user
expectations, control and freedom, consistency, error prevention, recognition
over recall, efficiency, and accessibility basics.

Purpose: measure whether the panel adds value over checklist-driven critique.

Create the scaffold:

```bash
python3 -m uxpanel baseline \
  --surface benchmark/products/<slug>/surface.md \
  --surface-type benchmark \
  --kind heuristic-evaluation \
  --run-id <slug>-heuristic-evaluation
```

### Preflight Panel

Run the default panel with the same surface evidence, model provenance, prompt
versions, and output retention rules.

Purpose: measure issue-class coverage, persona contribution, misses, and false
positives.

Create the scaffold:

```bash
python3 -m uxpanel run \
  --surface benchmark/products/<slug>/surface.md \
  --surface-type benchmark \
  --panel panels/default.yaml \
  --run-id <slug>-panel
```

Optional later baselines:

- browser-agent run with task traces
- human heuristic review
- multi-model consensus run
- single strongest persona run

## Scoring Units

Score at two levels:

### Issue Class Level

Issue-class scoring asks whether a prediction found the right type of failure.

Use for early calibration because it is more robust to wording differences.

### Issue ID Level

Issue-ID scoring asks whether a prediction matched a specific known issue.

Use for stronger claims because it reduces post-hoc credit.

## Metrics

Report:

- precision
- recall
- F1
- severity-weighted recall
- false-positive count
- miss count
- per-persona marginal contribution
- per-issue-class hit rate
- abstention or quarantine candidates for noisy personas

When repeated runs exist, report variance across model, prompt, and run date.

## Scorer Rules

Scorers should see:

- the launch or pre-fix surface
- the model output being scored
- the known issue list
- the issue taxonomy

Scorers should record:

- accepted matches
- rejected matches
- ambiguous matches
- unsupported claims
- notes on whether the prediction was inferable from the supplied surface

Do not give credit for predicting issues that could not reasonably be inferred
from the benchmark surface.

## Release Thresholds

Use these thresholds for public claims:

### v0.2

- 5 ready benchmark products
- one complete scored run across all ready products
- generic critique baseline
- false-positive and miss logs

### v0.3

- 10-12 ready benchmark products
- issue-ID scoring in addition to issue-class scoring
- persona-by-issue-class reliability matrix
- heuristic-evaluation baseline
- repeated runs across at least two model providers

### v0.4

- live product validation
- shipped changes linked to panel findings
- post-launch hit, miss, and false-positive analysis
- technical report with methods and limitations

## Reporting

Every evaluation report should include:

- benchmark products and source quality
- benchmark-selection rationale or information-gain note
- exact prompts and model versions
- redacted execution receipts
- raw-output archive status
- normalized findings
- scoring notes
- metrics table
- false positives
- misses
- limitations
- changes to personas, prompts, or taxonomy made after scoring

Baseline runs are stored as normal `run.json` artifacts with
`run_type: baseline`, a `baseline.kind`, and a `baseline.prompt_ref`. Normalized
baseline findings should use a `source` such as `baseline-generic-critique`
instead of a persona ID.

The baseline runner tries subscription CLIs first and API providers second. It
supports Codex and Claude subscriptions, then Anthropic, OpenAI, and Gemini API
fallbacks.

```bash
python3 tools/run_baseline_agent.py --run runs/<slug>-generic-critique
```

Override the order if needed:

```bash
python3 tools/run_baseline_agent.py \
  --run runs/<slug>-generic-critique \
  --transports claude,codex,gemini,anthropic,openai
```

Panel runs use the same transport stack. First scaffold a run from a panel
definition, then execute each persona:

```bash
python3 -m uxpanel run \
  --surface benchmark/products/<slug>/surface.md \
  --panel panels/public-service-access.yaml \
  --out runs/<slug>-public-service-panel-v0-3 \
  --run-id <slug>-public-service-panel-v0-3

python3 tools/run_panel_agent.py \
  --run runs/<slug>-public-service-panel-v0-3
```

Use focused panels when the benchmark has a clear domain. For public-service,
identity, or benefits flows, `panels/public-service-access.yaml` keeps the
review on access, inclusion, trust, and first-session comprehension instead of
brand or growth concerns.

Compare score files with:

```bash
python3 -m uxpanel compare-scores \
  calibration/<slug>-panel.score.json \
  calibration/<slug>-generic-critique.score.json \
  calibration/<slug>-heuristic-evaluation.score.json
```

The goal is not to avoid failure. The goal is to make failure visible enough
that the method can improve.
