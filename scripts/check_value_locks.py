#!/usr/bin/env python3
"""Cross-check critical value locks across key docs to prevent drift.

Checks (hard-coded for Rev C.4x):
- LM5069 variant is '-1' in: SSOT, INIT, Component_Report, README_FOR_CODEX
- DRV8873 locks: R_ILIM = 1.58 kΩ, R_IPROPI = 1.00 kΩ present in: SSOT, INIT, Component_Report, README_FOR_CODEX
- Battery divider: RUV_TOP = 140kΩ, RUV_BOT = 10.0kΩ in BOM matches SSOT and firmware calibration
- Board size '75 × 55 mm' present in: SSOT or Mounting, and INIT

Exit codes: 0 = OK, 1 = mismatches found
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

FILES = {
    "SSOT": ROOT / "docs" / "SEDU_Single_PCB_Parity_Corrected_RevC4a_Final.md",
    "INIT": ROOT / "INIT.md",
    "REPORT": ROOT / "Component_Report.md",
    "GUIDE": ROOT / "README_FOR_CODEX.md",
}

def contains(path: pathlib.Path, pattern: str) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="ignore")
    return re.search(pattern, text, flags=re.IGNORECASE) is not None

def present(path: pathlib.Path, patterns: list[str]) -> list[str]:
    missing = []
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    for pat in patterns:
        if not re.search(pat, text, flags=re.IGNORECASE):
            missing.append(pat)
    return missing

def main() -> int:
    rc = 0
    # LM5069-1 latch-off
    pats_lm5069 = [r"LM5069-1", r"latch\s*[-\u2010-\u2015]?\s*off"]
    # DRV8873 locks (allow 1.0 or 1.00 formatting)
    pats_drv = [r"R[_ ]?ILIM\s*=\s*1\.58\s*k", r"R[_ ]?IPROPI\s*=\s*1\.0+\s*k"]
    # Board size (optimized from 80×60mm)
    pats_size = [r"75\s*[×x]\s*55\s*mm"]

    for label, path in FILES.items():
        missing = present(path, pats_lm5069 + pats_drv)
        if missing:
            print(f"[locks] {label}: missing {', '.join(missing)} in {path}")
            rc = 1

    # Rsense lock (3.0 mΩ) must appear in SSOT and Schematic_Place_List.csv
    ssot_ok = contains(FILES["SSOT"], r"3\.0\s*m[ΩOhm]") and contains(FILES["SSOT"], r"ILIM\s*≈?\s*18")
    bom_ok = contains(ROOT / "hardware" / "Schematic_Place_List.csv", r"RS_IN,\s*3\.0\s*m[ΩOhm]")
    if not ssot_ok:
        print("[locks] Rsense 3.0 mΩ and ILIM≈18 A not confirmed in SSOT")
        rc = 1
    if not bom_ok:
        print("[locks] RS_IN not set to 3.0 mΩ in hardware/Schematic_Place_List.csv")
        rc = 1

    # Battery divider lock (140kΩ / 10.0kΩ) must match across BOM, SSOT, and firmware
    bom_path = ROOT / "hardware" / "BOM_Seed.csv"
    bom_ruv_top_ok = contains(bom_path, r"RUV_TOP,\s*ERA-3AEB1403V") and contains(bom_path, r"140\s*k[ΩOhm]")
    bom_ruv_bot_ok = contains(bom_path, r"RUV_BOT,\s*ERA-3AEB1002V") and contains(bom_path, r"10\.0\s*k[ΩOhm]")
    ssot_divider_ok = contains(FILES["SSOT"], r"140\s*k[ΩOhm]\s*/\s*10\.0\s*k[ΩOhm]")

    if not bom_ruv_top_ok:
        print("[locks] Battery divider RUV_TOP not set to 140kΩ (ERA-3AEB1403V) in BOM_Seed.csv")
        rc = 1
    if not bom_ruv_bot_ok:
        print("[locks] Battery divider RUV_BOT not set to 10.0kΩ (ERA-3AEB1002V) in BOM_Seed.csv")
        rc = 1
    if not ssot_divider_ok:
        print("[locks] Battery divider 140kΩ/10.0kΩ not documented in SSOT")
        rc = 1

    # Firmware calibration check (optional - verify sensors.cpp has correct cal values)
    sensors_path = ROOT / "firmware" / "src" / "sensors.cpp"
    if sensors_path.exists():
        # Check for correct calibration: {1489, 18.0f, 2084, 25.2f}
        cal_ok = contains(sensors_path, r"1489,\s*18\.0f,\s*2084,\s*25\.2f")
        if not cal_ok:
            print("[locks] Battery calibration in sensors.cpp doesn't match 140kΩ/10kΩ divider")
            print("        Expected: kBatteryCal{1489, 18.0f, 2084, 25.2f}")
            rc = 1

    # Board size must be in SSOT (or mounting) and INIT
    ssot_ok = not present(FILES["SSOT"], pats_size)
    init_ok = not present(FILES["INIT"], pats_size)
    if not ssot_ok:
        # try mounting file
        mount = ROOT / "hardware" / "Mounting_And_Envelope.md"
        ssot_ok = not present(mount, pats_size)
    if not ssot_ok:
        print("[locks] Board size 75×55 mm missing in SSOT/Mounting")
        rc = 1
    if not init_ok:
        print("[locks] Board size 75×55 mm missing in INIT.md")
        rc = 1

    if rc == 0:
        print("[locks] Critical value locks consistent. PASS")
    return rc

if __name__ == "__main__":
    sys.exit(main())
