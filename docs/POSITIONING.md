# Positioning

Preflight UX sits in the same broad area as synthetic users, LLM-assisted
heuristic evaluation, browser agents for usability testing, and
persona-conditioned UI/UX evaluation.

The project should not claim that LLM personas are new. The useful claim is
narrower: Preflight UX is an open, repo-native calibration loop for pre-ship UX
risk detection.

## Core Position

Preflight UX is for teams that want to turn early model critique into auditable
product-risk evidence.

The differentiator is the open loop:

1. capture the product surface
2. run structured personas against the same evidence
3. normalize findings to issue classes
4. preserve redacted execution receipts and archive raw model text
5. score predictions against known issues
6. publish misses and false positives
7. update persona reliability by issue class
8. export artifacts that product repos can consume

The public repository should expose the method rather than only describing it:
schemas, prompts, taxonomy, benchmark entries, normalized findings, score files,
misses, false positives, redacted execution receipts, and report templates.

## Adjacent Work

| Area | What it is good at | What Preflight UX should borrow | Where Preflight UX differs |
|---|---|---|---|
| Browser-agent usability testing | Simulated task execution, click traces, screenshots, and study rehearsal | URL capture, browser evidence, action logs, replayable traces | Preflight UX starts from product-risk synthesis and benchmark calibration rather than thousands of simulated sessions |
| Synthetic heuristic evaluation | Comparing AI-generated critique with human evaluator issue coverage | Human-baseline comparisons, issue-overlap scoring, evaluator reliability analysis | Preflight UX stores repo-native artifacts and scores by issue class, persona, severity, misses, and false positives |
| Persona-conditioned UI/UX evaluation | Modeling how a given persona would answer UI questions | Persona fidelity checks, response-distribution thinking, prompt-evolution from failures | Preflight UX treats personas as instruments for risk detection, not as claims about human realism |
| LLM simulation benchmarks | Standardized tasks, metrics, and reproducible scoring | Benchmark discipline, baselines, confidence intervals, repeated runs | Preflight UX adapts benchmark discipline to product surfaces and post-launch UX issues |
| Product analytics and support mining | Real post-launch signal from tickets, funnel drop-off, app reviews, and telemetry | Ground-truth issue sourcing and severity calibration | Preflight UX focuses on pre-ship prediction, then uses post-launch evidence as calibration data |
| Eval harnesses for LLM products | Repeatable task specs, model/provider comparisons, failure logs, and CI gates | Provider baselines, variance checks, and regression testing | Preflight UX evaluates UX-risk predictions, not task-answer correctness |

## Comparison To Current Research Directions

Preflight UX should position itself as a product-engineering complement to
research systems, not as a paper-only method.

| Direction | Typical unit of analysis | Strongest evidence | Failure mode | Preflight UX move |
|---|---|---|---|---|
| Synthetic users | Persona-like responses or interview-style answers | Qualitative plausibility, sometimes comparison with real participants | Sounds like user evidence without real stakes | Never call outputs user research; score issue predictions against documented failures |
| Heuristic LLM evaluation | Lists of usability violations | Issue overlap with expert evaluators | Aggregate coverage can hide false positives and missed severe classes | Score precision, recall, severity-weighted recall, misses, and false positives by issue class |
| Persona-conditioned UI evaluation | Predicted user answers and rationales | Human-alignment or response-similarity metrics | Persona realism becomes the target | Treat personas as instruments; keep or retire them by marginal contribution |
| Browser-agent UX testing | Click paths, task completion, screenshots | Replayable interaction traces | Simulated action can look precise while product-risk synthesis stays shallow | Borrow traces for surfaces, but keep the core output as product-risk action cards |
| LLM simulation benchmarks | Standardized tasks and simulation metrics | Repeated runs, controlled prompts, model comparisons | Generic tasks may not map to launch decisions | Build benchmark entries around recoverable launch surfaces and cited known issues |
| Product postmortem mining | Known failures after launch | Real incidents, support data, public reports | Arrives too late to help pre-ship teams | Use postmortems as ground truth for pre-ship prediction benchmarks |

## Research-Director Read

A skeptical research director should be able to accept the project without
accepting the premise that synthetic users are equivalent to real users. The
method should read as an auditable pre-study risk screen:

- it proposes risks before launch
- it ties each risk to supplied surface evidence
- it labels uncertainty and validation paths
- it preserves enough execution evidence to audit normalization
- it scores predictions against known issues when benchmark evidence exists
- it publishes misses and false positives instead of hiding them

That framing matters because the project is most credible when it keeps the
same shape as mature research and evaluation practice. It should have explicit
inputs, a stable protocol, traceable outputs, scorer notes, validation plans,
and revision history. The model is not the evidence. The evidence is the
calibrated loop around the model.

## Method Isomorphism

Preflight UX should be isomorphic to the workflow it wants product teams to
trust. Each public artifact should have a role that maps to an ordinary research
or evaluation artifact:

| Preflight UX artifact | Research or evaluation analogue | Why it exists |
|---|---|---|
| Product surface | Stimulus or test material | Keeps every reviewer and baseline on the same evidence |
| Persona or baseline prompt | Review instrument | Makes the lens explicit enough to compare and revise |
| Normalized finding | Coded observation or risk note | Converts free text into a stable issue class |
| Redacted trace | Session receipt | Proves what was run without exposing unnecessary raw transcript text |
| Raw-output archive | Audit log | Allows internal review of parsing and normalization decisions |
| Known issue | Ground-truth item | Prevents post-hoc claims from replacing scored evidence |
| Score file | Evaluation sheet | Records hits, misses, false positives, and scorer rationale |
| Reliability matrix | Instrument calibration | Shows which personas or baselines contribute by issue class |
| Report export | Product decision memo | Turns calibrated risk into action and validation plans |

This is the answer to the "synthetic user" critique: the project should not ask
people to trust a persona performance. It should ask them to inspect a system of
artifacts that behaves like a calibrated evaluation pipeline.

## Claims The Project Can Make Now

These claims are appropriate for the current public repo:

- Preflight UX provides an open schema and artifact format for pre-ship UX panel
  runs.
- It includes a draft issue taxonomy, persona library, benchmark scaffold, CLI,
  BYOK web UI, and report format.
- It is designed to preserve enough evidence for later scoring.
- Its current findings are product-risk hypotheses, not validated user research.

## Claims The Project Should Earn

These claims require more evidence:

| Claim | Evidence needed |
|---|---|
| "The panel catches recurring UX risk classes" | scored benchmark runs across multiple ready benchmark products |
| "Persona X is useful for issue class Y" | persona-by-issue-class precision and recall |
| "The method is stronger than generic LLM critique" | benchmark comparison against a generic critique baseline |
| "The method is competitive with synthetic heuristic evaluation" | issue-overlap comparison against a heuristic-evaluation baseline |
| "The method improves shipped products" | applied reports linked to shipped changes and post-launch validation |
| "The method outperforms human heuristic review in a setting" | comparison against human reviewers on the same benchmark surfaces |

## What Would Make It Distinctive

The project becomes meaningfully differentiated when the public repo contains:

- ready benchmark entries with recoverable launch or pre-fix surfaces
- known issues mapped to a stable taxonomy
- redacted traces for public runs and raw model text archived outside the public
  artifact surface
- normalized findings with scorer notes
- false-positive and miss logs
- repeated runs across at least two model providers
- baseline comparisons against generic critique and heuristic-evaluation prompts
- a persona reliability matrix by issue class
- at least one applied product case study with redacted but inspectable evidence

The strongest version of the project is not "synthetic users for UX." It is an
open measurement layer for deciding when synthetic UX critique is useful, where
it fails, and which parts of the output deserve product attention.

## What To Borrow

Preflight UX should borrow aggressively where adjacent work is stronger:

- from browser-agent systems: URL capture, screenshots, traces, and replayable
  evidence
- from synthetic heuristic evaluation: human-baseline comparison and issue
  overlap analysis
- from persona-conditioned evaluation: persona-fidelity checks and repeated
  failure-driven prompt improvement
- from simulation benchmarks: standardized tasks, repeated runs, and clear
  metrics

Borrowing does not weaken the positioning. It makes the calibration loop better.

## What To Avoid

The project should avoid:

- claiming persona prompting is new
- optimizing for persona vividness instead of measured contribution
- publishing only polished reports without archived raw-output access for
  internal audit
- putting raw model transcripts in the public path when normalized findings and
  redacted receipts are enough
- treating issue coverage as enough without false-positive accounting
- making product claims from draft benchmark entries
- calling outputs user research before live validation exists

## Open-Source Advantage

Many research systems are strongest as papers and weakest as reusable product
infrastructure. Preflight UX can be strongest where product teams and
contributors can inspect and run the method:

- exact prompts and model versions
- exact schemas
- exact issue taxonomy
- exact benchmark surfaces
- exact known issues and citations
- raw outputs archived outside the public artifact surface
- scorer notes
- scoring scripts
- CI checks
- BYOK web workflow
- repo-ready report artifacts

This transparency is part of the method. It lets contributors dispute matches,
add misses, replace weak benchmarks, and compare new panels against old ones.
