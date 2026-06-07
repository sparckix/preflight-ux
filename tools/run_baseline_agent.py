#!/usr/bin/env python3
"""Run a Preflight UX baseline through subscription CLIs with API fallback.

Default runtime order is subscription-first:

    codex, claude, anthropic, openai, gemini

The runner updates a baseline `run.json` in place with normalized findings,
archives raw model text under ignored `internal/archive/`, and writes a redacted
trace receipt. It is intentionally not part of CI because it may use
subscription CLIs, network, or paid APIs.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RAW_OUTPUT_ROOT = ROOT / "internal" / "archive" / "raw-model-outputs"
SUBSCRIPTION_RUNTIMES = {"codex", "claude"}
API_RUNTIMES = {"anthropic", "openai", "gemini"}
DEFAULT_TRANSPORTS = ["codex", "claude", "anthropic", "openai", "gemini"]
SUBSCRIPTION_ERROR_PATTERNS = (
    "please run `codex login`",
    "codex login",
    "not logged in",
    "login required",
    "authentication",
    "quota",
    "rate limit",
    "usage limit",
)


@dataclass
class RuntimeResult:
    runtime: str
    model: str
    text: str
    stderr: str = ""
    command_preview: list[str] | None = None


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")


def baseline_source(kind: str) -> str:
    return "baseline-generic-critique" if kind == "generic-critique" else "baseline-heuristic-evaluation"


def build_task_prompt(run: dict[str, Any], prompt_text: str, taxonomy_text: str) -> str:
    source = baseline_source(str(run.get("baseline", {}).get("kind", "")))
    return f"""{prompt_text}

## Canonical Issue Taxonomy

{taxonomy_text}

## Output Contract

Return JSON only, with this exact shape:

{{
  "findings": [
    {{
      "id": "finding-001",
      "source": "{source}",
      "raw_finding": "...",
      "issue_class": "taxonomy-slug",
      "severity": "minor|moderate|severe",
      "confidence": "low|medium|high",
      "evidence": "surface evidence",
      "recommendation": "recommended change",
      "nearest_confuser": "alternative issue class or explanation",
      "validation_path": "how to validate",
      "stop_or_repair_rule": "when to drop, defer, or revise"
    }}
  ]
}}

Rules:
- Use at most eight findings.
- Do not include a finding without supplied surface evidence.
- Use source "{source}" for every finding.
- Use only taxonomy slugs for issue_class.
- Do not include hidden chain-of-thought.
"""


def subscription_env(runtime: str) -> dict[str, str]:
    env = dict(os.environ)
    if runtime == "codex":
        env.pop("OPENAI_API_KEY", None)
        env.pop("OPENAI_BASE_URL", None)
        env.pop("OPENAI_ORG_ID", None)
    elif runtime == "claude":
        env.pop("ANTHROPIC_API_KEY", None)
        env.pop("ANTHROPIC_AUTH_TOKEN", None)
        env.pop("CLAUDE_CODE_USE_BEDROCK", None)
        env.pop("CLAUDE_CODE_USE_VERTEX", None)
    return env


def build_subscription_command(runtime: str, prompt: str, repo: Path, codex_model: str) -> list[str]:
    if runtime == "codex":
        cmd = ["codex", "exec", "--skip-git-repo-check"]
        if codex_model not in {"", "default", "account-default", "account_default"}:
            cmd += ["--model", codex_model]
        cmd += ["--cd", str(repo), "--sandbox", "read-only", prompt]
        return cmd
    if runtime == "claude":
        cmd = [
            "claude",
            "--print",
            "--permission-mode",
            os.environ.get("PREFLIGHT_CLAUDE_PERMISSION_MODE", "acceptEdits"),
        ]
        for tool in ("Bash", "Read", "Glob", "Grep", "Edit", "Write", "WebFetch", "WebSearch"):
            cmd += ["--disallowedTools", tool]
        cmd += ["-p", prompt]
        return cmd
    raise ValueError(f"unsupported subscription runtime: {runtime}")


def run_subscription(runtime: str, prompt: str, timeout: int, codex_model: str) -> RuntimeResult:
    cmd = build_subscription_command(runtime, prompt, ROOT, codex_model)
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            env=subscription_env(runtime),
            text=True,
            capture_output=True,
            stdin=subprocess.DEVNULL,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"{runtime} subscription timed out after {timeout}s: {exc}") from exc
    combined = f"{proc.stdout or ''}\n{proc.stderr or ''}".strip()
    lowered = combined.lower()
    if proc.returncode != 0:
        raise RuntimeError(f"{runtime} subscription failed rc={proc.returncode}: {combined[:500]}")
    if any(pattern in lowered for pattern in SUBSCRIPTION_ERROR_PATTERNS):
        raise RuntimeError(f"{runtime} subscription auth/quota/rate failure: {combined[:500]}")
    if not (proc.stdout or "").strip():
        raise RuntimeError(f"{runtime} subscription returned empty stdout")
    preview = cmd[:-1] + ["<prompt>"]
    model = codex_model if runtime == "codex" else os.environ.get("PREFLIGHT_CLAUDE_MODEL", "subscription-default")
    return RuntimeResult(runtime=runtime, model=model, text=proc.stdout, stderr=proc.stderr or "", command_preview=preview)


def post_json(url: str, headers: dict[str, str], body: dict[str, Any], timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail[:500]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(str(exc)) from exc


def run_openai_api(prompt: str, timeout: int, model: str) -> RuntimeResult:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are Preflight UX baseline runner. Return JSON only."},
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
    }
    data = post_json(
        "https://api.openai.com/v1/chat/completions",
        {"content-type": "application/json", "authorization": f"Bearer {key}"},
        body,
        timeout,
    )
    return RuntimeResult("openai", model, data.get("choices", [{}])[0].get("message", {}).get("content", ""))


def run_anthropic_api(prompt: str, timeout: int, model: str) -> RuntimeResult:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")
    body = {
        "model": model,
        "max_tokens": 3000,
        "temperature": 0,
        "system": "You are Preflight UX baseline runner. Return strict JSON only.",
        "messages": [{"role": "user", "content": prompt}],
    }
    data = post_json(
        "https://api.anthropic.com/v1/messages",
        {"content-type": "application/json", "x-api-key": key, "anthropic-version": "2023-06-01"},
        body,
        timeout,
    )
    text = "".join(block.get("text", "") for block in data.get("content", []) if block.get("type") == "text")
    return RuntimeResult("anthropic", model, text)


def run_gemini_api(prompt: str, timeout: int, model: str) -> RuntimeResult:
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY or GOOGLE_API_KEY is not set")
    body = {
        "systemInstruction": {"parts": [{"text": "You are Preflight UX baseline runner. Return JSON only."}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0, "maxOutputTokens": 3000, "responseMimeType": "application/json"},
    }
    data = post_json(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
        {"content-type": "application/json"},
        body,
        timeout,
    )
    text = "".join(
        part.get("text", "")
        for candidate in data.get("candidates", [])
        for part in candidate.get("content", {}).get("parts", [])
    )
    return RuntimeResult("gemini", model, text)


def extract_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("no JSON object found")
    return json.loads(cleaned[start : end + 1])


def run_runtime(runtime: str, prompt: str, args: argparse.Namespace) -> RuntimeResult:
    if runtime == "codex":
        return run_subscription(runtime, prompt, args.timeout_seconds, args.codex_model)
    if runtime == "claude":
        return run_subscription(runtime, prompt, args.timeout_seconds, args.codex_model)
    if runtime == "anthropic":
        return run_anthropic_api(prompt, args.timeout_seconds, args.anthropic_model)
    if runtime == "openai":
        return run_openai_api(prompt, args.timeout_seconds, args.openai_model)
    if runtime == "gemini":
        return run_gemini_api(prompt, args.timeout_seconds, args.gemini_model)
    raise RuntimeError(f"unsupported runtime: {runtime}")


def update_run(run_path: Path, run: dict[str, Any], result: RuntimeResult, parsed: dict[str, Any]) -> None:
    run["model"] = {
        "provider": result.runtime,
        "name": result.model,
        "version": "",
        "temperature": 0,
    }
    run["findings"] = parsed.get("findings") if isinstance(parsed.get("findings"), list) else []
    run_path.write_text(json.dumps(run, indent=2) + "\n", encoding="utf-8")


def write_trace(run_dir: Path, run: dict[str, Any], result: RuntimeResult, parsed: dict[str, Any]) -> None:
    run_id = str(run.get("run_id") or run_dir.name)
    raw_dir = RAW_OUTPUT_ROOT / run_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_ref = raw_dir / "raw-output.json"
    raw_ref.write_text(result.text.strip() + "\n", encoding="utf-8")
    trace = {
        "schema": "preflight-baseline-agent-trace-v1",
        "run_id": run_id,
        "runtime": result.runtime,
        "model": result.model,
        "timestamp": int(time.time()),
        "command_preview": result.command_preview,
        "stderr_present": bool(result.stderr.strip()),
        "raw_output_archived": True,
        "raw_output_storage": "internal/archive/raw-model-outputs",
        "finding_count": len(parsed.get("findings", [])) if isinstance(parsed.get("findings"), list) else 0,
    }
    (run_dir / "agent-trace.json").write_text(json.dumps(trace, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def self_test() -> int:
    prompt = build_task_prompt(
        {"baseline": {"kind": "generic-critique"}},
        "Surface",
        "issue_classes:\n  - slug: empty-state-confusion\n",
    )
    assert "Return JSON only" in prompt
    codex = build_subscription_command("codex", "hi", ROOT, "default")
    assert codex[:3] == ["codex", "exec", "--skip-git-repo-check"]
    assert "--model" not in codex
    claude = build_subscription_command("claude", "hi", ROOT, "ignored")
    assert claude[:2] == ["claude", "--print"]
    parsed = extract_json_object("```json\n{\"findings\": []}\n```")
    assert parsed == {"findings": []}
    print("run_baseline_agent self-test PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", help="baseline run directory or run.json")
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
    if run.get("run_type") != "baseline":
        fail("run.json must have run_type: baseline")
    prompt_ref = run.get("baseline", {}).get("prompt_ref")
    if not prompt_ref:
        fail("baseline.prompt_ref is required")
    prompt_path = ROOT / prompt_ref
    prompt = build_task_prompt(
        run,
        prompt_path.read_text(encoding="utf-8"),
        (ROOT / "taxonomy" / "issue-classes.yaml").read_text(encoding="utf-8"),
    )

    errors: list[str] = []
    transports = [item.strip() for item in args.transports.split(",") if item.strip()]
    for runtime in transports:
        try:
            result = run_runtime(runtime, prompt, args)
            parsed = extract_json_object(result.text)
            update_run(run_path, run, result, parsed)
            write_trace(run_dir, run, result, parsed)
            print(f"Wrote {len(run.get('findings', []))} findings via {runtime} to {run_path.relative_to(ROOT)}")
            return 0
        except Exception as exc:  # noqa: BLE001 - this is a fallback runner.
            errors.append(f"{runtime}: {exc}")
            continue
    fail("all runtimes failed:\n" + "\n".join(f"- {item}" for item in errors))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
