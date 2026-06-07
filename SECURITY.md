# Security And Sensitive Data

Preflight UX handles product surfaces, screenshots, prompts, and generated model
output. Treat those artifacts as potentially sensitive unless they are clearly
public or explicitly permissioned for release.

## Do Not Commit

Do not commit:

- API keys, tokens, credentials, cookies, or private config
- private user data
- interview transcripts or research recordings
- analytics exports
- customer support tickets
- proprietary screenshots or unreleased product details
- private benchmark material without permission
- exploit details against live third-party systems

## BYOK Web App Posture

The web UI is designed for a bring-your-own-key workflow:

- provider keys are entered by the user
- keys are stored only in the user's browser localStorage
- keys and selected screenshots are sent to `/api/panel` only when the user runs
  a panel
- the serverless endpoint forwards the request to the selected provider
- the app should not log, persist, or echo keys

Changes to `api/panel.js`, `web/app.js`, or deployment configuration should
preserve that posture unless a change explicitly updates the security model and
documentation.

## Benchmark And Report Data

Public benchmark entries should use public sources or explicitly permissioned
material. If a source contains sensitive details, summarize only what is needed
for the issue class and link to the public artifact where possible.

Generated reports should be reviewed before publication. Panel output can expose
product strategy, roadmap assumptions, internal vocabulary, and critique of
unreleased work even when it contains no secrets.

## Reporting A Concern

If you find sensitive material, a credential leak, or a security issue, report it
privately to the project maintainers. Do not open a public issue that includes
secrets, private data, or reproduction steps for an active vulnerability.

For AI security issues such as prompt injection, data leakage, or unsafe
tool-use behavior:

- describe the impact and reproduction conditions at a safe level
- avoid publishing exploit payloads against live third-party systems
- coordinate privately with affected maintainers when appropriate
