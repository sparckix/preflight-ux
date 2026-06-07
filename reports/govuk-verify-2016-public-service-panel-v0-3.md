# Preflight UX Panel Report: govuk-verify-2016-public-service-panel-v0-3

## Summary

Surface: `benchmark/products/govuk-verify-2016/surface.md`.
Run date: `2026-06-06`.
Run type: `panel`.
Model: `mixed/subscription-or-api-panel`.
Prompt version: `panel-action-card-v0.3`.
Calibration status: `not populated`.

This report is generated from normalized panel findings. It is a product-risk artifact, not validated user research.

## Top Risks

| Priority | Issue class | Source | Severity | Confidence | Recommended action |
|---|---|---|---|---|---|
| P0 | `account-before-value` | `tom-random-visitor` | severe | high | Before provider selection, show a concrete preview of the exact downstream access benefit, required documents, expected time, and fallback routes so users understand the value and cost before committing sensitive information. |
| P0 | `identity-verification-friction` | `aisha-policy-researcher` | severe | high | Add clearer provider-fit guidance, pre-check eligibility signals, and a visible fallback route before users commit sensitive identity information. |
| P0 | `identity-verification-friction` | `jamie-accessibility` | severe | high | Provide accessible alternative verification routes, clear failure recovery, and a non-dead-end path back to the public service when provider selection or proofing fails. |
| P0 | `identity-verification-friction` | `sara-ux-researcher` | severe | high | Reduce provider-choice burden, explain eligibility and evidence requirements before commitment, and provide clear alternative verification routes when a provider path fails. |
| P0 | `identity-verification-friction` | `tom-random-visitor` | severe | high | Add an eligibility triage step before provider choice, explain why each provider is recommended, expose document requirements up front, and provide a clear non-digital or assisted route when no provider is likely to work. |
| P0 | `service-unavailable-blocker` | `aisha-policy-researcher` | severe | high | Provide a non-digital or assisted route when verification fails, and make return-to-service recovery explicit rather than leaving the user stranded in the identity layer. |
| P0 | `service-unavailable-blocker` | `jamie-accessibility` | severe | medium | Treat verification failure as a service-access blocker: preserve the user’s task context, offer assisted routes, and guarantee a fallback path for accessing the downstream service. |
| P0 | `service-unavailable-blocker` | `sara-ux-researcher` | severe | high | Treat failed verification as a recoverable service-access state with visible next steps, alternative channels, and continuity back to the original government service. |
| P0 | `service-unavailable-blocker` | `tom-random-visitor` | severe | high | Make failed verification recoverable inside the service journey with saved progress, explicit retry paths, direct assisted support, and a way to continue through an alternative identity route without restarting. |
| P0 | `vulnerable-user-access-barrier` | `aisha-policy-researcher` | severe | high | Design and measure fallback support specifically for benefits-related and higher-support users, with parity targets for completion and service access. |
| P0 | `vulnerable-user-access-barrier` | `jamie-accessibility` | severe | high | Design and validate assisted digital support, inclusive identity evidence options, and fallback channels specifically for benefits-related and vulnerable users before requiring digital verification. |
| P0 | `vulnerable-user-access-barrier` | `sara-ux-researcher` | severe | high | Design assisted digital, non-digital, and delegated-support paths as first-class routes rather than exceptions, and monitor completion by user group and service type. |
| P0 | `vulnerable-user-access-barrier` | `tom-random-visitor` | severe | high | Treat assisted access as a core path rather than an exception: publish accessible fallback options before verification begins, route failed users to human support, and monitor completion by service type and support need. |
| P1 | `account-before-value` | `aisha-policy-researcher` | moderate | medium | Explain why a third-party provider is required, what data is shared, what success depends on, and what alternatives exist before provider selection. |
| P1 | `information-architecture-overload` | `sara-ux-researcher` | moderate | medium | Preserve the user's mental model by framing provider choice around concrete fit, required documents, completion likelihood, and recovery options, not just a list of certified companies. |

## Structured Findings

### finding-012: `account-before-value`

- Source: `tom-random-visitor`
- Severity: `severe`
- Confidence: `high`
- Predicted behavior: A first-time visitor would likely experience the Verify handoff as commitment before visible value because identity proofing is required before service access.
- Evidence: Users attempting to access participating government services were routed through GOV.UK Verify, then had to select a provider, supply identity information, and complete verification before returning to the government service.
- Recommendation: Before provider selection, show a concrete preview of the exact downstream access benefit, required documents, expected time, and fallback routes so users understand the value and cost before committing sensitive information.

### finding-008: `identity-verification-friction`

- Source: `aisha-policy-researcher`
- Severity: `severe`
- Confidence: `high`
- Predicted behavior: A cautious policy researcher would likely treat provider selection plus identity proofing as a high-friction gate that can fail before the public-service task begins.
- Evidence: The surface says users were routed through GOV.UK Verify, had to select a provider, supply identity information, and could fail during provider selection or identity proofing.
- Recommendation: Add clearer provider-fit guidance, pre-check eligibility signals, and a visible fallback route before users commit sensitive identity information.

### finding-005: `identity-verification-friction`

- Source: `jamie-accessibility`
- Severity: `severe`
- Confidence: `high`
- Predicted behavior: The verification mechanism itself created a high-stakes access failure for users who could not complete provider selection or identity proofing.
- Evidence: The surface says users were routed through GOV.UK Verify, had to select a provider and complete identity proofing, and could fail during provider selection or identity proofing.
- Recommendation: Provide accessible alternative verification routes, clear failure recovery, and a non-dead-end path back to the public service when provider selection or proofing fails.

### finding-001: `identity-verification-friction`

- Source: `sara-ux-researcher`
- Severity: `severe`
- Confidence: `high`
- Predicted behavior: Provider selection and identity proofing created a high-friction verification step that could prevent eligible users from proving identity.
- Evidence: The surface says users had to select a certified provider, supply identity information, and could fail during provider selection or identity proofing.
- Recommendation: Reduce provider-choice burden, explain eligibility and evidence requirements before commitment, and provide clear alternative verification routes when a provider path fails.

### finding-013: `identity-verification-friction`

- Source: `tom-random-visitor`
- Severity: `severe`
- Confidence: `high`
- Predicted behavior: Provider selection and identity proofing would likely become the main abandonment point for users who cannot quickly tell which path will work for them.
- Evidence: The surface reports that users could fail during provider selection or identity proofing, and completion rates were below original expectations.
- Recommendation: Add an eligibility triage step before provider choice, explain why each provider is recommended, expose document requirements up front, and provide a clear non-digital or assisted route when no provider is likely to work.

### finding-009: `service-unavailable-blocker`

- Source: `aisha-policy-researcher`
- Severity: `severe`
- Confidence: `high`
- Predicted behavior: Failure inside Verify would likely be experienced as inability to reach the downstream public service, not merely as an identity-product problem.
- Evidence: Verify mediated access to downstream public services, and completion and service-access rates were below original expectations.
- Recommendation: Provide a non-digital or assisted route when verification fails, and make return-to-service recovery explicit rather than leaving the user stranded in the identity layer.

### finding-006: `service-unavailable-blocker`

- Source: `jamie-accessibility`
- Severity: `severe`
- Confidence: `medium`
- Predicted behavior: Because Verify mediated access to downstream public services, verification failure could block completion of the primary public-service task.
- Evidence: The surface says Verify mediated access to downstream public services and that completion and service-access rates were below original expectations.
- Recommendation: Treat verification failure as a service-access blocker: preserve the user’s task context, offer assisted routes, and guarantee a fallback path for accessing the downstream service.

### finding-002: `service-unavailable-blocker`

- Source: `sara-ux-researcher`
- Severity: `severe`
- Confidence: `high`
- Predicted behavior: Because Verify mediated access to downstream public services, verification failure became a blocker to the primary public-service task.
- Evidence: The surface says Verify mediated access to participating government services and that completion and service-access rates were below original expectations.
- Recommendation: Treat failed verification as a recoverable service-access state with visible next steps, alternative channels, and continuity back to the original government service.

### finding-014: `service-unavailable-blocker`

- Source: `tom-random-visitor`
- Severity: `severe`
- Confidence: `high`
- Predicted behavior: Verification failure would likely block the actual public-service task, not just the identity step.
- Evidence: Verify mediated access to downstream public services, users had to complete verification before returning to the government service, and service-access rates were below expectations.
- Recommendation: Make failed verification recoverable inside the service journey with saved progress, explicit retry paths, direct assisted support, and a way to continue through an alternative identity route without restarting.

### finding-010: `vulnerable-user-access-barrier`

- Source: `aisha-policy-researcher`
- Severity: `severe`
- Confidence: `high`
- Predicted behavior: The flow would likely raise inclusion risk because vulnerable or benefits-related users were among those affected by the access barrier.
- Evidence: The surface states that vulnerable or benefits-related users were among those affected, in a high-stakes public-service access case.
- Recommendation: Design and measure fallback support specifically for benefits-related and higher-support users, with parity targets for completion and service access.

### finding-007: `vulnerable-user-access-barrier`

- Source: `jamie-accessibility`
- Severity: `severe`
- Confidence: `high`
- Predicted behavior: The flow likely created an inclusion barrier for users with higher support needs or fewer fallback options.
- Evidence: The surface explicitly says vulnerable or benefits-related users were among those affected in a high-stakes identity and public-service access case.
- Recommendation: Design and validate assisted digital support, inclusive identity evidence options, and fallback channels specifically for benefits-related and vulnerable users before requiring digital verification.

### finding-003: `vulnerable-user-access-barrier`

- Source: `sara-ux-researcher`
- Severity: `severe`
- Confidence: `high`
- Predicted behavior: The flow likely imposed unequal access costs on users with higher support needs or fewer fallback options.
- Evidence: The surface explicitly states that vulnerable or benefits-related users were among those affected in a high-stakes public-service access case.
- Recommendation: Design assisted digital, non-digital, and delegated-support paths as first-class routes rather than exceptions, and monitor completion by user group and service type.

### finding-015: `vulnerable-user-access-barrier`

- Source: `tom-random-visitor`
- Severity: `severe`
- Confidence: `high`
- Predicted behavior: The flow would likely create disproportionate access risk for users with higher support needs or fewer fallback options.
- Evidence: The product surface states that vulnerable or benefits-related users were among those affected, and the case is a high-stakes identity and public-service access flow.
- Recommendation: Treat assisted access as a core path rather than an exception: publish accessible fallback options before verification begins, route failed users to human support, and monitor completion by service type and support need.

### finding-011: `account-before-value`

- Source: `aisha-policy-researcher`
- Severity: `moderate`
- Confidence: `medium`
- Predicted behavior: The need to choose a certified company before completing a government-service task would likely create early commitment friction and uncertainty about whether the route is appropriate.
- Evidence: The flow required users to select a provider and supply identity information before returning to the government service.
- Recommendation: Explain why a third-party provider is required, what data is shared, what success depends on, and what alternatives exist before provider selection.

### finding-004: `information-architecture-overload`

- Source: `sara-ux-researcher`
- Severity: `moderate`
- Confidence: `medium`
- Predicted behavior: Selecting among certified identity providers may have added cognitive load at the moment users expected to access a government service.
- Evidence: The flow routed users from a government service into a provider-selection step before identity proofing and return to the original service.
- Recommendation: Preserve the user's mental model by framing provider choice around concrete fit, required documents, completion likelihood, and recovery options, not just a list of certified companies.

## Confidence and Uncertainty

- Calibration status: not populated unless this run has been scored against benchmark ground truth.
- Treat findings as pre-ship hypotheses until validated by user behavior, telemetry, support data, or scorer review.

## Validation Plan

- Compare findings against `benchmark/products/<slug>/known-issues.yaml` when this is a benchmark run.
- Record hits, misses, and false positives in `calibration/`.
- Promote findings only after human scorer review.

