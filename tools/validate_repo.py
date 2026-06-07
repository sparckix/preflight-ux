#!/usr/bin/env python3
"""Structural checks for the Preflight UX repo."""

from __future__ import annotations

import re
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PERSONA_KEYS = {"id", "type", "name", "populated"}
VALID_PERSONA_TYPES = {"ux-expert", "user-type"}
TAXONOMY = ROOT / "taxonomy" / "issue-classes.yaml"
BENCHMARK_TEMPLATE = ROOT / "benchmark" / "products" / "_template"
PANELS = ROOT / "panels"
PROMPTS = ROOT / "prompts"
SCHEMAS = ROOT / "schemas"
RUNS = ROOT / "runs"
BASELINE_KINDS = {"generic-critique", "heuristic-evaluation"}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"{path.relative_to(ROOT)} is missing YAML frontmatter")
    end = text.find("\n---", 4)
    if end == -1:
        fail(f"{path.relative_to(ROOT)} has unterminated frontmatter")
    frontmatter = text[4:end].strip().splitlines()
    data: dict[str, str] = {}
    for line in frontmatter:
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            fail(f"{path.relative_to(ROOT)} has malformed frontmatter line: {line}")
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def collect_personas() -> set[str]:
    persona_paths = sorted((ROOT / "personas").glob("*/*.md"))
    if not persona_paths:
        fail("no persona files found")

    seen_ids: set[str] = set()
    for path in persona_paths:
        data = parse_frontmatter(path)
        missing = REQUIRED_PERSONA_KEYS - set(data)
        if missing:
            fail(f"{path.relative_to(ROOT)} missing frontmatter keys: {sorted(missing)}")
        persona_id = data["id"]
        if persona_id in seen_ids:
            fail(f"duplicate persona id: {persona_id}")
        seen_ids.add(persona_id)
        if data["type"] not in VALID_PERSONA_TYPES:
            fail(f"{path.relative_to(ROOT)} has invalid type: {data['type']}")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", persona_id):
            fail(f"{path.relative_to(ROOT)} has non-slug id: {persona_id}")
    return seen_ids


def collect_taxonomy_slugs() -> set[str]:
    if not TAXONOMY.exists():
        fail("taxonomy/issue-classes.yaml is missing")
    text = TAXONOMY.read_text(encoding="utf-8")
    slugs = re.findall(r"^\s+- slug: ([a-z0-9]+(?:-[a-z0-9]+)*)$", text, re.MULTILINE)
    if not slugs:
        fail("taxonomy has no issue-class slugs")
    duplicates = sorted({slug for slug in slugs if slugs.count(slug) > 1})
    if duplicates:
        fail(f"duplicate taxonomy slugs: {duplicates}")
    return set(slugs)


def validate_benchmark_template(taxonomy_slugs: set[str]) -> None:
    required = {"description.md", "surface.md", "known-issues.yaml", "meta.yaml"}
    missing = [name for name in sorted(required) if not (BENCHMARK_TEMPLATE / name).exists()]
    if missing:
        fail(f"benchmark template missing files: {missing}")
    products_root = ROOT / "benchmark" / "products"
    for product_dir in sorted(path for path in products_root.iterdir() if path.is_dir()):
        missing = [name for name in sorted(required) if not (product_dir / name).exists()]
        if missing:
            fail(f"{product_dir.relative_to(ROOT)} missing files: {missing}")

        meta = (product_dir / "meta.yaml").read_text(encoding="utf-8")
        slug_match = re.search(r"^slug: ([a-z0-9]+(?:-[a-z0-9]+)*)$", meta, re.MULTILINE)
        if not slug_match:
            fail(f"{(product_dir / 'meta.yaml').relative_to(ROOT)} missing slug")
        if product_dir.name != "_template" and slug_match.group(1) != product_dir.name:
            fail(f"{product_dir.relative_to(ROOT)} slug does not match directory name")

        text = (product_dir / "known-issues.yaml").read_text(encoding="utf-8")
        classes = re.findall(r"^\s+class: ([a-z0-9]+(?:-[a-z0-9]+)*)$", text, re.MULTILINE)
        unknown = sorted({item for item in classes if item not in taxonomy_slugs})
        if unknown:
            fail(f"{(product_dir / 'known-issues.yaml').relative_to(ROOT)} references unknown issue classes: {unknown}")
        severities = re.findall(r"^\s+severity: ([a-z]+)$", text, re.MULTILINE)
        invalid_severities = sorted({item for item in severities if item not in {"minor", "moderate", "severe"}})
        if invalid_severities:
            fail(f"{(product_dir / 'known-issues.yaml').relative_to(ROOT)} has invalid severities: {invalid_severities}")
        if product_dir.name != "_template" and "url: " not in text:
            fail(f"{(product_dir / 'known-issues.yaml').relative_to(ROOT)} has no source URLs")


def validate_panels(persona_ids: set[str]) -> None:
    if not PANELS.exists():
        return
    for path in sorted(PANELS.glob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        referenced = re.findall(r"^\s+- ([a-z0-9]+(?:-[a-z0-9]+)*)$", text, re.MULTILINE)
        unknown = sorted({item for item in referenced if item not in persona_ids})
        if unknown:
            fail(f"{path.relative_to(ROOT)} references unknown personas: {unknown}")


def validate_prompts() -> None:
    required = {
        "expert-persona-review.v0.2.md",
        "user-type-review.v0.2.md",
        "normalize-findings.v0.2.md",
        "synthesize-report.v0.2.md",
        "panel-action-card.v0.2.md",
    }
    missing = [name for name in sorted(required) if not (PROMPTS / name).exists()]
    if missing:
        fail(f"prompts missing files: {missing}")


def validate_schemas() -> None:
    required = {
        "persona.schema.json",
        "issue-classes.schema.json",
        "known-issues.schema.json",
        "meta.schema.json",
        "panel-run.schema.json",
        "report-finding.schema.json",
        "score.schema.json",
    }
    missing = [name for name in sorted(required) if not (SCHEMAS / name).exists()]
    if missing:
        fail(f"schemas missing files: {missing}")


def validate_runs(persona_ids: set[str], taxonomy_slugs: set[str]) -> None:
    if not RUNS.exists():
        return
    for path in sorted(RUNS.glob("*/run.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"{path.relative_to(ROOT)} is invalid JSON: {exc}")
        required = {"run_id", "surface", "model", "prompt_version", "date", "personas", "findings"}
        missing = sorted(required - set(data))
        if missing:
            fail(f"{path.relative_to(ROOT)} missing keys: {missing}")
        run_type = data.get("run_type", "panel")
        if run_type not in {"panel", "baseline"}:
            fail(f"{path.relative_to(ROOT)} has invalid run_type: {run_type}")
        if run_type == "panel" and not data.get("personas"):
            fail(f"{path.relative_to(ROOT)} panel run has no personas")
        if run_type == "baseline":
            baseline = data.get("baseline") if isinstance(data.get("baseline"), dict) else {}
            if baseline.get("kind") not in BASELINE_KINDS:
                fail(f"{path.relative_to(ROOT)} has invalid baseline.kind: {baseline.get('kind')}")
            if not str(baseline.get("prompt_ref", "")).strip():
                fail(f"{path.relative_to(ROOT)} baseline.prompt_ref is required")
        unknown_personas = sorted({item for item in data.get("personas", []) if item not in persona_ids})
        if unknown_personas:
            fail(f"{path.relative_to(ROOT)} references unknown personas: {unknown_personas}")
        for finding in data.get("findings", []):
            for key in ["id", "raw_finding", "issue_class", "severity", "confidence"]:
                if key not in finding:
                    fail(f"{path.relative_to(ROOT)} finding missing key: {key}")
            if "persona" not in finding and "source" not in finding:
                fail(f"{path.relative_to(ROOT)} finding must include persona or source")
            if "persona" in finding and finding["persona"] not in persona_ids:
                fail(f"{path.relative_to(ROOT)} finding references unknown persona: {finding['persona']}")
            if "source" in finding and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", str(finding["source"])):
                fail(f"{path.relative_to(ROOT)} finding has invalid source: {finding['source']}")
            if finding["issue_class"] not in taxonomy_slugs:
                fail(f"{path.relative_to(ROOT)} finding references unknown issue class: {finding['issue_class']}")
            if finding["severity"] not in {"minor", "moderate", "severe"}:
                fail(f"{path.relative_to(ROOT)} finding has invalid severity: {finding['severity']}")
            if finding["confidence"] not in {"low", "medium", "high"}:
                fail(f"{path.relative_to(ROOT)} finding has invalid confidence: {finding['confidence']}")


def validate_scores(taxonomy_slugs: set[str]) -> None:
    calibration = ROOT / "calibration"
    if not calibration.exists():
        return
    for path in sorted(calibration.glob("*.score.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"{path.relative_to(ROOT)} is invalid JSON: {exc}")
        required = {
            "score_type",
            "run_id",
            "surface",
            "truth_classes",
            "predicted_classes",
            "hits",
            "misses",
            "false_positives",
            "precision",
            "recall",
            "f1",
            "severity_weighted_recall",
            "notes",
        }
        missing = sorted(required - set(data))
        if missing:
            fail(f"{path.relative_to(ROOT)} missing keys: {missing}")
        if data["score_type"] not in {"class-level-preliminary", "issue-level-reviewed"}:
            fail(f"{path.relative_to(ROOT)} has invalid score_type: {data['score_type']}")
        if data.get("run_type") not in {None, "panel", "baseline"}:
            fail(f"{path.relative_to(ROOT)} has invalid run_type: {data.get('run_type')}")
        if data.get("baseline_kind") not in {None, *BASELINE_KINDS}:
            fail(f"{path.relative_to(ROOT)} has invalid baseline_kind: {data.get('baseline_kind')}")
        for key in ["truth_classes", "predicted_classes", "hits", "misses", "false_positives"]:
            unknown = sorted({item for item in data.get(key, []) if item not in taxonomy_slugs})
            if unknown:
                fail(f"{path.relative_to(ROOT)} has unknown issue classes in {key}: {unknown}")


def main() -> int:
    persona_ids = collect_personas()
    taxonomy_slugs = collect_taxonomy_slugs()
    validate_benchmark_template(taxonomy_slugs)
    validate_panels(persona_ids)
    validate_prompts()
    validate_schemas()
    validate_runs(persona_ids, taxonomy_slugs)
    validate_scores(taxonomy_slugs)
    print("OK: repo structure is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
