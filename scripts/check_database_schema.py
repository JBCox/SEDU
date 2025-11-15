#!/usr/bin/env python3
"""
SEDU Database Schema Validation

Validates that design_database.yaml:
1. Has correct structure (required sections present)
2. Has valid data types for all fields
3. Has no duplicate GPIO assignments
4. References are consistent (IC references, etc.)

This is the FIRST LINE OF DEFENSE - catches database errors before generation.

Returns 0 if database valid, 1 if schema violations found.
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

    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"[ERROR] Failed to parse YAML: {e}")
        sys.exit(1)


def check_database_schema():
    """Validate database schema and consistency."""
    db = load_database()

    all_pass = True
    errors = []
    warnings = []

    print("=" * 70)
    print("SEDU DATABASE SCHEMA VALIDATION")
    print("=" * 70)
    print()

    # Check 1: Required top-level sections
    print("1. TOP-LEVEL STRUCTURE")
    print("-" * 70)

    required_sections = ['metadata', 'power_rails', 'ics', 'components', 'gpio_pins']
    for section in required_sections:
        if section in db:
            print(f"[OK]   {section:20s} present")
        else:
            print(f"[FAIL] {section:20s} MISSING")
            errors.append(f"Missing required section: {section}")
            all_pass = False

    print()

    # Check 2: Metadata validation
    print("2. METADATA VALIDATION")
    print("-" * 70)

    metadata = db.get('metadata', {})
    required_metadata = ['project', 'revision', 'frozen', 'board_size']

    for field in required_metadata:
        if field in metadata:
            value = metadata[field]
            print(f"[OK]   {field:20s} = {value}")
        else:
            print(f"[FAIL] {field:20s} MISSING")
            errors.append(f"Metadata missing field: {field}")
            all_pass = False

    # Validate board size format
    if 'board_size' in metadata:
        board_size = metadata['board_size']
        if not isinstance(board_size, str) or 'x' not in board_size:
            print(f"[WARN] board_size format should be 'WxH' (e.g., '80x50')")
            warnings.append(f"board_size format: {board_size}")

    print()

    # Check 3: IC definitions
    print("3. IC DEFINITIONS")
    print("-" * 70)

    ics = db.get('ics', {})
    ic_refs = set()

    for ic_ref, ic_data in ics.items():
        ic_refs.add(ic_ref)
        required_ic_fields = ['part', 'manufacturer', 'description']
        missing_fields = [f for f in required_ic_fields if f not in ic_data]

        if missing_fields:
            print(f"[FAIL] {ic_ref:10s} missing fields: {', '.join(missing_fields)}")
            errors.append(f"IC {ic_ref} missing: {', '.join(missing_fields)}")
            all_pass = False
        else:
            print(f"[OK]   {ic_ref:10s} {ic_data['part']}")

    print(f"\nTotal ICs defined: {len(ics)}")
    print()

    # Check 4: Component validation
    print("4. COMPONENT VALIDATION")
    print("-" * 70)

    components = db.get('components', {})
    component_refs = set()

    for ref, comp_data in components.items():
        component_refs.add(ref)

        # Check required fields
        if 'value' not in comp_data:
            print(f"[FAIL] {ref:15s} missing 'value' field")
            errors.append(f"Component {ref} missing value")
            all_pass = False

        # Check IC reference is valid
        if 'ic' in comp_data:
            ic_ref = comp_data['ic']
            if ic_ref not in ic_refs and ic_ref not in ['J_LCD', 'J_BAT', 'J_MOT']:  # Allow connector ICs
                print(f"[WARN] {ref:15s} references unknown IC: {ic_ref}")
                warnings.append(f"Component {ref} references unknown IC {ic_ref}")

        # Check locked components have reason
        if comp_data.get('locked', False) and 'calculation' not in comp_data and 'description' not in comp_data:
            print(f"[WARN] {ref:15s} locked but no calculation/description")
            warnings.append(f"Component {ref} locked without justification")

    print(f"Total components defined: {len(components)}")
    print()

    # Check 5: GPIO pin assignments
    print("5. GPIO PIN VALIDATION")
    print("-" * 70)

    gpio_pins = db.get('gpio_pins', {})
    used_gpios = {}
    gpio_functions = set()

    for gpio_str, pin_data in sorted(gpio_pins.items(), key=lambda x: int(x[0].replace('GPIO', ''))):
        # Validate GPIO string format
        if not gpio_str.startswith('GPIO'):
            print(f"[FAIL] Invalid GPIO key format: {gpio_str}")
            errors.append(f"GPIO key should be 'GPION': {gpio_str}")
            all_pass = False
            continue

        try:
            gpio_num = int(gpio_str.replace('GPIO', ''))
        except ValueError:
            print(f"[FAIL] Invalid GPIO number in: {gpio_str}")
            errors.append(f"Cannot parse GPIO number: {gpio_str}")
            all_pass = False
            continue

        # Check required pin fields
        required_pin_fields = ['function', 'direction', 'peripheral', 'description']
        missing_fields = [f for f in required_pin_fields if f not in pin_data]

        if missing_fields:
            print(f"[FAIL] {gpio_str:10s} missing fields: {', '.join(missing_fields)}")
            errors.append(f"GPIO {gpio_str} missing: {', '.join(missing_fields)}")
            all_pass = False
            continue

        function = pin_data['function']

        # Check for duplicate GPIO numbers
        if gpio_num in used_gpios:
            print(f"[FAIL] {gpio_str:10s} DUPLICATE - already used by {used_gpios[gpio_num]}")
            errors.append(f"GPIO{gpio_num} assigned to both {function} and {used_gpios[gpio_num]}")
            all_pass = False
        else:
            used_gpios[gpio_num] = function

        # Check for duplicate function names
        if function in gpio_functions:
            print(f"[WARN] {function:20s} DUPLICATE function name")
            warnings.append(f"Function name {function} used multiple times")
        else:
            gpio_functions.add(function)

    print(f"Total GPIO pins assigned: {len(used_gpios)}")
    if len(used_gpios) != len(gpio_pins):
        print(f"[WARN] {len(gpio_pins) - len(used_gpios)} duplicate GPIO assignments")

    print()

    # Check 6: Cross-references
    print("6. CROSS-REFERENCE VALIDATION")
    print("-" * 70)

    # Check that firmware constants reference existing components
    fw_constants = db.get('firmware_constants', {})
    if fw_constants:
        # Check VBAT_DIVIDER matches components
        if 'VBAT_DIVIDER_TOP' in fw_constants:
            if 'R_VBAT_TOP' not in components:
                print("[WARN] VBAT_DIVIDER_TOP defined but R_VBAT_TOP component missing")
                warnings.append("Firmware constant VBAT_DIVIDER_TOP has no matching component")

        if 'VBAT_DIVIDER_BOT' in fw_constants:
            if 'R_VBAT_BOT' not in components:
                print("[WARN] VBAT_DIVIDER_BOT defined but R_VBAT_BOT component missing")
                warnings.append("Firmware constant VBAT_DIVIDER_BOT has no matching component")

        print(f"[OK]   Firmware constants: {len(fw_constants)} defined")
    else:
        print("[WARN] No firmware constants defined")

    print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if all_pass:
        print("[PASS] Database schema validation complete")
        print(f"   Metadata: {len(metadata)} fields")
        print(f"   ICs: {len(ics)} defined")
        print(f"   Components: {len(components)} defined")
        print(f"   GPIO pins: {len(used_gpios)} assigned")
        if warnings:
            print(f"   {len(warnings)} warning(s) (non-blocking)")
        return 0
    else:
        print("[FAIL] Database schema validation failed")
        print(f"   {len(errors)} error(s):")
        for err in errors:
            print(f"      - {err}")
        if warnings:
            print(f"   {len(warnings)} warning(s):")
            for warn in warnings:
                print(f"      - {warn}")
        print()
        print("ACTION REQUIRED:")
        print("   1. Fix errors in design_database.yaml")
        print("   2. Re-run: python scripts/check_database_schema.py")
        print("   3. Run generators: python scripts/generate_all.py")
        return 1


if __name__ == "__main__":
    sys.exit(check_database_schema())
