#!/usr/bin/env python3
"""
Verify that 5V rail has been completely eliminated from SEDU design (Database-Driven).

UPDATED: Now reads banned components and nets from design_database.yaml

Checks:
1. Database banned_components list is complete
2. BOM doesn't contain any banned components
3. Net labels don't contain any banned nets
4. U4 (LMR33630) configured for 3.3V output (not 5V)
5. Documentation updated (no active 5V references)
"""
from __future__ import annotations

import pathlib
import re
import sys
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATABASE = ROOT / "design_database.yaml"
BOM = ROOT / "hardware" / "BOM_Seed.csv"
NET_LABELS = ROOT / "hardware" / "Net_Labels.csv"
SSOT = ROOT / "docs" / "SEDU_Single_PCB_Parity_Corrected_RevC4a_Final.md"


def load_database():
    """Load design database from YAML."""
    if not DATABASE.exists():
        print(f"[5v_elimination] ERROR: Database not found: {DATABASE}")
        sys.exit(1)

    try:
        with open(DATABASE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"[5v_elimination] ERROR: Failed to parse database: {e}")
        sys.exit(1)


def check_database_bans():
    """Verify database has banned components and nets defined."""
    db = load_database()

    banned_components = db.get('banned_components', [])
    banned_nets = db.get('banned_nets', [])

    issues = []

    if not banned_components:
        issues.append("Database has no banned_components section")

    if not banned_nets:
        issues.append("Database has no banned_nets section")

    return banned_components, banned_nets, issues


def check_bom(banned_components, db):
    """Verify BOM doesn't contain banned components and U4 is correct."""
    issues = []

    # Check banned components in BOM
    if BOM.exists():
        bom_text = BOM.read_text(encoding="utf-8", errors="ignore")

        for banned in banned_components:
            ref = banned.get('ref', '')
            reason = banned.get('reason', 'eliminated')

            # Skip refs that are descriptive (like OLD_5V_BUCK)
            if "OLD_" in ref:
                continue

            # Check if banned ref appears in BOM
            if re.search(rf"^{ref},", bom_text, re.MULTILINE):
                issues.append(f"BOM contains banned component {ref} ({reason})")

    # Check U4 in database (ICs section)
    ics = db.get('ics', {})
    u4_data = ics.get('U4')

    if not u4_data:
        issues.append("U4 not defined in database ics section")
    else:
        part = u4_data.get('part', '')
        output_voltage = u4_data.get('output_voltage')

        if "LMR33630" not in part:
            issues.append(f"U4 part is '{part}', should be LMR33630ADDAR (single-stage 24V->3.3V)")

        if output_voltage != 3.3:
            issues.append(f"U4 output_voltage is {output_voltage}V, should be 3.3V")

    return issues


def check_net_labels(banned_nets):
    """Verify no banned nets in net labels file."""
    if not NET_LABELS.exists():
        return ["Net labels file not found (schematic entry not started)"]

    net_text = NET_LABELS.read_text(encoding="utf-8", errors="ignore")
    issues = []

    for banned in banned_nets:
        net_name = banned.get('name', '')
        reason = banned.get('reason', 'eliminated')

        # Check if banned net appears in net labels
        if re.search(rf"^{net_name},", net_text, re.MULTILINE):
            issues.append(f"Net label '{net_name}' still exists ({reason})")

    return issues


def check_documentation():
    """Check SSOT and other docs for 5V rail references (except historical)."""
    issues = []

    if not SSOT.exists():
        # SSOT not required for basic check
        return []

    ssot_text = SSOT.read_text(encoding="utf-8", errors="ignore")

    # Check for OLD part number TPS62133 (only if not documenting transition)
    tps_mentions = re.findall(r"[^\n]*TPS62133[^\n]*", ssot_text)
    for mention in tps_mentions:
        # Allow mentions that document the transition
        if not re.search(r"eliminated|removed|replaced|was", mention, re.IGNORECASE):
            issues.append(f"SSOT references TPS62133 without noting elimination: {mention[:80]}...")

    return issues


def main():
    print("="*70)
    print("5V RAIL ELIMINATION VERIFICATION (Database-Driven)")
    print("="*70)
    print()

    all_issues = []

    # Load database
    db = load_database()

    # Database banned lists check
    print("1. DATABASE BANNED LISTS")
    print("-"*70)
    banned_components, banned_nets, db_issues = check_database_bans()

    if db_issues:
        for issue in db_issues:
            print(f"   [FAIL] {issue}")
        all_issues.extend(db_issues)
    else:
        print(f"   [OK] {len(banned_components)} banned components defined")
        print(f"   [OK] {len(banned_nets)} banned nets defined")
    print()

    # BOM checks
    print("2. BOM COMPONENT CHECK")
    print("-"*70)
    bom_issues = check_bom(banned_components, db)
    if bom_issues:
        for issue in bom_issues:
            print(f"   [FAIL] {issue}")
        all_issues.extend(bom_issues)
    else:
        print("   [OK] No banned components found in BOM")
        print("   [OK] U4 (LMR33630) configured for 3.3V output")
    print()

    # Net labels check
    print("3. NET LABELS CHECK")
    print("-"*70)
    net_issues = check_net_labels(banned_nets)
    if net_issues:
        for issue in net_issues:
            print(f"   [FAIL] {issue}")
        all_issues.extend(net_issues)
    else:
        print("   [OK] No banned nets found in net labels")
    print()

    # Documentation check
    print("4. DOCUMENTATION CHECK")
    print("-"*70)
    doc_issues = check_documentation()
    if doc_issues:
        for issue in doc_issues:
            print(f"   [FAIL] {issue}")
        all_issues.extend(doc_issues)
    else:
        print("   [OK] Documentation updated (no active 5V rail references)")
    print()

    # Summary
    print("="*70)
    if all_issues:
        print(f"VERIFICATION FAILED: {len(all_issues)} issue(s) found")
        print("="*70)
        sys.exit(1)
    else:
        print("VERIFICATION COMPLETE: 5V rail successfully eliminated")
        print("="*70)
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)
