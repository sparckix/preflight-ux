#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run(cmd: list[str], expect: int = 0) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if proc.returncode != expect:
        print(f"FAILED: {' '.join(cmd)}", file=sys.stderr)
        print(f"expected={expect} actual={proc.returncode}", file=sys.stderr)
        print(proc.stdout, file=sys.stderr)
        print(proc.stderr, file=sys.stderr)
        raise SystemExit(1)
    return proc


def assert_contains(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"missing {label}: {needle!r}\n{text}")


def main() -> int:
    run([PYTHON, "tools/validate_repo.py"])
    run([PYTHON, "-m", "uxpanel", "validate"])
    help_out = run([PYTHON, "-m", "uxpanel", "--help"]).stdout
    for cmd in ["validate", "validate-artifact", "new-benchmark", "benchmark-status", "run", "baseline", "report", "score", "compare-scores"]:
        assert_contains(help_out, cmd, f"help command {cmd}")

    bad_slug = run([PYTHON, "-m", "uxpanel", "new-benchmark", "Bad_Slug"], expect=2)
    assert_contains(bad_slug.stderr, "slug must", "bad slug error")
    status = run([PYTHON, "-m", "uxpanel", "benchmark-status"]).stdout
    assert_contains(status, "apple-maps-2012", "benchmark status apple row")
    assert_contains(status, "Source quality", "benchmark status header")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        run_dir = tmp_path / "run"
        run([
            PYTHON,
            "-m",
            "uxpanel",
            "run",
            "--surface",
            "web/README.md",
            "--run-id",
            "sim-web-ui",
            "--out",
            str(run_dir),
            "--force",
        ])
        run_json = run_dir / "run.json"
        if not run_json.exists():
            raise SystemExit("run scaffold missing run.json")
        data = json.loads(run_json.read_text())
        if data["run_id"] != "sim-web-ui":
            raise SystemExit("run id mismatch")
        if len(data["personas"]) < 5:
            raise SystemExit("default panel persona parse failed")

        brief_json = tmp_path / "brief.json"
        brief_json.write_text(json.dumps({
            "artifact_type": "preflight_ux_review_brief",
            "schema_version": "0.3",
            "run_id": "sim-brief",
            "prompt_version": "web-byok-v0.4",
            "product": {
                "name": "Sim Brief",
                "audience": "Operators",
                "stage": "prototype",
                "surface_type": "prototype",
                "prototype_url": "https://example.com/proto",
                "surface": "A surface description"
            },
            "attachments": {"screenshots": []},
            "review": {"depth": "fast", "synthesis_mode": "prioritized"},
            "panel": {"personas": ["tom-random-visitor"], "risk_focus": ["empty-state-confusion"]}
        }, indent=2))
        run([PYTHON, "-m", "uxpanel", "validate-artifact", str(brief_json), "--type", "review-brief"])
        run([PYTHON, "-m", "uxpanel", "validate-artifact", str(run_json), "--type", "panel-run"])

        report = run([PYTHON, "-m", "uxpanel", "report", "--run", str(run_dir)]).stdout
        assert_contains(report, "No normalized findings", "empty report state")

        baseline_dir = tmp_path / "baseline"
        run([
            PYTHON,
            "-m",
            "uxpanel",
            "baseline",
            "--surface",
            "benchmark/products/apple-maps-2012/surface.md",
            "--surface-type",
            "benchmark",
            "--kind",
            "generic-critique",
            "--run-id",
            "sim-baseline",
            "--out",
            str(baseline_dir),
            "--force",
        ])
        baseline_prompt = baseline_dir / "baseline-prompt.md"
        if not baseline_prompt.exists():
            raise SystemExit("baseline prompt missing")
        assert_contains(baseline_prompt.read_text(), "Likely false positives", "baseline uncertainty section")
        baseline_json = baseline_dir / "run.json"
        baseline_data = json.loads(baseline_json.read_text())
        baseline_data["findings"] = [
            {
                "id": "finding-001",
                "source": "baseline-generic-critique",
                "raw_finding": "Incorrect map data would undermine trust in the default navigation product.",
                "issue_class": "data-quality-trust-break",
                "severity": "severe",
                "confidence": "high",
                "evidence": "Surface describes wrong or missing locations.",
                "recommendation": "Expose data limitations and fallback options."
            }
        ]
        baseline_json.write_text(json.dumps(baseline_data, indent=2) + "\n")
        run([PYTHON, "-m", "uxpanel", "validate-artifact", str(baseline_json), "--type", "panel-run"])
        baseline_report = run([PYTHON, "-m", "uxpanel", "report", "--run", str(baseline_dir)]).stdout
        assert_contains(baseline_report, "Run type: `baseline`", "baseline report type")
        assert_contains(baseline_report, "baseline-generic-critique", "baseline finding source")
        baseline_score_out = tmp_path / "baseline-score.json"
        run([
            PYTHON,
            "-m",
            "uxpanel",
            "score",
            "--run",
            str(baseline_dir),
            "--benchmark",
            "benchmark/products/apple-maps-2012",
            "--out",
            str(baseline_score_out),
        ])
        baseline_score = json.loads(baseline_score_out.read_text())
        if baseline_score["run_type"] != "baseline" or baseline_score["baseline_kind"] != "generic-critique":
            raise SystemExit("baseline score metadata missing")
        if baseline_score["precision"] != 1.0 or baseline_score["recall"] != 0.5:
            raise SystemExit("expected illustrative baseline class score to be precision 1.0 and recall 0.5")

        report_out = tmp_path / "report.md"
        run([
            PYTHON,
            "-m",
            "uxpanel",
            "report",
            "--run",
            "runs/govuk-verify-2016-public-service-panel-v0-3",
            "--out",
            str(report_out),
        ])
        assert_contains(report_out.read_text(), "Preflight UX Panel Report", "written report title")

        score_out = tmp_path / "score.json"
        run([
            PYTHON,
            "-m",
            "uxpanel",
            "score",
            "--run",
            "runs/govuk-verify-2016-public-service-panel-v0-3",
            "--benchmark",
            "benchmark/products/govuk-verify-2016",
            "--out",
            str(score_out),
        ])
        score = json.loads(score_out.read_text())
        if score["precision"] != 0.6 or score["recall"] != 1.0:
            raise SystemExit("expected GOV.UK Verify panel score precision 0.6 and recall 1.0")

        comparison = run([PYTHON, "-m", "uxpanel", "compare-scores", str(score_out), str(baseline_score_out)]).stdout
        assert_contains(comparison, "govuk-verify-2016-public-service-panel-v0-3", "panel score comparison row")
        assert_contains(comparison, "sim-baseline", "baseline score comparison row")
        assert_contains(comparison, "generic-critique", "baseline score comparison kind")

        bench_slug = "sim-product"
        bench_dir = ROOT / "benchmark" / "products" / bench_slug
        if bench_dir.exists():
            shutil.rmtree(bench_dir)
        try:
            run([PYTHON, "-m", "uxpanel", "new-benchmark", bench_slug])
            meta = (bench_dir / "meta.yaml").read_text()
            assert_contains(meta, "slug: sim-product", "new benchmark slug")
        finally:
            if bench_dir.exists():
                shutil.rmtree(bench_dir)

    run(["node", "--check", "api/panel.js"])
    run(["node", "--check", "web/app.js"])
    run([PYTHON, "tools/run_baseline_agent.py", "--self-test"])
    run([PYTHON, "tools/run_panel_agent.py", "--self-test"])
    run(["node", "tests/simulate_byok_api.mjs"])
    run(["node", "tests/simulate_web_logic.mjs"])
    run(["node", "tests/simulate_web_static.mjs"])

    print("OK: local simulations passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
