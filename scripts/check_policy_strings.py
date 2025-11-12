#!/usr/bin/env python3
"""Scan repo for banned strings to prevent documentation confusion.

Fails if banned strings appear outside allowlist files.
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TLV_BANNED = ["TLV757"]  # wrong LDO family
BANNED_HW = ["VESC fallback", "PPM", "PWM header"]  # legacy interfaces

ALLOWLIST = {
    ROOT / "README_FOR_CODEX.md",  # mentions banned strings as examples in rules
    ROOT / ".github" / "workflows" / "validate.yml",  # references in CI text
    ROOT / "docs" / "DOCS_INDEX.md",  # archive listings may mention TLV757
    ROOT / "scripts" / "check_policy_strings.py",  # this script contains the tokens
}


def scan() -> int:
    rc = 0
    for p in ROOT.rglob("*"):
        if p.is_dir():
            continue
        if p.suffix in {".pdf", ".jpg", ".png"}:
            continue
        if p in ALLOWLIST:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        # Rule 1: TLV757 banned anywhere except archive/
        if any(s in text for s in TLV_BANNED):
            if "archive/" not in str(p):
                print(f"[policy] {p}: banned LDO string found (TLV757)")
                rc = 1
                continue
        # Rule 2: legacy interfaces banned only in hardware/, firmware/, New Single Board Idea.md, Component_Report.md
        if "hardware/" in str(p) or "firmware/" in str(p) or p.name in {"New Single Board Idea.md", "Component_Report.md"}:
            hits = [s for s in BANNED_HW if s in text]
            if hits:
                print(f"[policy] {p}: banned legacy strings found: {', '.join(hits)}")
                rc = 1
    if rc == 0:
        print("[policy] No banned strings found outside allowlist. PASS")
    return rc


if __name__ == "__main__":
    sys.exit(scan())
