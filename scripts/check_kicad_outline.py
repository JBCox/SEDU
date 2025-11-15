#!/usr/bin/env python3
"""Verify the KiCad PCB outline and mounting holes (Database-Driven).

UPDATED: Now reads authoritative values from design_database.yaml

Checks:
1. Database has correct board_size (80x50mm) and mounting_holes
2. KiCad PCB file implements database specification correctly

Exit codes:
 0 = OK, 1 = violations found
"""
from __future__ import annotations

import math
import pathlib
import re
import sys
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
PCB = ROOT / "hardware" / "SEDU_PCB.kicad_pcb"
DATABASE = ROOT / "design_database.yaml"


def load_database():
    """Load design database from YAML."""
    if not DATABASE.exists():
        print(f"[kicad_outline] ERROR: Database not found: {DATABASE}")
        sys.exit(1)

    try:
        with open(DATABASE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"[kicad_outline] ERROR: Failed to parse database: {e}")
        sys.exit(1)


def parse_outline_and_holes(text: str):
    # Edge.Cuts rectangle
    rect = re.search(r"\(gr_rect \(start ([\d\.]+) ([\d\.]+)\) \(end ([\d\.]+) ([\d\.]+)\) \(layer \"Edge.Cuts\"\)", text)
    holes = re.findall(r"MountingHole_3\.2mm_M3.*?\(at ([\d\.]+) ([\d\.]+)\).*?\(drill 3\.2\)", text, re.S)
    return rect, [(float(x), float(y)) for x, y in holes]


def main() -> int:
    rc = 0

    # Load database (authoritative source)
    db = load_database()
    metadata = db.get('metadata', {})

    # Extract expected values from database
    board_size = metadata.get('board_size', '')
    mounting_holes = metadata.get('mounting_holes', [])

    # Parse board size (format: "80x50")
    if 'x' not in board_size:
        print(f"[kicad_outline] ERROR: Invalid board_size in database: {board_size}")
        return 1

    try:
        expected_w, expected_h = map(int, board_size.lower().split('x'))
    except ValueError:
        print(f"[kicad_outline] ERROR: Cannot parse board_size: {board_size}")
        return 1

    print(f"[kicad_outline] Database: board_size = {expected_w}x{expected_h}mm")
    print(f"[kicad_outline] Database: {len(mounting_holes)} mounting holes")

    # Validate database values are frozen state compliant
    if expected_w != 80 or expected_h != 50:
        print(f"[kicad_outline] WARNING: Board size {expected_w}x{expected_h} != frozen 80x50mm")
        rc = 1

    if len(mounting_holes) != 4:
        print(f"[kicad_outline] WARNING: {len(mounting_holes)} holes in database, expected 4")
        rc = 1

    # Verify KiCad file implements database spec
    if not PCB.exists():
        print("[kicad_outline] WARNING: hardware/SEDU_PCB.kicad_pcb not found (schematic entry not started)")
        print("[kicad_outline] Database values validated, KiCad check skipped")
        return rc

    text = PCB.read_text(encoding="utf-8")
    rect, holes = parse_outline_and_holes(text)

    if not rect:
        print("[kicad_outline] FAIL: Edge.Cuts rectangle not found in KiCad file")
        rc = 1
    else:
        x0, y0, x1, y1 = map(float, rect.groups())
        w = abs(x1 - x0)
        h = abs(y1 - y0)

        # Check KiCad matches database (with 0.1mm tolerance)
        if abs(w - expected_w) > 0.1 or abs(h - expected_h) > 0.1:
            print(f"[kicad_outline] FAIL: KiCad outline {w:.2f} x {h:.2f} mm != database {expected_w}x{expected_h} mm")
            rc = 1
        else:
            print(f"[kicad_outline] OK: KiCad outline {w:.2f} x {h:.2f} mm matches database")

    if len(holes) != len(mounting_holes):
        print(f"[kicad_outline] FAIL: KiCad has {len(holes)} holes, database specifies {len(mounting_holes)}")
        rc = 1
    else:
        # Convert database hole positions to expected format
        expected = [(h[0], h[1]) for h in mounting_holes]

        def dist(a, b):
            return math.hypot(a[0] - b[0], a[1] - b[1])

        matched = 0
        for e in expected:
            if any(dist(e, h) <= 1.0 for h in holes):
                matched += 1

        if matched != len(expected):
            print(f"[kicad_outline] FAIL: Mounting hole positions off; matched {matched}/{len(expected)} within 1mm")
            rc = 1
        else:
            print(f"[kicad_outline] OK: All {matched} mounting holes match database positions")

    if rc == 0:
        print("[kicad_outline] PASS: Database and KiCad implementation consistent")
    else:
        print("[kicad_outline] FAIL: Verification failed")

    return rc


if __name__ == "__main__":
    sys.exit(main())
