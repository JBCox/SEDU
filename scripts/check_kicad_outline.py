#!/usr/bin/env python3
"""Verify the KiCad PCB outline and mounting holes.

Checks:
- Edge.Cuts rectangle exists and is <= 80 x 50 mm (within small tolerance)
- Four M3 mounting holes exist (3.2 mm drill), roughly at (4,4), (76,4), (4,46), (76,46)

Exit codes:
 0 = OK, 1 = violations found
"""
from __future__ import annotations

import math
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PCB = ROOT / "hardware" / "SEDU_PCB.kicad_pcb"


def parse_outline_and_holes(text: str):
    # Edge.Cuts rectangle
    rect = re.search(r"\(gr_rect \(start ([\d\.]+) ([\d\.]+)\) \(end ([\d\.]+) ([\d\.]+)\) \(layer \"Edge.Cuts\"\)", text)
    holes = re.findall(r"MountingHole_3\.2mm_M3.*?\(at ([\d\.]+) ([\d\.]+)\).*?\(drill 3\.2\)", text, re.S)
    return rect, [(float(x), float(y)) for x, y in holes]


def main() -> int:
    if not PCB.exists():
        print("[kicad_outline] Missing hardware/SEDU_PCB.kicad_pcb")
        return 1
    text = PCB.read_text(encoding="utf-8")
    rect, holes = parse_outline_and_holes(text)
    rc = 0
    if not rect:
        print("[kicad_outline] Edge.Cuts rectangle not found")
        rc = 1
    else:
        x0, y0, x1, y1 = map(float, rect.groups())
        w = abs(x1 - x0)
        h = abs(y1 - y0)
        if w > 80.05 or h > 50.05:
            print(f"[kicad_outline] Outline too large: {w:.2f} x {h:.2f} mm (max 80 x 50)")
            rc = 1
        else:
            print(f"[kicad_outline] Outline OK: {w:.2f} x {h:.2f} mm")
    if len(holes) != 4:
        print(f"[kicad_outline] Expected 4 mounting holes, found {len(holes)}")
        rc = 1
    else:
        expected = [(4, 4), (76, 4), (4, 46), (76, 46)]
        def dist(a,b):
            return math.hypot(a[0]-b[0], a[1]-b[1])
        matched = 0
        for e in expected:
            if any(dist(e, h) <= 1.0 for h in holes):
                matched += 1
        if matched != 4:
            print(f"[kicad_outline] Mounting holes positions off; matched {matched}/4 within 1 mm tolerance")
            rc = 1
        else:
            print("[kicad_outline] Mounting holes OK")
    if rc == 0:
        print("[kicad_outline] PASS")
    return rc


if __name__ == "__main__":
    sys.exit(main())

