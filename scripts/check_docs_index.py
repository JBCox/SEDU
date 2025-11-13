#!/usr/bin/env python3
"""Validate docs/DOCS_INDEX.md against the repo.

Checks:
- Every backticked path under docs/, hardware/, firmware/, scripts/, archive/ exists.
- List unindexed artifacts in those folders (ignoring common noise).

Exit codes:
 0 = OK, 1 = missing referenced files, 2 = unindexed artifacts found.
"""
from __future__ import annotations

import pathlib
import re
import sys
from typing import Set, List

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs" / "DOCS_INDEX.md"
SCAN_DIRS = ["docs", "hardware", "firmware", "scripts", "archive"]
IGNORE_SUFFIXES = {
    ".pyc", ".pyo", ".log", ".tmp", ".bak",
}
IGNORE_NAMES = {
    ".DS_Store", "__pycache__",
}


def extract_paths(md_text: str) -> Set[pathlib.Path]:
    paths: Set[pathlib.Path] = set()
    # Match backticked code spans and filter for our dirs
    for m in re.findall(r"`([^`]+)`", md_text):
        p = pathlib.Path(m)
        if any(p.as_posix().startswith(d + "/") for d in SCAN_DIRS):
            paths.add(p)
    return paths


def list_repo_artifacts() -> Set[pathlib.Path]:
    results: Set[pathlib.Path] = set()
    for d in SCAN_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for p in base.rglob("*"):
            rel = p.relative_to(ROOT)
            if p.is_dir():
                continue
            if rel.name in IGNORE_NAMES:
                continue
            if any(rel.suffix.endswith(s) for s in IGNORE_SUFFIXES):
                continue
            results.add(rel)
    return results


def main() -> int:
    if not INDEX.exists():
        print("[docs_index] Missing docs/DOCS_INDEX.md")
        return 1
    md_text = INDEX.read_text(encoding="utf-8")
    listed = extract_paths(md_text)
    repo = list_repo_artifacts()

    missing: List[pathlib.Path] = []
    for p in sorted(listed):
        if not (ROOT / p).exists():
            missing.append(p)

    unindexed = sorted(repo - listed)

    rc = 0
    if missing:
        print("[docs_index] Missing files referenced in DOCS_INDEX.md:")
        for p in missing:
            print(f"  - {p}")
        rc = 1
    if unindexed:
        print("[docs_index] Unindexed artifacts found (consider adding to DOCS_INDEX.md):")
        for p in unindexed:
            print(f"  - {p}")
        # Do not fail hard for unindexed; return 2 to flag review while allowing CI to pass if desired
        rc = rc or 2
    if rc == 0:
        print("[docs_index] Index OK; all referenced files exist and no unindexed artifacts detected.")
    return rc


if __name__ == "__main__":
    sys.exit(main())

