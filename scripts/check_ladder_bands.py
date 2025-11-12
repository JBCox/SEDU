#!/usr/bin/env python3
"""
Verify ladder voltage bands are consistent between the SSOT doc and firmware constants.

Checks:
- Parse bands from docs/SEDU_Single_PCB_Parity_Corrected_RevC4a_Final.md
- Parse constants from firmware/src/input_ladder.cpp
- Assert values match within a small tolerance
- Assert ordering and gap structure are as expected
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SSOT = ROOT / "docs" / "SEDU_Single_PCB_Parity_Corrected_RevC4a_Final.md"
FW = ROOT / "firmware" / "src" / "input_ladder.cpp"


def parse_ssot(path: pathlib.Path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    # Find the ladder bands row
    # Example: Ladder voltage bands: <0.20 V fault, 0.75–1.00 V START, 1.55–2.10 V IDLE, 2.60–3.35 V STOP, >3.40 V fault.
    m = re.search(r"Ladder voltage bands:\s*<([0-9.]+)\s*V.*?([0-9.]+)[–-]([0-9.]+)\s*V\s*START,\s*([0-9.]+)[–-]([0-9.]+)\s*V\s*IDLE,\s*([0-9.]+)[–-]([0-9.]+)\s*V\s*STOP,\s*>\s*([0-9.]+)\s*V",
                  text, re.IGNORECASE | re.DOTALL)
    if not m:
        raise SystemExit("[ladder_bands] Could not parse ladder band row from SSOT")
    fault_low, start_min, start_max, idle_min, idle_max, stop_min, stop_max, fault_high = map(float, m.groups())
    return {
        "fault_low": fault_low,
        "start_min": start_min,
        "start_max": start_max,
        "idle_min": idle_min,
        "idle_max": idle_max,
        "stop_min": stop_min,
        "stop_max": stop_max,
        "fault_high": fault_high,
    }


def parse_fw(path: pathlib.Path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    vals = {}
    for name in (
        "kLadderFaultLow",
        "kLadderStartMin",
        "kLadderStartMax",
        "kLadderIdleMin",
        "kLadderIdleMax",
        "kLadderStopMin",
        "kLadderStopMax",
        "kLadderFaultHigh",
    ):
        m = re.search(rf"\b{name}\s*=\s*([0-9]+\.[0-9]+)f?\s*;", text)
        if not m:
            raise SystemExit(f"[ladder_bands] Missing {name} in firmware")
        vals[name] = float(m.group(1))
    return {
        "fault_low": vals["kLadderFaultLow"],
        "start_min": vals["kLadderStartMin"],
        "start_max": vals["kLadderStartMax"],
        "idle_min": vals["kLadderIdleMin"],
        "idle_max": vals["kLadderIdleMax"],
        "stop_min": vals["kLadderStopMin"],
        "stop_max": vals["kLadderStopMax"],
        "fault_high": vals["kLadderFaultHigh"],
    }


def approx_equal(a: float, b: float, tol: float = 0.02) -> bool:
    return abs(a - b) <= tol


def main():
    ssot = parse_ssot(SSOT)
    fw = parse_fw(FW)

    keys = [
        ("fault_low", "FaultLow"),
        ("start_min", "StartMin"),
        ("start_max", "StartMax"),
        ("idle_min", "IdleMin"),
        ("idle_max", "IdleMax"),
        ("stop_min", "StopMin"),
        ("stop_max", "StopMax"),
        ("fault_high", "FaultHigh"),
    ]
    ok = True
    for k, label in keys:
        if not approx_equal(ssot[k], fw[k]):
            print(f"[ladder_bands] {label} mismatch: SSOT={ssot[k]:.2f} V, FW={fw[k]:.2f} V")
            ok = False

    # Ordering checks (expected monotonic increasing)
    seq = [
        ("fault_low", ssot["fault_low"]),
        ("start_min", ssot["start_min"]),
        ("start_max", ssot["start_max"]),
        ("idle_min", ssot["idle_min"]),
        ("idle_max", ssot["idle_max"]),
        ("stop_min", ssot["stop_min"]),
        ("stop_max", ssot["stop_max"]),
        ("fault_high", ssot["fault_high"]),
    ]
    for idx, ((ka, va), (kb, vb)) in enumerate(zip(seq, seq[1:])):
        # Allow equality only for stop_max <= fault_high (inclusive STOP window, fault above)
        if ka == "stop_max" and kb == "fault_high":
            if not (va <= vb):
                print(f"[ladder_bands] Expected {ka} <= {kb}, got {va} !<= {vb}")
                ok = False
            continue
        if not (va < vb):
            print(f"[ladder_bands] Expected {ka} < {kb}, got {va} !< {vb}")
            ok = False

    # Gap checks: only two gaps: (start_max, idle_min) and (idle_max, stop_min)
    gaps = [
        (ssot["start_max"], ssot["idle_min"]),
        (ssot["idle_max"], ssot["stop_min"]),
    ]
    if not (gaps[0][1] > gaps[0][0] and gaps[1][1] > gaps[1][0]):
        print("[ladder_bands] Unexpected gap configuration")
        ok = False

    if not ok:
        raise SystemExit(1)
    print("[ladder_bands] SSOT <-> firmware ladder bands: OK")


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        raise
    except Exception as e:
        print(f"[ladder_bands] ERROR: {e}")
        sys.exit(2)
