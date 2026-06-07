# Product UI

Preflight UX includes a deployable browser interface for teams that want to run
or prepare panel reviews without hand-editing JSON.

The UI should remain a thin product workflow over the same artifacts used by the
CLI: review briefs, panel runs, normalized findings, redacted run receipts, and Markdown
reports.

## Current Capabilities

- Capture a product brief, audience, stage, surface description, and prototype
  or live URL.
- Accept local PNG, JPG, and WebP screenshots for multimodal review.
- Import prior review-brief JSON or `run.json` artifacts.
- Select the default panel or a subset of personas.
- Select issue-class focus areas.
- Generate and validate a structured review brief.
- Run a synthesized BYOK panel through `/api/panel`.
- Forward attached screenshots as multimodal model inputs when supported by the
  selected provider.
- Parse model Markdown into editable normalized findings.
- Export normalized findings as `run.json`.
- Export the review brief as JSON, raw panel output as Markdown, and a
  repo-ready report as Markdown.
- Show provider, model, prompt, and image-count provenance in generated reports.
- Store a small local browser history without server persistence.
- Expose the request path in the interface: browser to `/api/panel` to provider.

## BYOK Requirements

The app follows a bring-your-own-key posture:

- no operator-funded default model in v0
- explicit user opt-in before model execution
- provider keys stored only in browser localStorage
- keys and selected screenshots sent to `/api/panel` only on `Run panel`
- no server-side persistence of keys, screenshots, or generated reports
- clear export path so users can keep artifacts in their own repo

Supported provider adapters:

- Anthropic
- OpenAI
- Google Gemini

## Product Direction

Near-term UI work should prioritize:

1. URL and prototype capture through a browser capture service.
2. Shared schema validation between web and CLI.
3. Stricter output contracts for Markdown-to-finding parsing.
4. Better import and repair flows for partially valid artifacts.
5. Optional hosted workspace mode only if repeated team usage requires it.
