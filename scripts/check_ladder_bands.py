#!/usr/bin/env python3
"""
Verify ladder voltage bands are consistent between database and firmware (Database-Driven).

UPDATED: Now reads authoritative values from design_database.yaml

Checks:
1. Database defines button_ladder with fault thresholds and bands
2. Firmware constants match database values
3. Ordering and gap structure are correct
4. Monotonic increasing voltage bands

Exit codes: 0 OK, 1 violations found
"""
from __future__ import annotations

import pathlib
import re
import sys
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATABASE = ROOT / "design_database.yaml"
FW = ROOT / "firmware" / "src" / "input_ladder.cpp"


def load_database():
    """Load design database from YAML."""
    if not DATABASE.exists():
        print(f"[ladder_bands] ERROR: Database not found: {DATABASE}")
        sys.exit(1)

    try:
        with open(DATABASE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"[ladder_bands] ERROR: Failed to parse database: {e}")
        sys.exit(1)


def parse_database_ladder(db):
    """Extract ladder band values from database.

    Returns dict with keys: fault_low, start_min, start_max, idle_min,
    idle_max, stop_min, stop_max, fault_high
    """
    ladder = db.get('button_ladder', {})

    if not ladder:
        print("[ladder_bands] ERROR: No button_ladder section in database")
        sys.exit(1)

    bands = ladder.get('bands', {})

    # Extract values
    values = {
        "fault_low": ladder.get('fault_low_threshold'),
        "fault_high": ladder.get('fault_high_threshold'),
    }

    # Extract band min/max values
    for band_name in ['START', 'IDLE', 'STOP']:
        band = bands.get(band_name, {})
        if not band:
            print(f"[ladder_bands] ERROR: Band {band_name} not found in database")
            sys.exit(1)

        key_min = band_name.lower() + "_min"
        key_max = band_name.lower() + "_max"
        values[key_min] = band.get('voltage_min')
        values[key_max] = band.get('voltage_max')

    # Validate all values exist
    for key, val in values.items():
        if val is None:
            print(f"[ladder_bands] ERROR: Missing value for {key} in database")
            sys.exit(1)

    return values


def parse_fw(path: pathlib.Path):
    """Parse firmware ladder constants."""
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
    """Check if two values are approximately equal within tolerance."""
    return abs(a - b) <= tol


def main():
    # Load database (authoritative source)
    db = load_database()
    db_ladder = parse_database_ladder(db)

    # Parse firmware constants
    fw = parse_fw(FW)

    print("[ladder_bands] Database ladder values:")
    print(f"  Fault low:  < {db_ladder['fault_low']:.2f} V")
    print(f"  START:      {db_ladder['start_min']:.2f} - {db_ladder['start_max']:.2f} V")
    print(f"  IDLE:       {db_ladder['idle_min']:.2f} - {db_ladder['idle_max']:.2f} V")
    print(f"  STOP:       {db_ladder['stop_min']:.2f} - {db_ladder['stop_max']:.2f} V")
    print(f"  Fault high: > {db_ladder['fault_high']:.2f} V")
    print()

    # Compare database vs firmware
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
    mismatches = []

    for k, label in keys:
        if not approx_equal(db_ladder[k], fw[k]):
            mismatch = f"  {label}: Database={db_ladder[k]:.2f} V, Firmware={fw[k]:.2f} V"
            mismatches.append(mismatch)
            ok = False

    if mismatches:
        print("[ladder_bands] FAIL: Database vs Firmware mismatch:")
        for m in mismatches:
            print(m)
        print()
    else:
        print("[ladder_bands] OK: Database matches firmware (±0.02V tolerance)")
        print()

    # Ordering checks (expected monotonic increasing)
    seq = [
        ("fault_low", db_ladder["fault_low"]),
        ("start_min", db_ladder["start_min"]),
        ("start_max", db_ladder["start_max"]),
        ("idle_min", db_ladder["idle_min"]),
        ("idle_max", db_ladder["idle_max"]),
        ("stop_min", db_ladder["stop_min"]),
        ("stop_max", db_ladder["stop_max"]),
        ("fault_high", db_ladder["fault_high"]),
    ]

    ordering_ok = True
    for idx, ((ka, va), (kb, vb)) in enumerate(zip(seq, seq[1:])):
        # Allow equality only for stop_max <= fault_high (inclusive STOP window, fault above)
        if ka == "stop_max" and kb == "fault_high":
            if not (va <= vb):
                print(f"[ladder_bands] FAIL: Expected {ka} <= {kb}, got {va:.2f} !<= {vb:.2f}")
                ordering_ok = False
            continue
        if not (va < vb):
            print(f"[ladder_bands] FAIL: Expected {ka} < {kb}, got {va:.2f} !< {vb:.2f}")
            ordering_ok = False

    if not ordering_ok:
        ok = False
    else:
        print("[ladder_bands] OK: Voltage bands are monotonically increasing")
        print()

    # Gap checks: only two gaps: (start_max, idle_min) and (idle_max, stop_min)
    gaps = [
        (db_ladder["start_max"], db_ladder["idle_min"]),
        (db_ladder["idle_max"], db_ladder["stop_min"]),
    ]

    gap_ok = True
    if not (gaps[0][1] > gaps[0][0]):
        print(f"[ladder_bands] FAIL: No gap between START and IDLE: {gaps[0][0]:.2f} >= {gaps[0][1]:.2f}")
        gap_ok = False

    if not (gaps[1][1] > gaps[1][0]):
        print(f"[ladder_bands] FAIL: No gap between IDLE and STOP: {gaps[1][0]:.2f} >= {gaps[1][1]:.2f}")
        gap_ok = False

    if gap_ok:
        gap1_size = gaps[0][1] - gaps[0][0]
        gap2_size = gaps[1][1] - gaps[1][0]
        print(f"[ladder_bands] OK: Gap between START and IDLE: {gap1_size:.2f} V")
        print(f"[ladder_bands] OK: Gap between IDLE and STOP: {gap2_size:.2f} V")
        print()
    else:
        ok = False

    if not ok:
        print("[ladder_bands] FAIL: Ladder band verification failed")
        raise SystemExit(1)

    print("[ladder_bands] PASS: Database <-> firmware ladder bands consistent")


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        raise
    except Exception as e:
        print(f"[ladder_bands] ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)
