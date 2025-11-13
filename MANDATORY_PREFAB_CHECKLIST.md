# MANDATORY PRE-FABRICATION VERIFICATION CHECKLIST

**DO NOT SKIP ANY ITEM. EVERY SINGLE CHECK MUST PASS BEFORE CLAIMING "READY".**

## 1. VERIFICATION SCRIPTS (Must ALL Pass)

```bash
□ python scripts/check_value_locks.py
□ python scripts/check_pinmap.py
□ python scripts/check_netlabels_vs_pins.py
□ python scripts/check_kicad_outline.py
□ python scripts/verify_power_calcs.py
□ python scripts/check_ladder_bands.py
□ python scripts/check_frozen_state_violations.py
□ python scripts/check_power_budget.py
□ python scripts/check_docs_index.py
```

## 2. BOM COMPLETENESS CHECK

For EVERY IC in the schematic, verify ALL required passives are in BOM:

□ **LM5069**: RS_IN (3mΩ), CDVDT (33nF), Q_HS (2×), TVS1
□ **LMR33630**: L4, C4IN_A, C4IN_B, C4x (4×), **C_BOOT**, **C_VCC**
□ **DRV8353RS**: C_CPLCPH, C_VCP, C_VGLS, C_DVDD
□ **DRV8873**: R_ILIM, R_IPROPI, TVS2
□ **ESP32-S3**: USB ESD, R_CC1/CC2
□ **TPS22919**: Input/output caps (if specified)
□ **TLV75533**: Input/output caps (if specified)
□ **Motor bridge**: 6× MOSFETs, 6× gate resistors, 3× phase shunts
□ **All ADC inputs**: Series resistor + shunt cap

## 3. OBSOLETE VALUE GREP (Must Return ZERO Hits)

Run these greps across ALL non-archived files:

```bash
□ rg "75×55|75 × 55" --type md -g "!docs/archive/*"
□ rg "4125mm²|4125 mm²" --type md -g "!docs/archive/*"
□ rg "14% (area )?reduction" --type md -g "!docs/archive/*"
□ rg "\(71,4\)|\(4,51\)|\(71,51\)" --type md -g "!docs/archive/*"
□ rg "67mm.*47mm|47mm.*67mm" --type md -g "!docs/archive/*"
□ rg "49\.9\s*k" --type md -g "!docs/archive/*" (old battery divider)
□ rg "6\.8\s*k" --type md -g "!docs/archive/*" (old battery divider)
□ rg "CSS2H-2512R-L200F" --type md -g "!docs/archive/*" (R suffix, old)
□ rg "CSS2H-2728R-L003F" . -g "!docs/archive/*" (old RS_IN)
□ rg "TPS62133" --type md -g "!docs/archive/*" (5V rail eliminated)
```

## 4. COMPONENT VALUE CROSS-CHECK

Verify these values are IDENTICAL across BOM, SSOT, FROZEN_STATE, and firmware:

□ **Battery divider**: 140kΩ / 10kΩ (RUV_TOP / RUV_BOT)
□ **RS_IN**: WSLP2728 (3.0mΩ, ≥3W)
□ **RS_U/V/W**: CSS2H-2512K-2L00F (2.0mΩ, 5W) - K suffix NOT R
□ **R_ILIM**: 1.58kΩ (ERA-3AEB1581V)
□ **R_IPROPI**: 1.00kΩ
□ **DRV8353 decoupling**: 47nF (CPL-CPH), 1µF (VCP/VGLS/DVDD)
□ **Board dimensions**: 80mm × 50mm
□ **Mounting holes**: (4,4), (76,4), (4,46), (76,46)
□ **LMR33630 caps**: C_BOOT (100nF), C_VCC (1µF) - CRITICAL

## 5. DATASHEET VERIFICATION

For EVERY power component, verify:

□ **LM5069**: RS_IN value matches ILIM calculation (18.3A)
□ **LMR33630**: Bootstrap cap value matches datasheet (100nF)
□ **DRV8873**: R_ILIM matches current limit formula (3.29A)
□ **DRV8353**: CSA gain configured correctly (20 V/V)
□ **Phase shunts**: Power rating ≥5W verified from datasheet
□ **All capacitors**: Voltage ratings have ≥20% margin

## 6. THERMAL VERIFICATION

□ **LM5069**: Tj < 150°C at 18.3A
□ **LMR33630**: Tj < 150°C at 3A (requires 8× thermal vias)
□ **DRV8873**: Tj < 150°C with 10s timeout (requires 8× thermal vias)
□ **TLV75533**: Tj < 125°C (programming <50°C ambient restriction)
□ **DRV8353RS**: Tj < 150°C (requires thermal vias)
□ **MOSFETs**: Tj < 175°C at 20A peak
□ **Phase shunts**: Power dissipation < 1.25W at 25A fault

## 7. FIRMWARE VERIFICATION

□ **Battery calibration**: {1489, 18.0V} to {2084, 25.2V} matches divider
□ **Ladder bands**: Firmware thresholds match SSOT voltage bands
□ **Actuator timeout**: 10s maximum enforced (DRV8873 thermal safety)
□ **Motor/actuator interlock**: Prevents simultaneous 23.7A (exceeds 18.3A ILIM)
□ **GPIO map**: pins.h matches SSOT table exactly

## 8. PHYSICAL FIT VERIFICATION

□ **Component density**: <85% (including routing overhead)
□ **Antenna keep-out**: ≥15mm forward, ≥5mm perimeter clear
□ **Mounting holes**: No interference with component placement
□ **High-power traces**: ≥4mm battery, ≥3mm motor, ≥1.5mm actuator
□ **Connector edge clearance**: All connectors accessible

## 9. DOCUMENTATION CONSISTENCY

□ **FROZEN_STATE_REV_C4b.md**: All frozen values current
□ **SSOT**: All specifications match BOM and firmware
□ **INIT.md**: Quick reference values correct
□ **CLAUDE.md**: All critical values in summary tables correct
□ **README_FOR_CODEX.md**: Component locks match SSOT
□ **SESSION_STATUS.md**: Current status accurate

## 10. FINAL GREP AUDIT

Run comprehensive search for ANY remaining issues:

```bash
□ rg "TODO|FIXME|XXX" --type md -g "!docs/archive/*"
□ rg "TBD|pending|placeholder" -i --type md -g "!docs/archive/*"
□ rg "VERIFY|CHECK THIS" -i --type md -g "!docs/archive/*"
□ rg "\?\?\?" . -g "!docs/archive/*"
```

---

## SIGN-OFF

**Only after ALL boxes above are checked, run:**

```bash
python scripts/check_frozen_state_violations.py && \
python scripts/check_power_budget.py && \
python scripts/check_value_locks.py && \
echo "===== ALL CHECKS PASS - READY FOR FABRICATION ====="
```

**If ANY check fails, DO NOT claim "ready". Fix the issue and restart checklist.**

---

**Created**: 2025-11-12
**Purpose**: Prevent premature "ready" declarations by enforcing systematic verification
