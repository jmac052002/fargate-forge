#!/usr/bin/env python3
"""Reject sensitive or generated files that must never be tracked."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path, PurePosixPath


def tracked_paths(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    return [
        item.decode("utf-8", errors="surrogateescape")
        for item in result.stdout.split(b"\0")
        if item
    ]


def forbidden_reason(relative_path: str) -> str | None:
    path = PurePosixPath(relative_path)
    parts = path.parts
    lower_name = path.name.lower()
    lower_parts = {part.lower() for part in parts}

    if ".terraform" in lower_parts:
        return "Terraform working directory"
    if ".venv" in lower_parts or "venv" in lower_parts:
        return "Python virtual environment"
    if "__pycache__" in lower_parts:
        return "Python bytecode cache"

    if lower_name.endswith(".tfstate") or ".tfstate." in lower_name:
        return "Terraform state or backup"
    if lower_name.endswith(".tfplan") or lower_name == "plan.out":
        return "Terraform plan artifact"
    if lower_name == ".terraform.tfstate.lock.info":
        return "Terraform local lock metadata"
    if lower_name.endswith(".tfvars") or lower_name.endswith(".tfvars.json"):
        return "Terraform variable values"

    if lower_name == ".env" or lower_name.startswith(".env."):
        if lower_name not in {".env.example", ".env.sample", ".env.template"}:
            return "environment file"

    if lower_name in {
        "credentials",
        "credentials.json",
        "kubeconfig",
        "id_rsa",
        "id_dsa",
        "id_ecdsa",
        "id_ed25519",
    }:
        return "credential or private-key file"
    if lower_name.endswith((".p12", ".pfx", ".jks", ".keystore")):
        return "credential keystore"

    return None


def main() -> int:
    repo_root = Path(
        subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
        ).strip()
    )

    violations: list[tuple[str, str]] = []
    for relative_path in tracked_paths(repo_root):
        # This permits review of an unstaged deletion while still checking every
        # tracked file in a clean checkout and in CI.
        if not (repo_root / relative_path).exists():
            continue
        reason = forbidden_reason(relative_path)
        if reason:
            violations.append((relative_path, reason))

    if violations:
        print("Forbidden tracked files detected:", file=sys.stderr)
        for relative_path, reason in violations:
            print(f"  {relative_path}: {reason}", file=sys.stderr)
        return 1

    print("Repository hygiene check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
