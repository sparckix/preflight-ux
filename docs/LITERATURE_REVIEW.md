# Literature And Positioning Notes

This note summarizes adjacent work as of June 2026. It is not a systematic
review; it is the positioning map for this repo.

## Category: Synthetic Users

The broad category is active and controversial. Industry commentary generally
allows synthetic users for early hypothesis generation, proto-personas, study
prep, and copy/label stress tests, but warns against treating synthetic users as
valid substitutes for real participants.

The core critique:

- synthetic users are too consistent
- they underrepresent real human variance
- they are prone to sycophancy
- they miss context-of-use and real stakes
- their outputs can sound like research without being evidence

This repo accepts that critique. It should not be positioned as a replacement
for interviews, usability studies, or telemetry.

## Category: LLM Agents For Usability Testing

Relevant work includes UXAgent, which uses LLM agents and a browser connector to
simulate usability testing of web designs before real human-subject studies.
That direction is close, but the emphasis is different:

- UXAgent centers simulated interaction and study-design rehearsal.
- Preflight UX centers calibrated critique, issue-class taxonomy, and benchmarked
  persona reliability.

## Category: Synthetic Heuristic Evaluation

Recent work compares multimodal LLM heuristic evaluation against human UX
evaluators. Results are mixed: some studies show strong issue coverage in
specific conditions, while others show low overlap with human experts and
substantial false positives.

Implication for this repo:

- do not claim generic LLM critique is reliable
- measure by issue class
- report false positives
- keep human judgment in the loop

## Category: Persona-Conditioned UI/UX Evaluation

PerceptUI is a close adjacent direction: persona-conditioned UI/UX evaluation
that predicts how a specific user would answer interface-related questions and
produces rationales. Its emphasis is human-aligned persona response modeling.

Preflight UX should not compete by claiming persona conditioning itself is new.
The contribution to pursue is the open calibration layer: issue-class taxonomy,
benchmark products, raw predictions, scorer-reviewed matches, and reliability
matrices by persona and issue class.

## Category: LLM Simulation Benchmarks

Simulation-fidelity benchmarks such as SimBench argue that LLM-based human
behavior simulation requires standardized tasks and metrics. The important
lesson is that simulation quality is uneven and must be measured rather than
assumed.

This repo adapts that stance to UX:

- benchmark known product issues
- score predictions
- publish calibration matrices
- treat demographic-specific simulation with caution

## Category: LLM-As-Judge Reliability

LLM evaluators have documented issues with bias, anchoring, sensitivity to prompt
wording, and inconsistent scoring. That matters because Preflight UX uses LLMs
to generate critique and, eventually, may use them to help normalize findings.

Design consequence:

- archive raw model text outside the public artifact surface
- keep normalized issue classes auditable
- keep public run traces redacted
- log model and prompt versions
- avoid letting the same model generate and silently grade its own findings

## Positioning statement

Preflight UX should be described as:

> A benchmark-calibrated pre-ship UX risk detection method using structured LLM
> persona panels.

An alternate product-facing description:

> An open, repo-native calibration loop for pre-ship UX risk review.

It should not be described as:

- AI user research
- synthetic interviews
- automatic usability testing replacement
- user behavior prediction without validation

## Research opportunity

The publishable contribution is not "LLMs can be personas." The contribution is
an evaluation framework:

- issue-class taxonomy for pre-ship UX risks
- benchmark corpus of known post-launch issues
- persona reliability matrix
- comparison to generic LLM critique and human heuristic review
- comparison to heuristic-evaluation prompting
- transparent normalized findings, redacted execution receipts, archived raw
  model text for internal audit, scoring notes, misses, and false positives
- live validation against shipped product outcomes

## Preflight UX Compared To Adjacent Work

| Direction | Strength | Limitation to avoid | Preflight UX response |
|---|---|---|---|
| UXAgent-style browser agents | Task execution, traces, and browser evidence | May optimize for simulated behavior rather than scorable product-risk predictions | Borrow browser capture and traces, but score against known UX issues |
| Synthetic heuristic evaluation | Direct comparison against human evaluators | May collapse many failure modes into aggregate coverage | Score by issue class, severity, persona, misses, and false positives |
| PerceptUI-style persona conditioning | Human-aligned persona response modeling | Can make persona realism the target instead of product usefulness | Treat personas as instruments and score their marginal contribution |
| LLM simulation benchmarks | Standardized tasks and metrics | Often not product-surface specific | Build benchmark entries around recoverable launch surfaces and documented UX issues |

## Selected references

- Park et al., "Generative Agents: Interactive Simulacra of Human Behavior,"
  arXiv:2304.03442: https://arxiv.org/abs/2304.03442
- Lu et al., "UXAgent: An LLM Agent-Based Usability Testing Framework for Web
  Design," arXiv:2502.12561: https://arxiv.org/abs/2502.12561
- Zheng et al., "EvAlignUX: Advancing UX Evaluation through LLM-Supported
  Metrics Exploration," arXiv:2409.15471: https://arxiv.org/abs/2409.15471
- Guerino et al., "Can GPT-4o Evaluate Usability Like Human Experts?",
  arXiv:2506.16345: https://arxiv.org/abs/2506.16345
- Zhong, McDonald, and Hsieh, "Synthetic Heuristic Evaluation,"
  arXiv:2507.02306: https://arxiv.org/abs/2507.02306
- Bougie et al., "PerceptUI: LLM Agents as Human-Aligned Synthetic Users for
  UI/UX Evaluation," arXiv:2606.05697: https://arxiv.org/abs/2606.05697
- Platt, Luchs, and Nizamani, "Catching UX Flaws in Code,"
  arXiv:2512.04262: https://arxiv.org/abs/2512.04262
- Hu et al., "SimBench: Benchmarking the Ability of Large Language Models to
  Simulate Human Behaviors," arXiv:2510.17516:
  https://arxiv.org/abs/2510.17516
- Stureborg, Alikaniotis, and Suhara, "Large Language Models are Inconsistent
  and Biased Evaluators," arXiv:2405.01724:
  https://arxiv.org/abs/2405.01724
- Nielsen Norman Group, "Synthetic Users: If, When, and How to Use
  AI-Generated Research": https://www.nngroup.com/articles/synthetic-users/
