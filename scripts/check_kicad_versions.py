#!/usr/bin/env python3
"""Report KiCad file format versions and compare to a target.

This does not fail the build; it prints the versions found so we can
record them in docs/TOOL_VERSIONS.md and decide whether to upgrade.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]

PCB = ROOT / "hardware" / "SEDU_PCB.kicad_pcb"
TOP_SCH = ROOT / "hardware" / "SEDU_PCB.kicad_sch"

def extract_version(text: str) -> str | None:
    m = re.search(r"\(version\s+(\d{6,})\)", text)
    return m.group(1) if m else None

def main() -> int:
    if PCB.exists():
        pv = extract_version(PCB.read_text(encoding="utf-8", errors="ignore"))
        print(f"[kicad_ver] PCB file format version: {pv or 'unknown'} ({PCB})")
    else:
        print("[kicad_ver] PCB file not found")
    if TOP_SCH.exists():
        sv = extract_version(TOP_SCH.read_text(encoding="utf-8", errors="ignore"))
        print(f"[kicad_ver] SCH file format version: {sv or 'unknown'} ({TOP_SCH})")
    else:
        print("[kicad_ver] Schematic file not found")
    print("[kicad_ver] Target KiCad: 8.x stable — ok to open and save to upgrade formats.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

