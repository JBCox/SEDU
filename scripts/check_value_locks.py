#!/usr/bin/env python3
"""
SEDU Value Locks Verification - Database-Driven

Validates that critical locked design values in design_database.yaml
are correct and haven't been accidentally changed.

This script checks THE DATABASE ITSELF, not generated files.
Generated files are checked separately by check_generated_files.py

Returns 0 if all locked values correct, 1 if violations found.
"""

import sys
from pathlib import Path
import yaml


def load_database():
    """Load design database from YAML."""
    db_path = Path(__file__).parent.parent / "design_database.yaml"
    if not db_path.exists():
        print(f"[ERROR] Database not found: {db_path}")
        sys.exit(1)

    with open(db_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def check_locked_values():
    """Verify all locked component values are correct."""
    db = load_database()

    # Expected locked values (frozen for Rev C.4b)
    EXPECTED_LOCKS = {
        'RS_IN': {'value': '3.0m', 'reason': 'LM5069 ILIM calculation'},
        'R_ILIM': {'value': '1.58k', 'reason': 'DRV8873 current limit'},
        'R_IPROPI': {'value': '1.00k', 'reason': 'DRV8873 IPROPI scaling'},
        'R_VBAT_TOP': {'value': '140k', 'reason': 'Battery divider calculation'},
        'R_VBAT_BOT': {'value': '10k', 'reason': 'Battery divider calculation'},
        'RS_U': {'value': '2.0m', 'reason': 'Motor CSA calculation'},
        'RS_V': {'value': '2.0m', 'reason': 'Motor CSA calculation'},
        'RS_W': {'value': '2.0m', 'reason': 'Motor CSA calculation'},
        'RFBT': {'value': '100k', 'reason': 'LMR33630 3.3V output'},
        'RFBB': {'value': '43.2k', 'reason': 'LMR33630 3.3V output'},
        'C_CPLCPH': {'value': '47nF', 'reason': 'DRV8353 charge pump'},
        'CDVDT': {'value': '33nF', 'reason': 'LM5069 dV/dt control'},
        'L4': {'value': '10uH', 'reason': 'LMR33630 inductor'},
        'RUV_TOP': {'value': '140k', 'reason': 'LM5069 UV threshold'},
        'RUV_BOT': {'value': '10k', 'reason': 'LM5069 UV threshold'},
        'ROV_TOP': {'value': '221k', 'reason': 'LM5069 OV threshold'},
        'ROV_BOT': {'value': '10k', 'reason': 'LM5069 OV threshold'},
    }

    components = db.get('components', {})

    all_pass = True
    violations = []

    print("=" * 70)
    print("SEDU VALUE LOCKS VERIFICATION (Database-Driven)")
    print("=" * 70)
    print()

    # Check each expected locked value
    for ref, expected in EXPECTED_LOCKS.items():
        if ref not in components:
            print(f"[FAIL] {ref:15s} MISSING from database")
            violations.append(f"{ref}: Component missing from design_database.yaml")
            all_pass = False
            continue

        comp = components[ref]
        actual_value = comp.get('value', 'NOT SET')
        is_locked = comp.get('locked', False)
        expected_value = expected['value']

        # Normalize values for comparison (handle different formats)
        def normalize_value(v):
            v = str(v).lower().replace('ohm', '').replace('f', 'F')
            v = v.replace('h', 'H')
            return v.strip()

        actual_norm = normalize_value(actual_value)
        expected_norm = normalize_value(expected_value)

        if actual_norm != expected_norm:
            print(f"[FAIL] {ref:15s} value mismatch: expected {expected_value}, got {actual_value}")
            violations.append(f"{ref}: Expected {expected_value}, found {actual_value}")
            all_pass = False
        elif not is_locked:
            print(f"[WARN] {ref:15s} value correct ({actual_value}) but NOT marked as locked")
            violations.append(f"{ref}: Not marked as locked in database")
            all_pass = False
        else:
            print(f"[OK]   {ref:15s} = {actual_value} (locked)")

    # Check board geometry
    print()
    print("Board Geometry:")
    print("-" * 70)

    metadata = db.get('metadata', {})
    board_size = metadata.get('board_size', 'NOT SET')
    frozen_state = metadata.get('frozen', False)

    if board_size != '80x50':
        print(f"[FAIL] Board size: expected 80x50mm, got {board_size}")
        violations.append(f"Board size: Expected 80x50, found {board_size}")
        all_pass = False
    else:
        print(f"[OK]   Board size = {board_size}mm")

    if not frozen_state:
        print(f"[WARN] Design not marked as frozen in metadata")
    else:
        print(f"[OK]   Design frozen = {frozen_state}")

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if all_pass:
        print("[PASS] All locked values correct")
        print(f"   {len(EXPECTED_LOCKS)} locked components verified")
        print(f"   Board geometry: {board_size}mm")
        return 0
    else:
        print("[FAIL] Locked value violations found")
        print(f"   {len(violations)} violation(s):")
        for v in violations:
            print(f"      - {v}")
        print()
        print("ACTION REQUIRED:")
        print("   1. Review violations above")
        print("   2. Fix design_database.yaml if values are incorrect")
        print("   3. Update FROZEN_STATE_REV_C4b.md if intentional change")
        print("   4. Re-run: python scripts/check_value_locks.py")
        return 1


if __name__ == "__main__":
    sys.exit(check_locked_values())
