#!/usr/bin/env python3
"""
SEDU BOM Completeness Checker - Verifies critical components are present (Database-Driven).

UPDATED: Now reads authoritative required component lists from design_database.yaml

This script checks that all MANDATORY components from IC datasheets are included in the BOM.
Prevents incomplete BOMs from reaching PCB fabrication.

Returns 0 if all required components present, 1 if missing components found.
"""

import sys
import csv
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "design_database.yaml"
BOM = ROOT / "hardware" / "BOM_Seed.csv"


def load_database():
    """Load design database from YAML."""
    if not DATABASE.exists():
        print(f"[bom_completeness] ERROR: Database not found: {DATABASE}")
        sys.exit(1)

    try:
        with open(DATABASE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"[bom_completeness] ERROR: Failed to parse database: {e}")
        sys.exit(1)


def load_bom(bom_path: Path) -> set:
    """Load BOM and return set of all component reference designators."""
    refs = set()
    with open(bom_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ref = row.get('Ref', '').strip()
            if ref and ref != 'Ref':  # Skip header duplicates
                refs.add(ref)
    return refs


def get_component_description(db, ref):
    """Get component description from database components or ics section."""
    # Check components section
    components = db.get('components', {})
    if ref in components:
        comp = components[ref]
        desc_parts = []

        if 'value' in comp:
            desc_parts.append(comp['value'])

        if 'description' in comp:
            desc_parts.append(comp['description'])
        elif 'part_number' in comp:
            desc_parts.append(comp['part_number'])

        return ' - '.join(desc_parts) if desc_parts else 'Component'

    # Check ICs section
    ics = db.get('ics', {})
    if ref in ics:
        ic = ics[ref]
        return ic.get('part', 'IC')

    return '(description not in database)'


def check_completeness():
    """Check BOM for required components per database definitions."""
    if not BOM.exists():
        print(f"[ERROR] BOM not found: {BOM}")
        return 1

    # Load database and BOM
    db = load_database()
    bom_refs = load_bom(BOM)

    # Get required components from database
    ic_required = db.get('ic_required_components', {})
    ics = db.get('ics', {})

    if not ic_required:
        print("[ERROR] No ic_required_components section in database")
        return 1

    all_pass = True
    missing_critical = []

    print("=" * 70)
    print("SEDU BOM COMPLETENESS VERIFICATION (Database-Driven)")
    print("=" * 70)
    print()

    print(f"[INFO] Database: {len(ic_required)} ICs with required component lists")
    print(f"[INFO] BOM: {len(bom_refs)} components found")
    print()

    for ic_ref, ic_data in sorted(ic_required.items()):
        required_refs = ic_data.get('required', [])
        ic_description = ic_data.get('description', 'Unknown IC')

        # Get IC part number from ics section
        ic_part = 'Unknown'
        if ic_ref in ics:
            ic_part = ics[ic_ref].get('part', 'Unknown')

        # NOTE: ICs are in the 'ics' section, not 'components', so they won't be in BOM
        # We check that required support components are present, regardless of IC presence

        print(f"{ic_ref} - {ic_part}:")
        print(f"  {ic_description}")
        print("-" * 70)

        # Check required components
        ic_pass = True
        missing_count = 0

        for ref in required_refs:
            comp_desc = get_component_description(db, ref)

            if ref in bom_refs:
                print(f"  [OK] {ref:20s} {comp_desc}")
            else:
                print(f"  [FAIL] {ref:20s} MISSING - {comp_desc}")
                missing_critical.append(f"{ic_ref} ({ic_part}): {ref} - {comp_desc}")
                ic_pass = False
                all_pass = False
                missing_count += 1

        if ic_pass:
            print(f"  [PASS] All {len(required_refs)} required components present")
        else:
            print(f"  [FAIL] {missing_count}/{len(required_refs)} required components MISSING!")
        print()

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    total_required = sum(len(ic_data.get('required', [])) for ic_data in ic_required.values())

    if all_pass:
        print("[PASS] BOM COMPLETENESS CHECK: PASS")
        print(f"   All {total_required} critical components present")
        print()
        print("DATABASE-DRIVEN BENEFITS:")
        print("   - Required component list auto-updates when database changes")
        print("   - Component descriptions pulled from single source")
        print("   - No hardcoded lists to maintain")
        return 0
    else:
        print("[FAIL] BOM COMPLETENESS CHECK: FAIL")
        print(f"   {len(missing_critical)} CRITICAL component(s) missing:")
        for item in missing_critical:
            print(f"      - {item}")
        print()
        print("ACTION REQUIRED:")
        print("   1. Add missing components to design_database.yaml components section")
        print("   2. Regenerate BOM: python scripts/generate_all.py")
        print("   3. Verify part numbers match datasheet requirements")
        print("   4. Re-run this script to verify fixes")
        print()
        print("NOTE: BOM is auto-generated from database. Do NOT edit BOM_Seed.csv directly.")
        return 1


if __name__ == "__main__":
    sys.exit(check_completeness())
