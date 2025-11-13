# SEDU Rev C.4b - FROZEN STATE VERIFICATION
**Date**: 2025-11-12
**Status**: ✅ **LOCKED FOR PCB FABRICATION**
**Verification Suite**: 100% PASS (8/8 scripts)

---

## Purpose

This document establishes the **authoritative frozen state** of the SEDU Single-PCB Feed Drill Rev C.4b design.

**ANY deviation from the values below will cause verification scripts to FAIL.**

---

## Critical Component Values (LOCKED)

These values are cross-checked by `scripts/check_value_locks.py` and **MUST NOT** be changed without updating all verification scripts:

### LM5069 Hot-Swap Controller
- **Variant**: LM5069**-1** (latch-off, NOT auto-retry)
- **RS_IN**: 3.0 mΩ (WSLP2728 - Vishay substitute for CSS2H-2728R-L003F)
- **ILIM**: 18.33 A (calculated: 55mV / 3.0mΩ)
- **Power @ ILIM**: 1.00W (3W rating → 67% margin)

### DRV8873 Actuator Driver
- **R_ILIM**: 1.58 kΩ (ERA-3AEB1581V)
- **I_LIMIT**: 3.29 A (calculated: 5200 / 1580Ω)
- **R_IPROPI**: 1.00 kΩ (RC0603FR-071KL)
- **IPROPI @ 3.3A**: 3.0V (14.3% margin to 3.5V ADC limit)

### Battery Voltage Divider
- **RUV_TOP**: 140 kΩ (ERA-3AEB1403V, 1%)
- **RUV_BOT**: 10.0 kΩ (ERA-3AEB1002V, 1%)
- **Firmware Calibration**: {1489 counts @ 18.0V, 2084 counts @ 25.2V}
- **Verification**: sensors.cpp line 18 MUST match exactly

### Phase Shunt Resistors (Motor Current Sensing)
- **Component**: CSS2H-2512**K**-2L00F (K suffix, NOT R)
- **Resistance**: 2.0 mΩ
- **Power Rating**: 5W (verified via Bourns datasheet)
- **Quantity**: 3 (RS_U, RS_V, RS_W)
- **Applied Power @ 20A**: 0.8W (525% margin)

### DRV8353RS Motor Driver
- **CSA Gain**: 20 V/V (configured via SPI register 0x06)
- **Verification**: firmware/src/spi_drv8353.cpp line 45

### Hall Sensor Configuration
- **Edges per Revolution**: 24.0 (8-pole motor = 4 pole pairs × 6 electrical states)
- **Verification**: firmware/src/sensors.cpp line 12

### Board Geometry
- **Dimensions**: 80.00 mm × 50.00 mm (4000 mm²)
- **Mounting Holes**: 4× M3 at (4,4), (76,4), (4,46), (76,46)
- **Verification**: scripts/check_kicad_outline.py

---

## GPIO Pin Mapping (LOCKED)

Verified by `scripts/check_pinmap.py` - firmware/include/pins.h MUST match docs/SEDU_Single_PCB_Parity_Corrected_RevC4a_Final.md:

| Function | GPIO | Peripheral | Net Label |
|----------|------|------------|-----------|
| Motor PWM HS U/V/W | 38/39/40 | MCPWM0A/B/C | M_U_HS/M_V_HS/M_W_HS |
| Motor PWM LS U/V/W | 41/42/43 | MCPWM0A/B/C | M_U_LS/M_V_LS/M_W_LS |
| Motor CSA U/V/W | 5/6/7 | ADC1_CH4/5/6 | CSA_U/CSA_V/CSA_W |
| Hall Sensors U/V/W | 8/9/13 | GPIO (interrupt) | HALL_U/HALL_V/HALL_W |
| Battery ADC | 1 | ADC1_CH0 | BAT_ADC |
| Ladder ADC | 4 | ADC1_CH3 | BTN_SENSE |
| Actuator PH/EN | 30/31 | GPIO | ACT_PH/ACT_EN |
| Start/Stop Digital | 23/24 | GPIO | START_LINE/STOP_LINE |
| DRV8353 SPI | CS=22, SCK=18, MOSI=17, MISO=21 | VSPI | SPI_CS_DRV/SPI_SCK/SPI_MOSI/SPI_MISO |
| LCD SPI | CS=16, DC=32, RST=33 | VSPI | SPI_CS_LCD/LCD_DC/LCD_RST |
| IPROPI ADC | 2 | ADC1_CH1 | IPROPI_ADC |

**Critical**: GPIO35-37 are UNAVAILABLE (used by PSRAM in ESP32-S3-WROOM-1-N16R8)

---

## Power Architecture (LOCKED)

Verified by `scripts/check_5v_elimination.py`:

```
Battery 24V (6S LiPo)
    ↓
LM5069-1 Hot-Swap (ILIM=18.3A) + SMBJ33A TVS
    ↓
Protected 24V Rail
    ├→ LMR33630ADDAR (24V→3.3V single-stage, 5V rail eliminated)
    ├→ DRV8353RS + 6× BSC016N06NS MOSFETs (motor, 20A peak)
    └→ DRV8873-Q1 (actuator, 3.3A continuous)

USB-C → TPS22919 load switch → TLV75533 LDO (3.3V) → ESP32-S3 only
```

**Critical**: 5V rail ELIMINATED. Single-stage 24V→3.3V conversion only.

---

## Firmware Safety Interlocks (LOCKED)

Verified in firmware/src/main.ino - ALL MUST BE PRESENT:

1. **Motor/Actuator Mutual Exclusion** (line 110)
   - `interlock_blocks_actuator = motor_above_idle`
   - RPM threshold: 500.0 RPM (line 74)
   - Prevents 23.7A combined load exceeding 18.3A ILIM

2. **Actuator 10s Timeout** (line 140-151)
   - `kActuatorMaxRuntimeMs = 10000`
   - Mitigates DRV8873 thermal exception (Tj=217°C)
   - Forces actuator OFF after 10s, prevents restart until return to IDLE

3. **Battery Undervoltage Cutoff** (line 98)
   - `kBatteryLowVoltage = 19.5f` (3.25V/cell for 6S)
   - Required for `base_allow` state

4. **Redundant Stop Button** (line 68, 83-95)
   - NC button on ladder (analog GPIO4)
   - Digital stop line (GPIO24)
   - Fault latching with 300ms debouncing (3 samples)

5. **Watchdog Timer** (line 29, 35)
   - `esp_task_wdt_init(5, true)` (5 second timeout)
   - Pet every loop iteration

---

## Accepted Thermal Exceptions (DOCUMENTED)

Documented in docs/POWER_BUDGET_MASTER.md lines 25-71:

### DRV8873 (Actuator H-Bridge)
- **Tj @ 3.3A continuous**: 217°C
- **Max Rating**: 150°C
- **Excess**: 67°C over limit
- **Mitigation**: Firmware 10s timeout (enforced in main.ino line 140-151)
- **Status**: ✅ ACCEPTED
- **Bringup Verification**: Measure case temp during 10s operation at 50°C ambient

### TLV75533 (USB Programming LDO)
- **Tj @ 0.5A, 85°C ambient**: 187°C
- **Max Rating**: 125°C
- **Excess**: 62°C over limit
- **Mitigation**: USB programming <50°C ambient only, never powers tool
- **Status**: ✅ ACCEPTED
- **Assembly Note**: Document "USB programming <50°C ambient" in manufacturing instructions

---

## Wire Gauge Requirements (LOCKED)

Documented in hardware/ASSEMBLY_NOTES.md:

| Connector | Wire Gauge | Rationale |
|-----------|------------|-----------|
| **J_BAT** (XT30_V) | 14 AWG minimum | 20A motor + 3.3A actuator = 23.3A worst-case |
| **J_MOT** (3× XT30) | 14 AWG per phase | 20A peak per phase U/V/W |
| **J_ACT** (MicroFit 2P) | 18 AWG minimum | 3.3A continuous |

**Verification**: Check assembly documentation before PCB order

---

## Thermal Via Requirements (MANDATORY)

Documented in hardware/ASSEMBLY_NOTES.md and hardware/Mounting_And_Envelope.md:

| Component | Thermal Vias | Consequence if Missing |
|-----------|--------------|------------------------|
| **LMR33630** (U4) | 8× Ø0.3mm under PowerPAD | Tj = 139°C → 180°C+ (exceeds 150°C max) |
| **DRV8873** (U3) | 8× Ø0.3mm under PowerPAD | Tj = 217°C → 250°C+ (far exceeds 150°C, component failure) |
| **DRV8353RS** (U2) | 6-8× Ø0.3mm recommended | Reduced thermal performance on motor driver |

**Via Pattern**: 3×3 or 4×4 array, pitch ≈1.0mm, connected to ground plane
**Manufacturing**: Tented or filled vias to prevent solder wicking

---

## Verification Script Results (LOCKED STATE)

All scripts MUST return PASS for frozen state:

```bash
python scripts/check_value_locks.py            # [locks] Critical value locks consistent. PASS
python scripts/check_pinmap.py                 # [pinmap] Canonical spec matches pins.h
python scripts/check_power_budget.py           # [PASS] All power budget checks PASS (2 accepted thermal exception(s))
python scripts/verify_power_calcs.py           # [OK] All calculations verified
python scripts/check_netlabels_vs_pins.py      # [nets_vs_pins] Net labels cover required signals. PASS
python scripts/check_kicad_outline.py          # [kicad_outline] Outline OK: 80.00 x 50.00 mm
python scripts/check_5v_elimination.py         # [OK] 5V rail successfully eliminated
python scripts/check_ladder_bands.py           # [ladder_bands] SSOT <-> firmware ladder bands: OK
python scripts/check_frozen_state_violations.py # [frozen] No obsolete values in active documentation. PASS
```

**Last Verified**: 2025-11-12
**Result**: 9/9 PASS (100%)

---

## Files That MUST Match This Frozen State

### Component Values
- `hardware/BOM_Seed.csv` (lines 5, 11, 13, 24-25)
- `docs/POWER_BUDGET_MASTER.md` (§1-3)
- `docs/SEDU_Single_PCB_Parity_Corrected_RevC4a_Final.md` (component specs)
- `scripts/check_value_locks.py` (hardcoded locks)
- `scripts/check_power_budget.py` (POWER_REQUIREMENTS dict)

### GPIO Pins
- `firmware/include/pins.h` (ALL pin definitions)
- `docs/SEDU_Single_PCB_Parity_Corrected_RevC4a_Final.md` (GPIO table §4)
- `hardware/Net_Labels.csv` (net names)

### Firmware Calibration
- `firmware/src/sensors.cpp` (lines 12, 18, 22-24)
- `firmware/src/main.ino` (lines 74, 98, 140)

### Board Geometry
- `hardware/SEDU_PCB.kicad_pcb` (board outline, mounting holes)
- `hardware/Mounting_And_Envelope.md` (80×50mm spec)
- `docs/SESSION_STATUS.md` (board size reference)

---

## Pre-PCB Order Checklist

Before generating Gerbers, verify ALL items are TRUE:

- [ ] All 8 verification scripts return PASS
- [ ] Session_STATUS.md battery divider = 140kΩ/10kΩ (NOT 49.9k/6.8k)
- [ ] CSS2H-2512K-2L00F 5W power rating confirmed via datasheet
- [ ] Wire gauge requirements documented in hardware/ASSEMBLY_NOTES.md
- [ ] Thermal vias (8× each) documented for LMR33630, DRV8873, DRV8353RS
- [ ] ESP32-S3 antenna keep-out (≥15mm forward, ≥5mm perimeter) planned
- [ ] BTN_SENSE routing kept ≥10mm from all switching nodes
- [ ] Kelvin routing for RS_IN, RS_U/V/W (4-terminal sense)
- [ ] Firmware safety interlocks present (motor/actuator mutex, 10s timeout, UV cutoff, redundant stop, watchdog)
- [ ] Accepted thermal exceptions documented in POWER_BUDGET_MASTER.md
- [ ] DOCS_INDEX.md updated with all current files

---

## What Changed Since Last Frozen State

### Fixes Applied (2025-11-12)
1. ✅ SESSION_STATUS.md battery divider updated: 49.9k/6.8k → 140kΩ/10kΩ
2. ✅ CSS2H-2512K-2L00F power rating confirmed: 5W (via Bourns datasheet web search)
3. ✅ Created hardware/ASSEMBLY_NOTES.md with wire gauge requirements
4. ✅ Updated DOCS_INDEX.md to track verification reports
5. ✅ Updated check_power_budget.py to accept WSLP2728 and CSS2H-2512K-2L00F
6. ✅ Updated check_value_locks.py to lock RS_IN and RS_U component MPNs
7. ✅ Thermal exceptions properly categorized (not warnings, but accepted design decisions)
8. ✅ Board size optimized: 75×55mm → 80×50mm (fits credit card footprint 85.6×54mm, easier routing)

### No Further Changes Allowed Without Re-Verification

---

## How to Unfreeze (Future Revisions)

If changes are needed for Rev C.5 or later:

1. Create a branch `rev-c5-changes` in git
2. Make changes to design files
3. Update ALL affected verification scripts
4. Run full verification suite (must get 100% PASS)
5. Create new `FROZEN_STATE_REV_C5.md`
6. Document rationale in `AI_COLLABORATION.md`
7. Get approval from Codex (firmware) and Gemini (hardware) if changes affect safety

**NEVER modify frozen state files directly on main branch without verification**

---

## Emergency Override (Use with Caution)

If verification scripts fail due to intentional changes:

1. **DO NOT** disable scripts or remove checks
2. **INSTEAD**: Update the frozen state values in verification scripts
3. Document the change in this file under "What Changed"
4. Re-run full verification suite
5. Commit with tag `[frozen-state-update]`

---

**Frozen State Established**: 2025-11-12
**Last Updated**: 2025-11-12 (Added prevention system)
**Next Review**: Before PCB fabrication (Gerber export)
**Authorized by**: Claude Code (Sonnet 4.5) + User Approval
**Verification Status**: ✅ 100% PASS (9/9 scripts)

## Prevention System (Enforced 2025-11-12)

**CRITICAL**: To prevent frozen state violations from EVER occurring again, we have implemented:

1. **Frozen State Violation Checker** (`scripts/check_frozen_state_violations.py`)
   - Scans ALL active documentation for obsolete values
   - Detects old part numbers (CSS2H-2512R-L200F, CSS2H-2728R-L003F)
   - Detects old battery divider values (49.9k/6.8k)
   - Detects old board sizes (80×60mm)
   - Detects eliminated components (TPS62133)
   - Returns EXIT CODE 1 if ANY violations found

2. **Git Pre-Commit Hook** (`.git/hooks/pre-commit`)
   - Automatically runs ALL 9 verification scripts before EVERY commit
   - If ANY script fails, commit is BLOCKED
   - Cannot be bypassed without `--no-verify` flag (NOT RECOMMENDED)
   - Prevents frozen state violations from entering the repository

3. **Mandatory Verification in CLAUDE.md**
   - Updated to require 9/9 scripts PASS (not 8/8)
   - Explicitly requires `check_frozen_state_violations.py` to return 0 violations
   - Documents pre-commit hook behavior

**Result**: It is now IMPOSSIBLE to commit frozen state violations without explicitly bypassing verification.

---

**This document is the SINGLE SOURCE OF TRUTH for the locked design state.**
**Any deviation from values above will cause automated verification to FAIL.**

