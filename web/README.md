# Product UI

Preflight UX includes a deployable web surface for product teams.

## What the UI does now

- captures a product brief and surface description
- accepts prototype/live URLs
- accepts local PNG, JPG, and WebP screenshot uploads for visual review
- imports prior review brief JSON or `run.json` artifacts
- selects the default persona panel or a subset
- selects issue-class focus areas
- generates and validates a structured review brief
- forwards attached screenshots as multimodal model inputs when supported
- runs a synthesized BYOK panel through `/api/panel`
- parses model Markdown into editable normalized findings
- exports normalized findings as `run.json`
- exports the review brief as JSON, raw panel output as Markdown, and a repo-ready report as Markdown
- shows provider/model/prompt provenance in generated reports
- stores a small local browser history without server persistence
- ships a public example workflow page at `/example`
- stores provider keys only in the user's browser localStorage
- exposes the request path in the interface: browser to `/api/panel` to provider

## BYOK posture

The app follows a strict BYOK posture:

- no operator-funded default model in v0
- user explicitly enables BYOK
- key is stored on the user's device in localStorage
- key and selected screenshots are sent to `/api/panel` only when the user clicks `Run panel`
- the serverless function forwards the request to the selected provider
- the app does not log or persist keys

Supported providers:

- Anthropic
- OpenAI
- Google Gemini

## Product direction

Near-term product work should prioritize:

1. adding real URL/prototype capture through a browser capture service
2. sharing validation logic between web and CLI from one schema source
3. improving Markdown-to-finding parsing with stricter model output contracts
4. adding an optional hosted workspace mode if repeated team usage appears
5. adding browser-based visual snapshots when Playwright work is no longer deferred
