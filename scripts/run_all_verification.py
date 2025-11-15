#!/usr/bin/env python3
"""
Run all SEDU verification scripts in sequence.
Use this to verify system integrity when resuming work.

Returns 0 if all scripts pass, 1 if any fail.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"

# All verification scripts in recommended order
VERIFICATION_SCRIPTS = [
    "check_database_schema.py",
    "check_value_locks.py",
    "check_pinmap.py",
    "check_netlabels_vs_pins.py",
    "check_kicad_outline.py",
    "check_5v_elimination.py",
    "check_ladder_bands.py",
    "verify_power_calcs.py",
    "check_bom_completeness.py",
]

def main():
    print("=" * 70)
    print("SEDU VERIFICATION SUITE - RUNNING ALL SCRIPTS")
    print("=" * 70)
    print()

    results = []

    for idx, script_name in enumerate(VERIFICATION_SCRIPTS, 1):
        script_path = SCRIPTS_DIR / script_name

        if not script_path.exists():
            print(f"[{idx}/{len(VERIFICATION_SCRIPTS)}] {script_name:30s} [!] NOT FOUND")
            results.append((script_name, "MISSING"))
            continue

        print(f"[{idx}/{len(VERIFICATION_SCRIPTS)}] Running {script_name}...")
        print("-" * 70)

        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=ROOT,
            capture_output=False,  # Show output in real-time
        )

        if result.returncode == 0:
            status = "[OK] PASS"
            results.append((script_name, "PASS"))
        else:
            status = "[FAIL] FAIL"
            results.append((script_name, "FAIL"))

        print()
        print(f"[{idx}/{len(VERIFICATION_SCRIPTS)}] {script_name:30s} {status}")
        print()

    # Summary
    print("=" * 70)
    print("VERIFICATION SUITE SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, status in results if status == "PASS")
    failed = sum(1 for _, status in results if status == "FAIL")
    missing = sum(1 for _, status in results if status == "MISSING")

    for script_name, status in results:
        if status == "PASS":
            print(f"  [OK]   {script_name}")
        elif status == "FAIL":
            print(f"  [FAIL] {script_name}")
        else:
            print(f"  [!]    {script_name} (not found)")

    print()
    print(f"Total: {passed}/{len(VERIFICATION_SCRIPTS)} passed")

    if failed > 0 or missing > 0:
        print()
        print("[FAIL] VERIFICATION SUITE FAILED")
        if failed > 0:
            print(f"   {failed} script(s) failed")
        if missing > 0:
            print(f"   {missing} script(s) missing")
        return 1
    else:
        print()
        print("[PASS] VERIFICATION SUITE PASSED")
        print("   All verification scripts passed successfully")
        print("   System integrity verified")
        return 0

if __name__ == "__main__":
    sys.exit(main())
