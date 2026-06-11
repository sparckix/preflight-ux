#!/usr/bin/env python3
"""Bridge installed Preflight UX skills back to a repo checkout."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def is_preflight_repo(path: Path) -> bool:
    return (
        (path / "pyproject.toml").is_file()
        and (path / "uxpanel" / "cli.py").is_file()
        and (path / "tools" / "validate_repo.py").is_file()
        and (path / "benchmark" / "products" / "_template").is_dir()
    )


def parents_from(path: Path) -> list[Path]:
    resolved = path.resolve()
    if resolved.is_file():
        resolved = resolved.parent
    return [resolved, *resolved.parents]


def candidate_roots(explicit_repo: str | None) -> list[Path]:
    candidates: list[Path] = []
    for value in [explicit_repo, os.environ.get("PREFLIGHT_UX_REPO")]:
        if value:
            candidates.append(Path(value).expanduser())

    candidates.extend(parents_from(Path.cwd()))
    candidates.extend(parents_from(Path(__file__)))

    home = Path.home()
    candidates.extend(
        [
            home / "preflight-ux",
            home / "src" / "preflight-ux",
            home / "code" / "preflight-ux",
            home / "Projects" / "preflight-ux",
        ]
    )

    seen: set[Path] = set()
    unique: list[Path] = []
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if resolved not in seen:
            seen.add(resolved)
            unique.append(resolved)
    return unique


def find_repo(explicit_repo: str | None = None) -> Path:
    for candidate in candidate_roots(explicit_repo):
        if is_preflight_repo(candidate):
            return candidate
    raise RuntimeError(
        "could not find a Preflight UX checkout; run from the repo or set PREFLIGHT_UX_REPO"
    )


def run_uxpanel(repo: Path, uxpanel_args: list[str]) -> int:
    if not uxpanel_args:
        print("error: provide uxpanel arguments, for example: uxpanel validate", file=sys.stderr)
        return 2
    if uxpanel_args and uxpanel_args[0] == "--":
        uxpanel_args = uxpanel_args[1:]
    command = [sys.executable, "-m", "uxpanel", *uxpanel_args]
    return subprocess.call(command, cwd=repo)


def run_validator(repo: Path) -> int:
    return subprocess.call([sys.executable, "tools/validate_repo.py"], cwd=repo)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Locate a Preflight UX checkout and delegate to its repo tooling."
    )
    parser.add_argument(
        "--repo",
        help="Preflight UX checkout path. Defaults to PREFLIGHT_UX_REPO or nearest parent checkout.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("locate", help="Print the detected Preflight UX repo path.")
    subparsers.add_parser("validate", help="Run repo validation and uxpanel validation.")
    subparsers.add_parser("benchmark-status", help="Run uxpanel benchmark-status.")

    uxpanel_parser = subparsers.add_parser("uxpanel", help="Pass arguments through to python -m uxpanel.")
    uxpanel_parser.add_argument("uxpanel_args", nargs=argparse.REMAINDER)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        repo = find_repo(args.repo)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.command == "locate":
        print(repo)
        return 0
    if args.command == "validate":
        repo_status = run_validator(repo)
        if repo_status != 0:
            return repo_status
        return run_uxpanel(repo, ["validate"])
    if args.command == "benchmark-status":
        return run_uxpanel(repo, ["benchmark-status"])
    if args.command == "uxpanel":
        return run_uxpanel(repo, args.uxpanel_args)

    print(f"error: unsupported command: {args.command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
