"""Command line tools for the Preflight UX repo."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Sequence


SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
BASELINE_KINDS = {"generic-critique", "heuristic-evaluation"}


def find_repo_root(start: Path | None = None) -> Path:
    """Find the repo root containing the validator and benchmark tree."""
    search_from = (start or Path.cwd()).resolve()
    candidates = [search_from, *search_from.parents, Path(__file__).resolve().parents[1]]
    for candidate in candidates:
        if (candidate / "tools" / "validate_repo.py").is_file() and (
            candidate / "benchmark" / "products" / "_template"
        ).is_dir():
            return candidate
    raise RuntimeError("could not find repo root; run this command from the Preflight UX checkout")


def cmd_validate(_args: argparse.Namespace) -> int:
    root = find_repo_root()
    validator = root / "tools" / "validate_repo.py"
    return subprocess.call([sys.executable, str(validator)], cwd=root)


def validate_review_brief(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("artifact_type") != "preflight_ux_review_brief":
        errors.append("artifact_type must be preflight_ux_review_brief")
    if not SLUG_RE.fullmatch(str(data.get("run_id", ""))):
        errors.append("run_id must be a lowercase slug")
    product = data.get("product") if isinstance(data.get("product"), dict) else {}
    if not str(product.get("name", "")).strip():
        errors.append("product.name is required")
    if product.get("stage") not in {"pre-ship", "prototype", "redesign", "post-launch"}:
        errors.append("product.stage is invalid")
    if product.get("surface_type") not in {"benchmark", "url", "screenshot", "spec", "prototype", "pr"}:
        errors.append("product.surface_type is invalid")
    screenshots = (data.get("attachments") or {}).get("screenshots", []) if isinstance(data.get("attachments"), dict) else []
    if not str(product.get("surface", "")).strip() and not str(product.get("prototype_url", "")).strip() and not screenshots:
        errors.append("provide product.surface, product.prototype_url, or at least one screenshot")
    if len(screenshots) > 3:
        errors.append("attachments.screenshots may contain at most 3 screenshots")
    for index, shot in enumerate(screenshots, 1):
        if shot.get("mime_type") not in {"image/png", "image/jpeg", "image/webp"}:
            errors.append(f"screenshot {index} mime_type is invalid")
        if int(shot.get("size_bytes") or 0) > 1800000:
            errors.append(f"screenshot {index} exceeds 1.8 MB")
    review = data.get("review") if isinstance(data.get("review"), dict) else {}
    if review.get("depth") not in {"fast", "deep"}:
        errors.append("review.depth must be fast or deep")
    if review.get("synthesis_mode") not in {"prioritized", "disagreement", "adversarial"}:
        errors.append("review.synthesis_mode is invalid")
    panel = data.get("panel") if isinstance(data.get("panel"), dict) else {}
    if not panel.get("personas"):
        errors.append("panel.personas must not be empty")
    if not panel.get("risk_focus"):
        errors.append("panel.risk_focus must not be empty")
    return errors


def validate_run_data(data: dict, label: str = "run") -> list[str]:
    errors: list[str] = []
    required = {"run_id", "surface", "model", "prompt_version", "date", "personas", "findings"}
    missing = sorted(required - set(data))
    if missing:
        errors.append(f"{label} missing required keys: {missing}")
        return errors

    if not SLUG_RE.fullmatch(str(data.get("run_id", ""))):
        errors.append("run_id must be a lowercase slug")

    run_type = data.get("run_type", "panel")
    if run_type not in {"panel", "baseline"}:
        errors.append("run_type must be panel or baseline")
    if run_type == "panel" and not data.get("personas"):
        errors.append("panel run must include at least one persona")
    if run_type == "baseline":
        baseline = data.get("baseline") if isinstance(data.get("baseline"), dict) else {}
        if baseline.get("kind") not in BASELINE_KINDS:
            errors.append("baseline.kind is invalid")
        if not str(baseline.get("prompt_ref", "")).strip():
            errors.append("baseline.prompt_ref is required")

    for index, finding in enumerate(data.get("findings", []), 1):
        for key in ["id", "raw_finding", "issue_class", "severity", "confidence"]:
            if key not in finding:
                errors.append(f"finding {index} missing key: {key}")
        if "persona" not in finding and "source" not in finding:
            errors.append(f"finding {index} must include persona or source")
        if finding.get("severity") not in {"minor", "moderate", "severe"}:
            errors.append(f"finding {index} severity is invalid")
        if finding.get("confidence") not in {"low", "medium", "high"}:
            errors.append(f"finding {index} confidence is invalid")
    return errors


def cmd_validate_artifact(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.exists():
        print(f"error: artifact path does not exist: {path}", file=sys.stderr)
        return 1
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in {path}: {exc}", file=sys.stderr)
        return 1

    if args.type == "review-brief":
        errors = validate_review_brief(data)
    elif args.type == "panel-run":
        errors = validate_run_data(data, str(path))
    else:
        raise RuntimeError(f"unsupported artifact type: {args.type}")

    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"OK: {args.type} artifact is valid: {path}")
    return 0


def update_meta_slug(meta_path: Path, slug: str) -> None:
    text = meta_path.read_text(encoding="utf-8")
    updated, count = re.subn(r"^slug:\s*.*$", f"slug: {slug}", text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise RuntimeError(f"{meta_path} does not contain exactly one slug field")
    meta_path.write_text(updated, encoding="utf-8")


def cmd_new_benchmark(args: argparse.Namespace) -> int:
    slug = args.slug
    if not SLUG_RE.fullmatch(slug):
        print("error: slug must use lowercase letters, numbers, and single hyphens", file=sys.stderr)
        return 2

    root = find_repo_root()
    template = root / "benchmark" / "products" / "_template"
    target = root / "benchmark" / "products" / slug
    if target.exists():
        print(f"error: benchmark already exists: {target.relative_to(root)}", file=sys.stderr)
        return 1

    shutil.copytree(template, target)
    update_meta_slug(target / "meta.yaml", slug)
    print(f"Created benchmark scaffold at {target.relative_to(root)}")
    return 0


def parse_simple_yaml_fields(path: Path, keys: set[str]) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    data: dict[str, str] = {}
    for key in keys:
        match = re.search(rf"^{re.escape(key)}:\s*(.+)$", text, re.MULTILINE)
        if match:
            data[key] = match.group(1).strip().strip('"')
    return data


def cmd_benchmark_status(_args: argparse.Namespace) -> int:
    root = find_repo_root()
    products_root = root / "benchmark" / "products"
    runs = []
    for path in sorted((root / "runs").glob("*/run.json")):
        try:
            runs.append(load_run(path))
        except RuntimeError:
            continue
    scores = []
    for path in sorted((root / "calibration").glob("*.score.json")):
        try:
            scores.append(load_score(path))
        except RuntimeError:
            continue

    lines = [
        "| Benchmark | Status | Source quality | Runs | Scores |",
        "|---|---|---|---:|---:|",
    ]
    for product_dir in sorted(path for path in products_root.iterdir() if path.is_dir() and path.name != "_template"):
        fields = parse_simple_yaml_fields(product_dir / "meta.yaml", {"benchmark_status", "source_quality"})
        refs = {str(product_dir.relative_to(root)), str(product_dir.relative_to(root) / "surface.md")}
        run_count = sum(1 for run in runs if run.get("surface", {}).get("ref") in refs)
        score_count = sum(1 for score in scores if score.get("surface") in refs)
        lines.append(
            f"| `{product_dir.name}` | "
            f"{fields.get('benchmark_status', '-')} | "
            f"{fields.get('source_quality', '-')} | "
            f"{run_count} | "
            f"{score_count} |"
        )
    print("\n".join(lines))
    return 0


def read_panel_personas(panel_path: Path) -> list[str]:
    text = panel_path.read_text(encoding="utf-8")
    personas: list[str] = []
    in_personas = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "personas:":
            in_personas = True
            continue
        if in_personas and stripped and not line.startswith((" ", "-")):
            break
        if in_personas:
            match = re.match(r"^\s+-\s+([a-z0-9]+(?:-[a-z0-9]+)*)$", line)
            if match:
                personas.append(match.group(1))
    if not personas:
        raise RuntimeError(f"no personas found in panel file: {panel_path}")
    return personas


def slug_from_path(path: Path) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", path.stem.lower()).strip("-")
    return slug or "surface"


def cmd_run(args: argparse.Namespace) -> int:
    root = find_repo_root()
    surface_path = Path(args.surface)
    if not surface_path.is_absolute():
        surface_path = root / surface_path
    if not surface_path.exists():
        print(f"error: surface path does not exist: {surface_path}", file=sys.stderr)
        return 1

    panel_path = Path(args.panel)
    if not panel_path.is_absolute():
        panel_path = root / panel_path
    if not panel_path.exists():
        print(f"error: panel path does not exist: {panel_path}", file=sys.stderr)
        return 1

    run_id = args.run_id or f"{slug_from_path(surface_path)}-{date.today().isoformat()}"
    run_id = run_id.replace("_", "-")
    if not SLUG_RE.fullmatch(run_id):
        print("error: run id must use lowercase letters, numbers, and single hyphens", file=sys.stderr)
        return 2

    out_dir = Path(args.out or root / "runs" / run_id)
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    if out_dir.exists() and not args.force:
        print(f"error: output directory already exists: {out_dir.relative_to(root)}", file=sys.stderr)
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        surface_ref = str(surface_path.relative_to(root))
    except ValueError:
        surface_ref = str(surface_path)

    run = {
        "run_type": "panel",
        "run_id": run_id,
        "surface": {"type": args.surface_type, "ref": surface_ref, "hash": ""},
        "model": {
            "provider": args.model_provider,
            "name": args.model,
            "version": args.model_version,
            "temperature": args.temperature,
        },
        "prompt_version": args.prompt_version,
        "date": date.today().isoformat(),
        "personas": read_panel_personas(panel_path),
        "findings": [],
    }
    run_path = out_dir / "run.json"
    run_path.write_text(json.dumps(run, indent=2) + "\n", encoding="utf-8")
    try:
        display_path = run_path.relative_to(root)
    except ValueError:
        display_path = run_path
    print(f"Wrote run scaffold to {display_path}")
    print("Add normalized findings, then run `uxpanel report --run ...`.")
    return 0


def baseline_prompt(kind: str, surface_text: str) -> str:
    if kind == "generic-critique":
        instruction = """You are reviewing a product surface before launch.

Find concrete UX risks that a product team can act on before users encounter
them. Use only the supplied surface. Do not claim user behavior as fact. Return
findings as product-risk hypotheses with issue-class suggestions when possible.

Return:
1. Top risks
2. Evidence from the surface
3. Recommended changes
4. Likely false positives or uncertainty
"""
    elif kind == "heuristic-evaluation":
        instruction = """You are conducting a heuristic UX evaluation of a product
surface before launch.

Review the surface against: visibility of system status, match to user
expectations, user control and freedom, consistency, error prevention,
recognition over recall, efficient workflows, accessibility basics, trust and
provenance, and recovery from failure. Use only the supplied surface. Return
findings as product-risk hypotheses with issue-class suggestions when possible.

Return:
1. Heuristic violations
2. Evidence from the surface
3. Recommended changes
4. Likely false positives or uncertainty
"""
    else:
        raise RuntimeError(f"unsupported baseline kind: {kind}")
    return f"{instruction}\n\n## Product Surface\n\n{surface_text.strip()}\n"


def cmd_baseline(args: argparse.Namespace) -> int:
    root = find_repo_root()
    surface_path = Path(args.surface)
    if not surface_path.is_absolute():
        surface_path = root / surface_path
    if not surface_path.exists():
        print(f"error: surface path does not exist: {surface_path}", file=sys.stderr)
        return 1

    run_id = args.run_id or f"{slug_from_path(surface_path)}-{args.kind}-{date.today().isoformat()}"
    run_id = run_id.replace("_", "-")
    if not SLUG_RE.fullmatch(run_id):
        print("error: run id must use lowercase letters, numbers, and single hyphens", file=sys.stderr)
        return 2

    out_dir = Path(args.out or root / "runs" / run_id)
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    if out_dir.exists() and not args.force:
        print(f"error: output directory already exists: {out_dir.relative_to(root)}", file=sys.stderr)
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        surface_ref = str(surface_path.relative_to(root))
    except ValueError:
        surface_ref = str(surface_path)

    prompt_path = out_dir / "baseline-prompt.md"
    prompt_path.write_text(baseline_prompt(args.kind, surface_path.read_text(encoding="utf-8")), encoding="utf-8")
    try:
        prompt_ref = str(prompt_path.relative_to(root))
    except ValueError:
        prompt_ref = str(prompt_path)

    run = {
        "run_type": "baseline",
        "run_id": run_id,
        "surface": {"type": args.surface_type, "ref": surface_ref, "hash": ""},
        "model": {
            "provider": args.model_provider,
            "name": args.model,
            "version": args.model_version,
            "temperature": args.temperature,
        },
        "prompt_version": f"baseline-{args.kind}-v0.2",
        "date": date.today().isoformat(),
        "personas": [],
        "baseline": {"kind": args.kind, "prompt_ref": prompt_ref},
        "findings": [],
    }
    run_path = out_dir / "run.json"
    run_path.write_text(json.dumps(run, indent=2) + "\n", encoding="utf-8")
    try:
        display_path = run_path.relative_to(root)
    except ValueError:
        display_path = run_path
    print(f"Wrote {args.kind} baseline scaffold to {display_path}")
    print(f"Prompt written to {prompt_ref}")
    print("Run the prompt, normalize findings, then score with `uxpanel score --run ...`.")
    return 0


def load_run(run_path: Path) -> dict:
    if run_path.is_dir():
        run_path = run_path / "run.json"
    if run_path.suffix != ".json":
        raise RuntimeError("report generation currently expects a JSON run file")
    try:
        with run_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid JSON in {run_path}: {exc}") from exc

    errors = validate_run_data(data, str(run_path))
    if errors:
        raise RuntimeError("; ".join(errors))
    return data


def load_known_issue_classes(benchmark_path: Path) -> dict[str, int]:
    issue_path = benchmark_path / "known-issues.yaml" if benchmark_path.is_dir() else benchmark_path
    if not issue_path.exists():
        raise RuntimeError(f"known issues file does not exist: {issue_path}")
    text = issue_path.read_text(encoding="utf-8")
    blocks = re.split(r"\n\s*-\s+id:\s+", "\n" + text)
    severity_weights = {"minor": 1, "moderate": 2, "severe": 4}
    classes: dict[str, int] = {}
    for block in blocks[1:]:
        class_match = re.search(r"^\s*class:\s*([a-z0-9]+(?:-[a-z0-9]+)*)$", block, re.MULTILINE)
        severity_match = re.search(r"^\s*severity:\s*(minor|moderate|severe)$", block, re.MULTILINE)
        if not class_match:
            continue
        issue_class = class_match.group(1)
        severity = severity_match.group(1) if severity_match else "minor"
        classes[issue_class] = max(classes.get(issue_class, 0), severity_weights[severity])
    if not classes:
        raise RuntimeError(f"no known issue classes found in {issue_path}")
    return classes


def score_run(run: dict, truth_by_class: dict[str, int]) -> dict:
    predicted_classes = sorted({finding["issue_class"] for finding in run.get("findings", [])})
    truth_classes = sorted(truth_by_class)
    hits = sorted(set(predicted_classes) & set(truth_classes))
    misses = sorted(set(truth_classes) - set(predicted_classes))
    false_positives = sorted(set(predicted_classes) - set(truth_classes))

    precision = None if not predicted_classes else len(hits) / len(predicted_classes)
    recall = None if not truth_classes else len(hits) / len(truth_classes)
    f1 = None if precision is None or recall is None or precision + recall == 0 else 2 * precision * recall / (precision + recall)
    total_weight = sum(truth_by_class.values())
    hit_weight = sum(truth_by_class[item] for item in hits)

    return {
        "score_type": "class-level-preliminary",
        "run_type": run.get("run_type", "panel"),
        "baseline_kind": (run.get("baseline") or {}).get("kind"),
        "run_id": run["run_id"],
        "surface": run["surface"]["ref"],
        "truth_classes": truth_classes,
        "predicted_classes": predicted_classes,
        "hits": hits,
        "misses": misses,
        "false_positives": false_positives,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "severity_weighted_recall": None if total_weight == 0 else hit_weight / total_weight,
        "notes": "Preliminary class-level score. Human scorer review is required for issue-level calibration.",
    }


def cmd_score(args: argparse.Namespace) -> int:
    run_path = Path(args.run)
    benchmark_path = Path(args.benchmark)
    if not run_path.exists():
        print(f"error: run path does not exist: {run_path}", file=sys.stderr)
        return 1
    if not benchmark_path.exists():
        print(f"error: benchmark path does not exist: {benchmark_path}", file=sys.stderr)
        return 1
    score = score_run(load_run(run_path), load_known_issue_classes(benchmark_path))
    text = json.dumps(score, indent=2, sort_keys=True)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text + "\n", encoding="utf-8")
        print(f"Wrote score to {out_path}")
    else:
        print(text)
    return 0


def load_score(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid JSON in {path}: {exc}") from exc


def metric_label(value: object) -> str:
    if value is None:
        return "-"
    if isinstance(value, (int, float)):
        return f"{value:.3f}"
    return str(value)


def render_score_comparison(scores: list[dict]) -> str:
    lines = [
        "| Run | Type | Baseline | Precision | Recall | F1 | Severity-weighted recall | False positives | Misses |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for score in scores:
        lines.append(
            "| "
            f"`{score.get('run_id', '')}` | "
            f"{score.get('run_type', 'panel')} | "
            f"{score.get('baseline_kind') or '-'} | "
            f"{metric_label(score.get('precision'))} | "
            f"{metric_label(score.get('recall'))} | "
            f"{metric_label(score.get('f1'))} | "
            f"{metric_label(score.get('severity_weighted_recall'))} | "
            f"{len(score.get('false_positives', []))} | "
            f"{len(score.get('misses', []))} |"
        )
    return "\n".join(lines)


def cmd_compare_scores(args: argparse.Namespace) -> int:
    scores = [load_score(Path(path)) for path in args.scores]
    comparison = render_score_comparison(scores)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(comparison + "\n", encoding="utf-8")
        print(f"Wrote score comparison to {out_path}")
    else:
        print(comparison)
    return 0


def priority_for(severity: str, confidence: str) -> str:
    if severity == "severe" and confidence in {"high", "medium"}:
        return "P0"
    if severity in {"severe", "moderate"}:
        return "P1"
    return "P2"


def finding_source(finding: dict) -> str:
    return str(finding.get("persona") or finding.get("source") or "unknown")


def render_report(run: dict) -> str:
    run_id = run["run_id"]
    surface = run["surface"]["ref"]
    model = run["model"]
    model_label = "/".join(item for item in [model.get("provider"), model.get("name"), model.get("version")] if item)
    findings = run.get("findings", [])
    run_type = run.get("run_type", "panel")
    baseline = run.get("baseline") or {}

    lines: list[str] = [
        f"# Preflight UX Panel Report: {run_id}",
        "",
        "## Summary",
        "",
        f"Surface: `{surface}`.",
        f"Run date: `{run['date']}`.",
        f"Run type: `{run_type}`.",
        f"Model: `{model_label}`.",
        f"Prompt version: `{run['prompt_version']}`.",
        "Calibration status: `not populated`.",
        "",
    ]
    if run_type == "baseline":
        lines.extend([
            f"Baseline kind: `{baseline.get('kind', 'unknown')}`.",
            f"Baseline prompt: `{baseline.get('prompt_ref', '')}`.",
            "",
        ])
    lines.extend([
        "This report is generated from normalized panel findings. It is a product-risk artifact, not validated user research.",
        "",
        "## Top Risks",
        "",
        "| Priority | Issue class | Source | Severity | Confidence | Recommended action |",
        "|---|---|---|---|---|---|",
    ])

    sorted_findings = sorted(
        findings,
        key=lambda finding: (
            {"P0": 0, "P1": 1, "P2": 2}[priority_for(finding["severity"], finding["confidence"])],
            finding["issue_class"],
            finding_source(finding),
        ),
    )
    if sorted_findings:
        for finding in sorted_findings:
            priority = priority_for(finding["severity"], finding["confidence"])
            recommendation = finding.get("recommendation", "").replace("|", "\\|")
            lines.append(
                f"| {priority} | `{finding['issue_class']}` | `{finding_source(finding)}` | "
                f"{finding['severity']} | {finding['confidence']} | {recommendation} |"
            )
    else:
        lines.append("| - | - | - | - | - | No normalized findings recorded yet. |")

    lines.extend(["", "## Structured Findings", ""])
    if sorted_findings:
        for finding in sorted_findings:
            lines.extend(
                [
                    f"### {finding['id']}: `{finding['issue_class']}`",
                    "",
                    f"- Source: `{finding_source(finding)}`",
                    f"- Severity: `{finding['severity']}`",
                    f"- Confidence: `{finding['confidence']}`",
                    f"- Predicted behavior: {finding['raw_finding']}",
                    f"- Evidence: {finding.get('evidence', '')}",
                    f"- Recommendation: {finding.get('recommendation', '')}",
                    "",
                ]
            )
    else:
        lines.extend([
            "No findings have been added to this run yet.",
            "",
            "Next step: run the panel prompts, normalize findings to taxonomy slugs, and update `findings` in `run.json`.",
            "",
        ])

    lines.extend(
        [
            "## Confidence and Uncertainty",
            "",
            "- Calibration status: not populated unless this run has been scored against benchmark ground truth.",
            "- Treat findings as pre-ship hypotheses until validated by user behavior, telemetry, support data, or scorer review.",
            "",
            "## Validation Plan",
            "",
            "- Compare findings against `benchmark/products/<slug>/known-issues.yaml` when this is a benchmark run.",
            "- Record hits, misses, and false positives in `calibration/`.",
            "- Promote findings only after human scorer review.",
            "",
        ]
    )
    return "\n".join(lines)


def cmd_report(args: argparse.Namespace) -> int:
    run_path = Path(args.run)
    if not run_path.exists():
        print(f"error: run path does not exist: {run_path}", file=sys.stderr)
        return 1
    report = render_report(load_run(run_path))
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report + "\n", encoding="utf-8")
        print(f"Wrote report to {out_path}")
    else:
        print(report)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="uxpanel", description="Preflight UX tooling")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="run repo structural validation")
    validate.set_defaults(func=cmd_validate)

    validate_artifact = subparsers.add_parser("validate-artifact", help="validate a JSON artifact")
    validate_artifact.add_argument("path", help="path to artifact JSON")
    validate_artifact.add_argument("--type", choices=["review-brief", "panel-run"], default="review-brief")
    validate_artifact.set_defaults(func=cmd_validate_artifact)

    new_benchmark = subparsers.add_parser("new-benchmark", help="create a benchmark scaffold")
    new_benchmark.add_argument("slug", help="benchmark slug, e.g. example-product-2026")
    new_benchmark.set_defaults(func=cmd_new_benchmark)

    benchmark_status = subparsers.add_parser("benchmark-status", help="summarize benchmark readiness and scored runs")
    benchmark_status.set_defaults(func=cmd_benchmark_status)

    run = subparsers.add_parser("run", help="create a panel run scaffold")
    run.add_argument("--surface", required=True, help="path to product surface markdown/spec")
    run.add_argument("--panel", default="panels/default.yaml", help="path to panel YAML")
    run.add_argument("--out", help="output run directory; defaults to runs/<run-id>")
    run.add_argument("--run-id", help="explicit run id")
    run.add_argument("--surface-type", default="spec", choices=["benchmark", "url", "screenshot", "spec", "prototype", "pr"])
    run.add_argument("--model-provider", default="manual")
    run.add_argument("--model", default="unrun")
    run.add_argument("--model-version", default="")
    run.add_argument("--temperature", type=float, default=0)
    run.add_argument("--prompt-version", default="manual")
    run.add_argument("--force", action="store_true", help="overwrite an existing run directory")
    run.set_defaults(func=cmd_run)

    baseline = subparsers.add_parser("baseline", help="create a baseline run scaffold")
    baseline.add_argument("--surface", required=True, help="path to product surface markdown/spec")
    baseline.add_argument("--kind", choices=sorted(BASELINE_KINDS), required=True, help="baseline prompt type")
    baseline.add_argument("--out", help="output run directory; defaults to runs/<run-id>")
    baseline.add_argument("--run-id", help="explicit run id")
    baseline.add_argument("--surface-type", default="spec", choices=["benchmark", "url", "screenshot", "spec", "prototype", "pr"])
    baseline.add_argument("--model-provider", default="manual")
    baseline.add_argument("--model", default="unrun")
    baseline.add_argument("--model-version", default="")
    baseline.add_argument("--temperature", type=float, default=0)
    baseline.add_argument("--force", action="store_true", help="overwrite an existing run directory")
    baseline.set_defaults(func=cmd_baseline)

    report = subparsers.add_parser("report", help="generate a report from a panel or baseline run")
    report.add_argument("--run", required=True, help="path to a JSON panel run or run directory")
    report.add_argument("--out", help="optional Markdown output path")
    report.set_defaults(func=cmd_report)

    score = subparsers.add_parser("score", help="score a run against benchmark known issues")
    score.add_argument("--run", required=True, help="path to a JSON panel run or run directory")
    score.add_argument("--benchmark", required=True, help="path to benchmark product directory or known-issues.yaml")
    score.add_argument("--out", help="optional JSON output path")
    score.set_defaults(func=cmd_score)

    compare = subparsers.add_parser("compare-scores", help="compare score JSON files")
    compare.add_argument("scores", nargs="+", help="score JSON files to compare")
    compare.add_argument("--out", help="optional Markdown table output path")
    compare.set_defaults(func=cmd_compare_scores)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
