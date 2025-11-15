#!/usr/bin/env python3
"""Ensure required net labels exist for firmware pins and connectors (Database-Driven).

UPDATED: Now reads authoritative values from design_database.yaml

Checks:
1. Database defines gpio_pins and power_rails
2. Net Labels CSV contains all GPIO function names
3. Net Labels CSV contains all power rail names
4. Net Labels CSV contains common nets (GND, motor phases)

Exit codes:
 0 = OK, 1 = violations found
"""
from __future__ import annotations

import csv
import pathlib
import sys
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATABASE = ROOT / "design_database.yaml"
NETS = ROOT / "hardware" / "Net_Labels.csv"


def load_database():
    """Load design database from YAML."""
    if not DATABASE.exists():
        print(f"[nets_vs_pins] ERROR: Database not found: {DATABASE}")
        sys.exit(1)

    try:
        with open(DATABASE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"[nets_vs_pins] ERROR: Failed to parse database: {e}")
        sys.exit(1)


def load_nets(path: pathlib.Path) -> set[str]:
    """Load net names from Net_Labels.csv."""
    nets: set[str] = set()
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            n = row.get("Net") or row.get("net") or row.get("label")
            if n:
                nets.add(n.strip())
    return nets


def build_required_nets(db):
    """Build required net list from database.

    Returns:
        set[str]: Set of required net names
        dict: Categorized nets for reporting
    """
    required = set()
    categorized = {
        'power': set(),
        'gpio': set(),
        'common': set(),
    }

    # 1. Power rails
    power_rails = db.get('power_rails', {})
    for rail_name in power_rails.keys():
        required.add(rail_name)
        categorized['power'].add(rail_name)

    # 2. GPIO function names
    gpio_pins = db.get('gpio_pins', {})
    for pin_data in gpio_pins.values():
        function = pin_data.get('function', '')
        if function:
            required.add(function)
            categorized['gpio'].add(function)

    # 3. Common nets (hardcoded - these are physical nets not tied to specific GPIOs)
    common_nets = ['GND', 'MOTOR_PH_U', 'MOTOR_PH_V', 'MOTOR_PH_W']
    for net in common_nets:
        required.add(net)
        categorized['common'].add(net)

    return required, categorized


def main() -> int:
    rc = 0

    # Load database (authoritative source)
    db = load_database()

    # Build required net list from database
    required_nets, categorized = build_required_nets(db)

    print(f"[nets_vs_pins] Database: {len(categorized['power'])} power rails")
    print(f"[nets_vs_pins] Database: {len(categorized['gpio'])} GPIO functions")
    print(f"[nets_vs_pins] Database: {len(categorized['common'])} common nets")
    print(f"[nets_vs_pins] Total required nets: {len(required_nets)}")
    print()

    # Load actual net labels file
    if not NETS.exists():
        print("[nets_vs_pins] FAIL: hardware/Net_Labels.csv not found (schematic entry not started)")
        return 1

    nets = load_nets(NETS)
    print(f"[nets_vs_pins] Net_Labels.csv: {len(nets)} nets found")
    print()

    # Check for missing nets
    missing = sorted(n for n in required_nets if n not in nets)

    if missing:
        print(f"[nets_vs_pins] FAIL: {len(missing)} missing required net labels:")

        # Categorize missing nets for better reporting
        missing_power = sorted(n for n in missing if n in categorized['power'])
        missing_gpio = sorted(n for n in missing if n in categorized['gpio'])
        missing_common = sorted(n for n in missing if n in categorized['common'])

        if missing_power:
            print(f"\n  Power Rails ({len(missing_power)}):")
            for n in missing_power:
                print(f"    - {n}")

        if missing_gpio:
            print(f"\n  GPIO Functions ({len(missing_gpio)}):")
            for n in missing_gpio:
                print(f"    - {n}")

        if missing_common:
            print(f"\n  Common Nets ({len(missing_common)}):")
            for n in missing_common:
                print(f"    - {n}")

        rc = 1
    else:
        print("[nets_vs_pins] PASS: Net labels cover all required signals")

    # Check for unexpected nets (informational only, not an error)
    unexpected = sorted(n for n in nets if n not in required_nets)
    if unexpected:
        print(f"\n[nets_vs_pins] INFO: {len(unexpected)} nets in CSV not in database (may be valid):")
        for n in unexpected[:10]:  # Show first 10 only
            print(f"  - {n}")
        if len(unexpected) > 10:
            print(f"  ... and {len(unexpected) - 10} more")

    return rc


if __name__ == "__main__":
    sys.exit(main())
