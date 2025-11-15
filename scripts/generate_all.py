#!/usr/bin/env python3
"""
SEDU Design File Generator - Master Script

This script generates ALL derived files from the single-source-of-truth database.

Usage:
    python scripts/generate_all.py

Generates:
    - hardware/BOM_Seed.csv (from components)
    - firmware/include/pins.h (from gpio_pins)
    - hardware/Net_Labels.csv (from gpio_pins + power_rails)
    - Component_Report.md (from components + ics)
    - docs/POWER_BUDGET_MASTER.md (from components power specs)

IMPORTANT: Never edit generated files directly - edit design_database.yaml
and run this script to regenerate.
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import individual generators
try:
    from generate_bom import generate_bom
    from generate_pins_h import generate_pins_h
    from generate_netlabels import generate_netlabels
    from generate_component_report import generate_component_report
except ImportError as e:
    print(f"[ERROR] Failed to import generators: {e}")
    print("Make sure all generator scripts exist in scripts/ directory")
    sys.exit(1)


def main():
    """Run all generators in sequence."""
    print("=" * 70)
    print("SEDU DESIGN FILE GENERATOR")
    print("=" * 70)
    print()
    print("Generating all derived files from design_database.yaml...")
    print()

    generators = [
        ("BOM (hardware/BOM_Seed.csv)", generate_bom),
        ("pins.h (firmware/include/pins.h)", generate_pins_h),
        ("Net Labels (hardware/Net_Labels.csv)", generate_netlabels),
        ("Component Report (Component_Report.md)", generate_component_report),
    ]

    success_count = 0
    fail_count = 0

    for name, generator_func in generators:
        try:
            print(f"[{success_count + fail_count + 1}/{len(generators)}] Generating {name}...")
            generator_func()
            print(f"    [OK] SUCCESS")
            success_count += 1
        except Exception as e:
            print(f"    [FAIL] FAILED: {e}")
            fail_count += 1
        print()

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"[OK] Successful: {success_count}/{len(generators)}")
    if fail_count > 0:
        print(f"[FAIL] Failed:     {fail_count}/{len(generators)}")
        print()
        print("[FAIL] Some generators failed. Fix errors and re-run.")
        return 1
    else:
        print()
        print("[PASS] All files generated successfully!")
        print()
        print("Next steps:")
        print("  1. Review generated files for correctness")
        print("  2. Run verification scripts: python scripts/check_value_locks.py")
        print("  3. Commit changes: git add -u && git commit")
        return 0


if __name__ == "__main__":
    sys.exit(main())
