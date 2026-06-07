#!/usr/bin/env python3
"""Run a Preflight UX panel through subscription CLIs with API fallback."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

from run_baseline_agent import DEFAULT_TRANSPORTS, RuntimeResult, extract_json_object, run_runtime


ROOT = Path(__file__).resolve().parents[1]
RAW_OUTPUT_ROOT = ROOT / "internal" / "archive" / "raw-model-outputs"
PERSONA_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")


def persona_path(persona_id: str) -> Path:
    for base in (ROOT / "personas" / "ux-experts", ROOT / "personas" / "user-types"):
        path = base / f"{persona_id}.md"
        if path.exists():
            return path
    fail(f"persona not found: {persona_id}")


def persona_type(persona_text: str) -> str:
    match = re.search(r"^type:\s*([a-z-]+)\s*$", persona_text, re.MULTILINE)
    return match.group(1) if match else "user-type"


def prompt_template_for(persona_text: str) -> str:
    if persona_type(persona_text) == "ux-expert":
        return (ROOT / "prompts" / "expert-persona-review.v0.2.md").read_text(encoding="utf-8")
    return (ROOT / "prompts" / "user-type-review.v0.2.md").read_text(encoding="utf-8")


def build_persona_prompt(run: dict[str, Any], persona_id: str, persona_text: str) -> str:
    surface_ref = run["surface"]["ref"]
    surface_path = ROOT / surface_ref
    product_dir = surface_path.parent if surface_path.name == "surface.md" else surface_path
    description_path = product_dir / "description.md"
    product_description = description_path.read_text(encoding="utf-8") if description_path.exists() else ""
    surface_text = surface_path.read_text(encoding="utf-8")
    taxonomy_text = (ROOT / "taxonomy" / "issue-classes.yaml").read_text(encoding="utf-8")
    template = prompt_template_for(persona_text)
    return f"""{template}

## Persona Definition

{persona_text.strip()}

## Product Description

{product_description.strip() or "(No separate product description supplied.)"}

## Product Surface

{surface_text.strip()}

## Canonical Issue Taxonomy

{taxonomy_text.strip()}

## Machine Output Contract

Return JSON only, with this exact shape:

{{
  "findings": [
    {{
      "id": "finding-001",
      "persona": "{persona_id}",
      "raw_finding": "One concise product-risk hypothesis",
      "issue_class": "taxonomy-slug",
      "severity": "minor|moderate|severe",
      "confidence": "low|medium|high",
      "evidence": "Surface evidence",
      "recommendation": "Recommended change"
    }}
  ],
  "tradeoffs": [],
  "likely_misses": [],
  "abstentions": []
}}

Rules:
- Use at most four findings for this persona.
- Do not include a finding without supplied surface evidence.
- Use persona "{persona_id}" for every finding.
- Use only taxonomy slugs for issue_class.
- Separate the mechanism, downstream task blocker, and inclusion impact when
  the surface supports all three.
- Use `identity-verification-friction` for failure to prove identity.
- Use `service-unavailable-blocker` for inability to access the downstream
  service or complete the primary public-service task after verification fails.
- Use `vulnerable-user-access-barrier` for disproportionate access impact on
  users with higher support needs or fewer fallback options.
- Avoid broad adjacent classes when a narrower public-service access class
  fits the supplied evidence.
- Do not include hidden chain-of-thought.
"""


def normalize_findings(persona_id: str, parsed: dict[str, Any], next_index: int) -> tuple[list[dict[str, Any]], int]:
    findings = parsed.get("findings") if isinstance(parsed.get("findings"), list) else []
    normalized: list[dict[str, Any]] = []
    for item in findings:
        if not isinstance(item, dict):
            continue
        issue_class = str(item.get("issue_class", "")).strip()
        if not PERSONA_RE.fullmatch(issue_class):
            continue
        finding = {
            "id": f"finding-{next_index:03d}",
            "persona": persona_id,
            "raw_finding": str(item.get("raw_finding", "")).strip(),
            "issue_class": issue_class,
            "severity": str(item.get("severity", "")).strip(),
            "confidence": str(item.get("confidence", "")).strip(),
            "evidence": str(item.get("evidence", "")).strip(),
            "recommendation": str(item.get("recommendation", "")).strip(),
        }
        if (
            finding["raw_finding"]
            and finding["severity"] in {"minor", "moderate", "severe"}
            and finding["confidence"] in {"low", "medium", "high"}
        ):
            normalized.append(finding)
            next_index += 1
    return normalized, next_index


def write_artifacts(run_dir: Path, persona_id: str, result: RuntimeResult, parsed: dict[str, Any]) -> None:
    run_id = run_dir.name
    raw_dir = RAW_OUTPUT_ROOT / run_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_ref = raw_dir / f"raw-{persona_id}.json"
    raw_ref.write_text(result.text.strip() + "\n", encoding="utf-8")
    trace_path = run_dir / "panel-agent-trace.json"
    if trace_path.exists():
        trace = read_json(trace_path)
    else:
        trace = {"schema": "preflight-panel-agent-trace-v1", "personas": []}
    trace["personas"].append(
        {
            "persona": persona_id,
            "runtime": result.runtime,
            "model": result.model,
            "timestamp": int(time.time()),
            "command_preview": result.command_preview,
            "stderr_present": bool(result.stderr.strip()),
            "finding_count": len(parsed.get("findings", [])) if isinstance(parsed.get("findings"), list) else 0,
            "raw_output_archived": True,
            "raw_output_storage": "internal/archive/raw-model-outputs",
        }
    )
    trace_path.write_text(json.dumps(trace, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def self_test() -> int:
    prompt = build_persona_prompt(
        {
            "surface": {"ref": "benchmark/products/govuk-verify-2016/surface.md"},
        },
        "tom-random-visitor",
        persona_path("tom-random-visitor").read_text(encoding="utf-8"),
    )
    assert "Return JSON only" in prompt
    assert '"persona": "tom-random-visitor"' in prompt
    findings, index = normalize_findings(
        "tom-random-visitor",
        {
            "findings": [
                {
                    "raw_finding": "Risk",
                    "issue_class": "service-unavailable-blocker",
                    "severity": "severe",
                    "confidence": "high",
                    "evidence": "Surface",
                    "recommendation": "Fix",
                }
            ]
        },
        1,
    )
    assert len(findings) == 1
    assert findings[0]["id"] == "finding-001"
    assert index == 2
    print("run_panel_agent self-test PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", help="panel run directory or run.json")
    parser.add_argument("--personas", help="comma-separated subset; defaults to run personas")
    parser.add_argument("--transports", default=",".join(DEFAULT_TRANSPORTS))
    parser.add_argument("--timeout-seconds", type=int, default=300)
    parser.add_argument("--codex-model", default=os.environ.get("PREFLIGHT_CODEX_MODEL", "default"))
    parser.add_argument("--anthropic-model", default=os.environ.get("PREFLIGHT_ANTHROPIC_MODEL", "claude-sonnet-4-6"))
    parser.add_argument("--openai-model", default=os.environ.get("PREFLIGHT_OPENAI_MODEL", "gpt-5.2"))
    parser.add_argument("--gemini-model", default=os.environ.get("PREFLIGHT_GEMINI_MODEL", "gemini-2.5-pro"))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.run:
        fail("--run is required")

    run_arg = Path(args.run)
    run_path = run_arg / "run.json" if run_arg.is_dir() else run_arg
    if not run_path.is_absolute():
        run_path = ROOT / run_path
    run_dir = run_path.parent
    run = read_json(run_path)
    if run.get("run_type", "panel") != "panel":
        fail("run.json must be a panel run")

    personas = [item.strip() for item in (args.personas or ",".join(run.get("personas", []))).split(",") if item.strip()]
    if not personas:
        fail("no personas supplied")

    run["findings"] = []
    run["prompt_version"] = "panel-action-card-v0.3"
    trace_path = run_dir / "panel-agent-trace.json"
    if trace_path.exists():
        trace_path.unlink()
    next_index = 1
    for persona_id in personas:
        persona_text = persona_path(persona_id).read_text(encoding="utf-8")
        prompt = build_persona_prompt(run, persona_id, persona_text)
        errors: list[str] = []
        for runtime in [item.strip() for item in args.transports.split(",") if item.strip()]:
            try:
                result = run_runtime(runtime, prompt, args)
                parsed = extract_json_object(result.text)
                findings, next_index = normalize_findings(persona_id, parsed, next_index)
                run["findings"].extend(findings)
                write_artifacts(run_dir, persona_id, result, parsed)
                print(f"Wrote {len(findings)} findings for {persona_id} via {runtime}")
                break
            except Exception as exc:  # noqa: BLE001 - this is a fallback runner.
                errors.append(f"{runtime}: {exc}")
                continue
        else:
            fail(f"all runtimes failed for {persona_id}:\n" + "\n".join(f"- {item}" for item in errors))

    run["model"] = {"provider": "mixed", "name": "subscription-or-api-panel", "version": "", "temperature": 0}
    run_path.write_text(json.dumps(run, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(run['findings'])} panel findings to {run_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
