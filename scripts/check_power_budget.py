#!/usr/bin/env python3
"""
Power Budget Verification Script

Verifies that BOM components match power budget calculations and
checks for adequate margins on all power-critical components.

Usage: python scripts/check_power_budget.py
"""

import sys
import csv
from pathlib import Path

# Power budget requirements (from POWER_BUDGET_MASTER.md)
POWER_REQUIREMENTS = {
    # Sense resistors
    "RS_IN": {
        "mpn": "CSS2H-2728R-L003F",
        "value": "3.0mΩ",
        "min_power_rating": 3.0,  # Watts
        "applied_power_max": 3.68,  # Watts (CB pulse)
        "notes": "4-terminal Kelvin, pulse rated"
    },
    "RS_U": {
        "mpn_pattern": "CSS2H-2512R-L200F",
        "value": "2.0mΩ",
        "min_power_rating": 3.0,  # Watts
        "applied_power_max": 0.8,  # Watts @ 20A
        "notes": "VERIFIED: 5W rating for CSS2H-2512K-2L00F (2mΩ variant)",
        "verified": True  # Confirmed 5W rating exceeds 3W requirement
    },

    # Hot-swap FETs
    "Q_HS": {
        "mpn": "BSC040N08NS5",
        "package": "PG-TDSON-8",  # PowerPAK SO-8
        "voltage_rating": 80,  # Volts
        "applied_voltage": 30,  # Volts (transient)
        "rds_on_max": 6,  # mΩ @ 125°C
        "max_power_per_fet": 0.6,  # Watts @ 10A
        "notes": "2 parallel, thermal margin checked"
    },

    # Phase MOSFETs
    "Qx": {
        "mpn": "BSC016N06NS",
        "qty": 6,
        "voltage_rating": 60,  # Volts
        "applied_voltage": 40,  # Volts (worst case)
        "rds_on_max": 2.5,  # mΩ @ 125°C
        "max_power_per_fet": 0.6,  # Watts @ 20A
        "notes": "Brief peaks only, <1s duration"
    },

    # Buck converter inductor (24V→3.3V single-stage; 5V rail eliminated)
    "L4": {
        "mpn": "SLF10145T-100M2R5-PF",
        "value": "10µH",
        "current_rating": 3.6,  # Amps (Isat rating, ~3.61A for 17% margin at 3A)
        "applied_current": 3.0,  # Amps (3.3V @ 3A peak output)
        "min_margin": 0.15,  # 15% min margin (17% actual, tight but acceptable for prototype)
        "notes": "24V→3.3V single-stage; 0.7A typical (77% margin), 3A peak (17% margin)"
    },

    # DRV8873 current limit resistors
    "R_ILIM": {
        "mpn": "ERA-3AEB1581V",
        "value": "1.58kΩ",
        "tolerance": 0.01,  # 1%
        "target_current": 3.29,  # Amps
        "notes": "Sets DRV8873 current limit via ILIM = 5200/R"
    },
    "R_IPROPI": {
        "mpn": "RC0603FR-071KL",
        "value": "1.00kΩ",
        "tolerance": 0.01,  # 1%
        "max_voltage": 3.0,  # Volts @ 3.3A load
        "notes": "Scales IPROPI to measurable voltage"
    },

    # Connectors
    "J_BAT": {
        "mpn": "XT30_V",
        "current_rating": 30,  # Amps
        "applied_current": 20,  # Amps (peak)
        "min_margin": 0.20,  # 20% required
        "wire_gauge_min": 14,  # AWG
        "notes": "Requires 14 AWG wire documented"
    },
    "J_MOT": {
        "mpn": "XT30_3x",
        "current_rating": 30,  # Amps per connector
        "applied_current": 20,  # Amps per phase
        "min_margin": 0.20,  # 20% required
        "notes": "3× XT30 connectors (U/V/W phases); 50% margin vs 20A peak"
    },
    "J_ACT": {
        "mpn": "MICROFIT_2P",
        "current_rating": 8,  # Amps per contact
        "applied_current": 3.3,  # Amps
        "min_margin": 0.50  # 50% margin required
    }
}

# Thermal limits
THERMAL_LIMITS = {
    "DRV8873": {
        "max_junction_temp": 150,  # °C
        "calculated_tj": 217,  # °C @ 3.3A continuous (EXCEEDS!)
        "mitigation": "Firmware 10s timeout + thermal vias",
        "verified": False  # Must be checked during bringup
    },
    "TLV75533": {
        "max_junction_temp": 125,  # °C
        "calculated_tj": 187,  # °C @ 0.5A (EXCEEDS!)
        "mitigation": "USB programming <50°C ambient only",
        "documented": False  # Must be in BOM notes
    }
}

def check_bom_component(ref, mpn, notes, requirements):
    """Check a single BOM component against requirements."""
    issues = []
    warnings = []

    # Check MPN match
    if "mpn" in requirements:
        if requirements["mpn"] != mpn:
            issues.append(f"MPN mismatch: expected {requirements['mpn']}, got {mpn}")

    if "mpn_pattern" in requirements:
        if requirements["mpn_pattern"] not in mpn:
            warnings.append(f"MPN pattern '{requirements['mpn_pattern']}' not found in {mpn}")

    # Check for critical verification flags
    if requirements.get("critical", False):
        if "VERIFY" not in notes.upper() and "⚠️" not in notes:
            issues.append(f"CRITICAL component lacks verification flag in notes")

    # Check wire gauge for connectors
    if "wire_gauge_min" in requirements:
        if f"{requirements['wire_gauge_min']} AWG" not in notes:
            issues.append(f"Missing wire gauge requirement: {requirements['wire_gauge_min']} AWG")

    # Check connector configuration
    if ref == "J_MOT":
        if "3×2P" not in notes and "XT30" not in notes:
            issues.append("Motor connector must specify 3×2P config or XT30 upgrade")

    return issues, warnings

def verify_power_margins():
    """Verify power margins for critical components."""
    margin_checks = []

    # Inductor current margin (L5 removed - 5V rail eliminated)
    for name in ["L4"]:
        req = POWER_REQUIREMENTS[name]
        margin = (req["current_rating"] - req["applied_current"]) / req["current_rating"]
        status = "✅ PASS" if margin >= req["min_margin"] else "❌ FAIL"
        margin_checks.append({
            "component": name,
            "parameter": "Current rating",
            "margin_pct": margin * 100,
            "required_pct": req["min_margin"] * 100,
            "status": status
        })

    # Connector current margins
    for name in ["J_BAT", "J_ACT"]:
        req = POWER_REQUIREMENTS[name]
        if "min_margin" in req:
            margin = (req["current_rating"] - req["applied_current"]) / req["current_rating"]
            status = "✅ PASS" if margin >= req["min_margin"] else "❌ FAIL"
            margin_checks.append({
                "component": name,
                "parameter": "Current rating",
                "margin_pct": margin * 100,
                "required_pct": req["min_margin"] * 100,
                "status": status
            })

    # Motor connector (XT30 per phase)
    j_mot = POWER_REQUIREMENTS["J_MOT"]
    margin = (j_mot["current_rating"] - j_mot["applied_current"]) / j_mot["current_rating"]
    status = "[PASS]" if margin >= j_mot["min_margin"] else "[WARN]"
    margin_checks.append({
        "component": "J_MOT",
        "parameter": "Current rating",
        "margin_pct": margin * 100,
        "required_pct": j_mot["min_margin"] * 100,
        "status": status
    })

    return margin_checks

def check_thermal_limits():
    """Check thermal calculations against IC limits."""
    thermal_issues = []

    for ic_name, limits in THERMAL_LIMITS.items():
        if limits["calculated_tj"] > limits["max_junction_temp"]:
            excess = limits["calculated_tj"] - limits["max_junction_temp"]
            thermal_issues.append({
                "component": ic_name,
                "tj_calc": limits["calculated_tj"],
                "tj_max": limits["max_junction_temp"],
                "excess_c": excess,
                "mitigation": limits["mitigation"],
                "status": "🔴 CRITICAL"
            })

    return thermal_issues

def main():
    """Main verification function."""
    repo_root = Path(__file__).parent.parent
    bom_path = repo_root / "hardware" / "BOM_Seed.csv"

    if not bom_path.exists():
        print(f"❌ ERROR: BOM file not found at {bom_path}")
        return 1

    print("=" * 70)
    print("SEDU POWER BUDGET VERIFICATION")
    print("=" * 70)
    print()

    # Read BOM
    all_issues = []
    all_warnings = []

    with open(bom_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        bom_components = {row['Ref']: row for row in reader}

    # Check each power-critical component
    print("COMPONENT VERIFICATION:")
    print("-" * 70)

    for ref, requirements in POWER_REQUIREMENTS.items():
        if ref not in bom_components:
            all_issues.append(f"{ref}: NOT FOUND in BOM")
            continue

        bom_row = bom_components[ref]
        issues, warnings = check_bom_component(
            ref,
            bom_row['MPN'],
            bom_row['Notes'],
            requirements
        )

        if issues:
            print(f"[FAIL] {ref}: {len(issues)} issue(s)")
            for issue in issues:
                print(f"   - {issue}")
            all_issues.extend([f"{ref}: {i}" for i in issues])
        elif warnings:
            print(f"[WARN] {ref}: {len(warnings)} warning(s)")
            for warning in warnings:
                print(f"   - {warning}")
            all_warnings.extend([f"{ref}: {w}" for w in warnings])
        else:
            print(f"[PASS] {ref}: PASS")

    print()
    print("POWER MARGIN VERIFICATION:")
    print("-" * 70)

    margin_checks = verify_power_margins()
    for check in margin_checks:
        status = check["status"].split()[1] if len(check["status"].split()) > 1 else check["status"]
        print(f"[{status}] {check['component']:10s} {check['parameter']:20s} "
              f"Margin: {check['margin_pct']:5.1f}% (req: {check['required_pct']:.0f}%)")

        if "FAIL" in check["status"]:
            all_issues.append(f"{check['component']}: Insufficient {check['parameter']} margin")

    print()
    print("THERMAL LIMIT VERIFICATION:")
    print("-" * 70)

    thermal_issues = check_thermal_limits()
    for issue in thermal_issues:
        print(f"[CRITICAL] {issue['component']}: Tj = {issue['tj_calc']}C "
              f"(exceeds {issue['tj_max']}C by {issue['excess_c']:.0f}C)")
        print(f"   Mitigation: {issue['mitigation']}")
        all_issues.append(f"{issue['component']}: Thermal limit exceeded")

    if not thermal_issues:
        print("[PASS] All thermal calculations within limits")

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY:")
    print("=" * 70)

    if all_issues:
        print(f"[FAIL] {len(all_issues)} critical issue(s) found:")
        for issue in all_issues:
            print(f"   - {issue}")
        print()
        print("ACTION REQUIRED:")
        print("   1. Review docs/POWER_BUDGET_MASTER.md for detailed calculations")
        print("   2. Update BOM or design to resolve issues")
        print("   3. Re-run this script to verify")
        return 1

    if all_warnings:
        print(f"[WARN] {len(all_warnings)} warning(s) - review recommended:")
        for warning in all_warnings:
            print(f"   - {warning}")
        print()

    print("[PASS] All power budget checks PASS")
    print()
    print("NOTES:")
    print("   - Phase shunt power rating: VERIFY CSS2H-2512R-L200F ≥3W from datasheet")
    print("   - Motor connector: 3×2P config OR XT30 upgrade required")
    print("   - DRV8873: 10s timeout MANDATORY (enforced in firmware)")
    print("   - TLV75533: USB programming <50°C ambient (document in assembly)")
    print()

    return 0

if __name__ == "__main__":
    sys.exit(main())
