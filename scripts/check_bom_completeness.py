#!/usr/bin/env python3
"""
SEDU BOM Completeness Checker - Verifies critical datasheet-required components are present.

This script checks that all MANDATORY components from IC datasheets are included in the BOM.
Prevents incomplete BOMs from reaching PCB fabrication.

Returns 0 if all required components present, 1 if missing components found.
"""

import sys
import csv
from pathlib import Path

# Critical datasheet-required components (per TI/Espressif design guidelines)
REQUIRED_COMPONENTS = {
    "ESP32-S3-WROOM-1": {
        "IC": "U1",
        "required": {
            "R_CHIP_PU": "10k CHIP_PU pull-up (Espressif mandatory - reliable boot)",
            "C_CHIP_PU": "1uF CHIP_PU RC delay (Espressif mandatory - power sequencing)",
            "C_VDD_CPU": "100nF VDD3P3_CPU decoupling (pin 46)",
            "C_VDD_RTC": "100nF VDD3P3_RTC decoupling (pin 20)",
            "C_VDD_SPI": "1uF VDD_SPI decoupling",
            "C_VDD3P3_1": "100nF VDD3P3 decoupling (pin 37)",
            "C_VDD3P3_2": "100nF VDD3P3_0 decoupling (pin 39)",
            "FB_VDDA": "Ferrite bead for VDDA filter (ADC accuracy)",
            "C_VDDA_10u": "10uF VDDA bulk capacitor",
            "C_VDDA_100n": "100nF VDDA bypass capacitor",
        },
        "recommended": {
            "C_VDD3P3_3": "Additional 100nF VDD3P3 decoupling",
        }
    },
    "DRV8353RS": {
        "IC": "U2",
        "required": {
            "C_CPLCPH": "47nF charge pump capacitor",
            "C_VCP": "1uF VCP bypass",
            "C_VGLS": "1uF VGLS bypass",
            "C_DVDD": "1uF DVDD bypass",
            "C_DRV8353_VM1": "100nF VM bypass (TI datasheet mandatory)",
            "C_DRV8353_VM2": "22uF VM bulk (TI datasheet >=10uF total)",
        },
        "recommended": {
            "C_DRV8353_VM3": "22uF additional VM bulk (margin)",
            "R_DRV8353_nFAULT": "10k nFAULT pull-up (read fault status)",
        }
    },
    "DRV8873-Q1": {
        "IC": "U3",
        "required": {
            "R_ILIM": "1.58k current limit setting",
            "R_IPROPI": "1k IPROPI scaling",
            "C_DRV8873_VM1": "100nF VM bypass (TI datasheet mandatory)",
            "C_DRV8873_VM2": "22uF VM bulk (TI datasheet mandatory)",
            "C_DRV8873_DVDD": "1uF DVDD bypass (TI datasheet mandatory)",
        },
        "recommended": {
            "R_DRV8873_nFAULT": "10k nFAULT pull-up (read fault status)",
        }
    },
    "LMR33630ADDAR": {
        "IC": "U4",
        "required": {
            "L4": "10uH inductor",
            "C4x": "Output capacitors (>=44uF total)",
            "C4IN_A": "10uF input bulk",
            "C4IN_B": "220nF input HF bypass",
            "C_BOOT": "100nF bootstrap cap (TI datasheet mandatory)",
            "C_VCC": "1uF VCC bypass (TI datasheet mandatory)",
            "RFBT": "100k feedback top resistor",
            "RFBB": "43.2k feedback bottom resistor",
        },
        "recommended": {}
    },
    "LM5069-1": {
        "IC": "U6",
        "required": {
            "RS_IN": "3.0 milliohm current sense resistor",
            "Q_HS": "Hot-swap pass FETs (2x)",
            "CDVDT": "33nF dv/dt control",
            "RUV_TOP": "140k UV divider top",
            "RUV_BOT": "10k UV divider bottom",
            "ROV_TOP": "221k OV divider top",
            "ROV_BOT": "10k OV divider bottom",
            "C_LM5069_VDD": "1uF VDD bypass (gate driver stability)",
        },
        "recommended": {
            "RPWR": "15.8k power limit resistor (optional if power limiting not used)",
            "R_PGD_PU": "100k PGD pull-up (read power good status)",
        }
    },
    "TPS22919": {
        "IC": "U7",
        "required": {
            "C_TPS22919_IN": "1uF input cap (VIN-GND)",
            "C_TPS22919_OUT": "1uF output cap (VOUT-GND)",
        },
        "recommended": {}
    },
    "TLV75533": {
        "IC": "U8",
        "required": {
            "C_TLV75533_IN": "1uF input cap (TI datasheet mandatory)",
            "C_TLV75533_OUT": "10uF output cap (TI datasheet mandatory - stability)",
        },
        "recommended": {}
    },
    "LCD-GC9A01": {
        "IC": "J_LCD",
        "required": {
            "R_SCK": "22 ohm SCK series resistor",
            "R_MOSI": "22 ohm MOSI series resistor",
            "Q_LED": "Backlight sink transistor",
            "R_LEDK": "Backlight current limit resistor (prevents overcurrent)",
        },
        "recommended": {
            "FB_LED": "600 ohm ferrite bead (EMI filtering)",
        }
    },
}


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


def check_completeness():
    """Check BOM for required components per datasheets."""
    bom_path = Path(__file__).parent.parent / "hardware" / "BOM_Seed.csv"

    if not bom_path.exists():
        print(f"[ERROR] BOM not found: {bom_path}")
        return 1

    bom_refs = load_bom(bom_path)

    all_pass = True
    missing_critical = []
    missing_recommended = []

    print("=" * 70)
    print("SEDU BOM COMPLETENESS VERIFICATION")
    print("=" * 70)
    print()

    for ic_name, ic_data in REQUIRED_COMPONENTS.items():
        ic_ref = ic_data["IC"]
        required = ic_data["required"]
        recommended = ic_data.get("recommended", {})

        # Check if IC is in BOM
        if ic_ref not in bom_refs:
            print(f"[SKIP] {ic_name} ({ic_ref}) not found in BOM - skipping checks")
            continue

        print(f"{ic_name} ({ic_ref}):")
        print("-" * 70)

        # Check required components
        ic_pass = True
        for ref, description in required.items():
            if ref in bom_refs:
                print(f"  [OK] {ref:20s} {description}")
            else:
                print(f"  [FAIL] {ref:20s} MISSING - {description}")
                missing_critical.append(f"{ic_name}: {ref} ({description})")
                ic_pass = False
                all_pass = False

        # Check recommended components
        for ref, description in recommended.items():
            if ref in bom_refs:
                print(f"  [OK] {ref:20s} {description}")
            else:
                print(f"  [WARN] {ref:20s} MISSING (recommended) - {description}")
                missing_recommended.append(f"{ic_name}: {ref} ({description})")

        if ic_pass:
            print(f"  [PASS] All required components present")
        else:
            print(f"  [FAIL] Missing required components!")
        print()

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if all_pass:
        print("[PASS] BOM COMPLETENESS CHECK: PASS")
        print(f"   All {sum(len(ic['required']) for ic in REQUIRED_COMPONENTS.values())} critical components present")
        if missing_recommended:
            print(f"   [WARN]  {len(missing_recommended)} recommended component(s) missing (non-blocking)")
            for item in missing_recommended:
                print(f"      - {item}")
        return 0
    else:
        print("[FAIL] BOM COMPLETENESS CHECK: FAIL")
        print(f"   {len(missing_critical)} CRITICAL component(s) missing:")
        for item in missing_critical:
            print(f"      - {item}")
        print()
        print("ACTION REQUIRED:")
        print("   1. Add missing components to hardware/BOM_Seed.csv")
        print("   2. Verify part numbers match datasheet requirements")
        print("   3. Re-run this script to verify fixes")
        print("   4. Update FROZEN_STATE_REV_C4b.md if making changes")
        return 1


if __name__ == "__main__":
    sys.exit(check_completeness())
