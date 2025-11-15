#!/usr/bin/env python3
"""
SEDU Pin Map Verification - Database-Driven

Validates that GPIO pin assignments in design_database.yaml are:
1. Correct (no conflicts, valid GPIO numbers for ESP32-S3)
2. Consistent with generated pins.h file

This script checks THE DATABASE and validates generated output matches it.

Returns 0 if pin map correct, 1 if violations found.
"""

import sys
import re
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


def parse_generated_pins_h(path: Path):
    """Parse generated pins.h to extract GPIO assignments."""
    if not path.exists():
        return {}

    pin_map = {}
    content = path.read_text(encoding='utf-8')

    # Match: #define FUNCTION_NAME   GPIO_NUM  // Description
    pattern = r'#define\s+(\w+)\s+(\d+)\s*//\s*(.*)'

    for match in re.finditer(pattern, content):
        function_name = match.group(1)
        gpio_num = int(match.group(2))
        description = match.group(3)
        pin_map[function_name] = gpio_num

    return pin_map


def check_pinmap():
    """Verify GPIO pin assignments in database."""
    db = load_database()
    gpio_pins = db.get('gpio_pins', {})

    # ESP32-S3 GPIO constraints
    VALID_GPIOS = set(range(0, 49))  # GPIO0-GPIO48
    # GPIO35-37 unavailable with PSRAM module
    UNAVAILABLE_WITH_PSRAM = {35, 36, 37}
    # Strapping pins (use with caution)
    STRAPPING_PINS = {0, 3, 45, 46}

    all_pass = True
    errors = []
    warnings = []

    print("=" * 70)
    print("SEDU PIN MAP VERIFICATION (Database-Driven)")
    print("=" * 70)
    print()

    # Check 1: Validate database GPIO assignments
    print("1. DATABASE GPIO VALIDATION")
    print("-" * 70)

    used_gpios = {}
    for gpio_str, pin_data in sorted(gpio_pins.items(), key=lambda x: int(x[0].replace('GPIO', ''))):
        gpio_num = int(gpio_str.replace('GPIO', ''))
        function = pin_data['function']

        # Check GPIO number is valid
        if gpio_num not in VALID_GPIOS:
            print(f"[FAIL] {function:20s} GPIO{gpio_num} - Invalid GPIO number")
            errors.append(f"{function}: GPIO{gpio_num} is not valid for ESP32-S3")
            all_pass = False
            continue

        # Check GPIO not in PSRAM conflict
        if gpio_num in UNAVAILABLE_WITH_PSRAM:
            print(f"[FAIL] {function:20s} GPIO{gpio_num} - Unavailable (PSRAM conflict)")
            errors.append(f"{function}: GPIO{gpio_num} unavailable with PSRAM module")
            all_pass = False
            continue

        # Warn about strapping pins
        if gpio_num in STRAPPING_PINS:
            print(f"[WARN] {function:20s} GPIO{gpio_num} - Strapping pin (use with caution)")
            warnings.append(f"{function}: GPIO{gpio_num} is a strapping pin")

        # Check for conflicts (same GPIO used twice)
        if gpio_num in used_gpios:
            print(f"[FAIL] {function:20s} GPIO{gpio_num} - CONFLICT with {used_gpios[gpio_num]}")
            errors.append(f"{function}: GPIO{gpio_num} already used by {used_gpios[gpio_num]}")
            all_pass = False
        else:
            print(f"[OK]   {function:20s} GPIO{gpio_num}")
            used_gpios[gpio_num] = function

    print()
    print(f"Total GPIO pins assigned: {len(used_gpios)}")
    print()

    # Check 2: Validate generated pins.h matches database
    print("2. GENERATED PINS.H VALIDATION")
    print("-" * 70)

    pins_h_path = Path(__file__).parent.parent / "firmware" / "include" / "pins.h"
    generated_pins = parse_generated_pins_h(pins_h_path)

    if not generated_pins:
        print("[FAIL] pins.h not found or empty - run: python scripts/generate_all.py")
        errors.append("pins.h not generated")
        all_pass = False
    else:
        # Verify each database entry appears in generated file
        for gpio_str, pin_data in gpio_pins.items():
            gpio_num = int(gpio_str.replace('GPIO', ''))
            function = pin_data['function']

            if function not in generated_pins:
                print(f"[FAIL] {function:20s} - Missing in generated pins.h")
                errors.append(f"{function}: Not found in generated pins.h")
                all_pass = False
            elif generated_pins[function] != gpio_num:
                print(f"[FAIL] {function:20s} - Mismatch: DB={gpio_num}, pins.h={generated_pins[function]}")
                errors.append(f"{function}: Database GPIO{gpio_num} != pins.h GPIO{generated_pins[function]}")
                all_pass = False
            else:
                print(f"[OK]   {function:20s} = GPIO{gpio_num}")

        # Check for extra pins in generated file not in database
        db_functions = set(pin_data['function'] for pin_data in gpio_pins.values())
        extra_functions = set(generated_pins.keys()) - db_functions
        if extra_functions:
            print()
            print(f"[WARN] {len(extra_functions)} extra definitions in pins.h not in database:")
            for func in sorted(extra_functions):
                print(f"       - {func}")
                warnings.append(f"pins.h contains {func} not in database")

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if all_pass:
        print("[PASS] Pin map verification complete")
        print(f"   {len(used_gpios)} GPIO pins assigned")
        print(f"   {len(generated_pins)} pins in generated pins.h")
        if warnings:
            print(f"   {len(warnings)} warning(s) (non-blocking)")
        return 0
    else:
        print("[FAIL] Pin map verification failed")
        print(f"   {len(errors)} error(s):")
        for err in errors:
            print(f"      - {err}")
        if warnings:
            print(f"   {len(warnings)} warning(s):")
            for warn in warnings:
                print(f"      - {warn}")
        print()
        print("ACTION REQUIRED:")
        print("   1. Fix GPIO assignments in design_database.yaml")
        print("   2. Run: python scripts/generate_all.py")
        print("   3. Re-run: python scripts/check_pinmap.py")
        return 1


if __name__ == "__main__":
    sys.exit(check_pinmap())
