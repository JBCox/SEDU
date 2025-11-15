# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## ⚠️ FROZEN STATE - READ FIRST

**CRITICAL**: This design is in FROZEN STATE for Rev C.4b PCB fabrication.

**Before making ANY changes**, read: `FROZEN_STATE_REV_C4b.md`

**All changes MUST**:
1. Pass 100% of verification scripts (9/9 PASS required)
2. Run `python scripts/check_frozen_state_violations.py` (MUST return 0 violations)
3. Be documented in FROZEN_STATE_REV_C4b.md
4. Update affected verification script locks
5. Get multi-AI approval if safety-critical

**Pre-Commit Hook ACTIVE**: Git pre-commit hook automatically runs ALL 9 verification scripts.
If ANY script fails, commit is BLOCKED. This prevents frozen state violations from ever being committed.

**Locked Values** (DO NOT CHANGE without updating frozen state):
- Battery divider: 140kΩ / 10kΩ
- LM5069 RS_IN: 3.0mΩ (WSLP2728)
- Phase shunts: 2.0mΩ, 5W (CSS2H-2512K-2L00F)
- DRV8873: R_ILIM=1.58kΩ, R_IPROPI=1.00kΩ
- Board: 80mm × 50mm
- All GPIO assignments in pins.h

**Verification Command** (must return 100% PASS):
```bash
python scripts/run_all_verification.py
```

This runs all 9 database-driven verification scripts. All must PASS before making changes.

---

## Project Overview

**SEDU Single-PCB Feed Drill** - 24V battery-powered handheld aviation tool with BLDC motor and linear actuator. Replaces legacy VESC-based multi-board stack with integrated ESP32-S3 controller combining motor driver (DRV8353RS), actuator driver (DRV8873-Q1), hot-swap protection (LM5069-1), and safety interlocks.

**Critical Safety Context**: This is aviation tooling with mandatory redundant safety features. All changes affecting motor control, actuator control, battery monitoring, or button interlocks require verification against `docs/SEDU_Single_PCB_Parity_Corrected_RevC4a_Final.md` (SSOT).

---

## Essential Commands

### ⚠️ MANDATORY VERIFICATION WORKFLOW

**Rule**: After fixing ANY bug, updating ANY component value, or changing ANY design parameter, you MUST run ALL verification scripts to ensure documentation consistency.

**Why**: Past issues (battery divider mismatch, power rating errors) were caused by updating one file but missing others. This prevents documentation drift.

### **Quick Verification (Recommended)** ⚡

Run the complete verification suite with a single command:

```bash
python scripts/run_all_verification.py
```

**What it does:**
- Runs all 9 database-driven verification scripts in sequence
- Shows real-time output from each script
- Provides summary with PASS/FAIL count
- Returns exit code 0 if all pass, 1 if any fail

**Expected output (all passing):**
```
[PASS] VERIFICATION SUITE PASSED
   All verification scripts passed successfully
   System integrity verified
Total: 9/9 passed
```

### **Individual Verification Scripts** (for debugging specific areas)

If you need to debug a specific verification failure, run scripts individually:

```bash
# 1. Database schema validation
python scripts/check_database_schema.py

# 2. Critical value locks (component values, battery divider, board size)
python scripts/check_value_locks.py

# 3. Pin mapping (firmware ↔ documentation GPIO assignments)
python scripts/check_pinmap.py

# 4. Net label consistency (schematic ↔ firmware)
python scripts/check_netlabels_vs_pins.py

# 5. Board geometry (80×50mm, 4× M3 holes)
python scripts/check_kicad_outline.py

# 6. 5V rail elimination verification
python scripts/check_5v_elimination.py

# 7. Button ladder verification
python scripts/check_ladder_bands.py

# 8. Power calculations verification
python scripts/verify_power_calcs.py

# 9. BOM completeness verification (CRITICAL - ensures all datasheet-required components present)
python scripts/check_bom_completeness.py

# Optional (not in main suite):
python scripts/check_power_budget.py          # Exit code 1 expected for known thermal issues
python scripts/check_frozen_state_violations.py  # Prevents obsolete values
python scripts/check_policy_strings.py        # Legacy banned strings
python scripts/check_docs_index.py            # Documentation tracking
```

**When to Run**:
- ✅ Changed any resistor value (R_ILIM, battery divider, sense resistor)
- ✅ Swapped IC or component package
- ✅ Modified firmware GPIO assignment
- ✅ Updated power calculations or current limits
- ✅ Fixed calibration constants
- ✅ Changed connector, wire gauge, or BOM entry

**Interpreting Results**:
- `check_value_locks.py` fails → Fix inconsistency immediately (BOM vs SSOT vs firmware)
- `check_power_budget.py` exit code 1 → EXPECTED (DRV8873 thermal, J_MOT rating are known issues); verify no NEW issues introduced
- Other failures → Follow script output to resolve

**Document in AI_COLLABORATION.md**: After verification PASSES, log fix as new PROPOSAL entry with verification results.

### Firmware Development

```bash
# Arduino CLI compilation (ESP32-S3)
arduino-cli compile --fqbn esp32:esp32:esp32s3 firmware/

# Upload to ESP32-S3 (battery disconnected, USB-C only)
arduino-cli upload -p COM3 --fqbn esp32:esp32:esp32s3 firmware/

# Serial monitor (115200 baud)
arduino-cli monitor -p COM3 -c baudrate=115200
```

**Critical**: USB is programming-only. Tool never operates from USB power (TPS22919 load switch + TLV75533 LDO isolate programming rail from main 5V/3.3V).

---

## Architecture Overview

### Power Architecture
```
Battery 24V (6S LiPo)
    ↓
LM5069-1 Hot-Swap (ILIM=18.3A, UV/OV, latch-off) + SMBJ33A TVS
    ↓
Protected 24V Rail
    ├─→ LMR33630ADDAR (24V→3.3V logic, single-stage; 5V rail eliminated)
    ├─→ DRV8353RS + 6× MOSFETs (motor, 20A peak)
    └─→ DRV8873-Q1 (actuator, 3.3A continuous)
```

**USB Programming Path** (isolated, never powers tool):
```
USB-C → TPS22919 load switch → TLV75533 LDO (3.3V) → ESP32-S3 only
```

### Motor Control Stack
- **DRV8353RS**: 3-phase gate driver with integrated CSAs (20V/V gain)
- **MOSFETs**: 6× 60V SuperSO8 (BSC016N06NS), 2mΩ typical
- **Shunts**: 3× 2mΩ 2512 Kelvin sense (CSS2H-2512K-2L00F, 5W verified)
- **Hall Sensors**: GPIO8/9/13 (3 halls → 6-step commutation, expandable to FOC)
- **PWM**: MCPWM peripheral on GPIO38-43 (HS U/V/W, LS U/V/W)

### Actuator Control
- **DRV8873-Q1**: H-bridge, PH/EN mode (GPIO30/31)
- **Current Limit**: R_ILIM=1.58kΩ → 3.3A nominal (IPROPI feedback on GPIO2)
- **Interlock**: Actuator blocked if motor RPM > 500 (prevents simultaneous 23A draw exceeding LM5069 ILIM)

### Safety Interlocks (Mandatory)
1. **Redundant Stop**: NC button on ladder AND discrete GPIO24
2. **Battery UV Cutoff**: 19.5V (3.25V/cell for 6S)
3. **Motor/Actuator Interlock**: Mutual exclusion enforced in firmware
4. **Actuator Timeout**: 10s max continuous runtime
5. **Watchdog**: 5s ESP32-S3 task watchdog
6. **Fault Latching**: Requires return to IDLE state to clear (with 300ms debounce)

### Firmware Architecture
```
firmware/
  ├─ include/pins.h         # GPIO constants (MUST match SSOT table)
  └─ src/
      ├─ main.ino           # Control loop (100ms poll), safety interlocks
      ├─ sensors.{cpp,h}    # Battery/ladder/IPROPI ADC, motor CSA
      ├─ rpm.{cpp,h}        # Hall edge counting (24 edges/rev for 8-pole motor)
      ├─ actuator.{cpp,h}   # DRV8873 PH/EN control
      ├─ input_ladder.{cpp,h} # Button voltage classification
      ├─ lcd_gc9a01.{cpp,h} # GC9A01 240×240 SPI display (write-only)
      └─ spi_drv8353.{cpp,h} # DRV8353RS SPI config (gain=20V/V)
```

**Key Firmware Constants** (sensors.cpp):
- Battery divider: 140kΩ/10kΩ → calibrated {1489, 18.0V} to {2084, 25.2V}
- Hall edges: 24.0f (8-pole motor = 4 pole pairs × 6 electrical states)
- DRV8353 CSA gain: 20V/V (configured via SPI register 0x06)
- Phase shunt: 2mΩ (kRsensePhaseOhms)

---

## Critical GPIO Map (ESP32-S3-WROOM-1-N16R8)

**Locked assignments** - changes require updating BOTH `firmware/include/pins.h` AND `docs/SEDU_Single_PCB_Parity_Corrected_RevC4a_Final.md`:

| Function | GPIO | Notes |
|----------|------|-------|
| **Motor PWM** | 38-43 | MCPWM HS/LS U/V/W (GPIO35-37 unavailable due to PSRAM) |
| **Motor CSAs** | 5/6/7 | ADC1_CH4/5/6 (56Ω+470pF anti-alias) |
| **Hall Sensors** | 8/9/13 | Interrupts on CHANGE, 24 edges/rev |
| **Battery ADC** | 1 | ADC1_CH0, 140kΩ/10kΩ divider |
| **Ladder ADC** | 4 | ADC1_CH3, button classification |
| **Actuator PH/EN** | 30/31 | DRV8873 control |
| **Start/Stop Digital** | 23/24 | Redundant with ladder |
| **DRV8353 SPI** | CS=22, SCK=18, MOSI=17, MISO=21 | MODE1, 1MHz |
| **LCD SPI** | CS=16, DC=32, RST=33 | Shares SCK/MOSI, MODE0, 20MHz, MISO NC |
| **USB D+/D-** | 19/20 | Native USB OTG, 22Ω series |

**ADC Configuration**: All ADC1 channels (no WiFi conflict), 12dB attenuation, 3.3V reference.

---

## Single Source of Truth (SSOT)

**Authoritative document**: `docs/SEDU_Single_PCB_Parity_Corrected_RevC4a_Final.md`

All other files must align with SSOT. Changes to pins, voltages, component values, or safety thresholds require:
1. Update SSOT document
2. Update `firmware/include/pins.h` (if GPIO changed)
3. Run **all verification scripts** (must PASS)
4. Document in `AI_COLLABORATION.md` if coordination with other AIs needed

**Deviation tracking**: `docs/DEVIATIONS_FROM_LEGACY.md` lists all changes from original VESC-based design.

---

## Multi-AI Collaboration

This project uses coordinated development between Claude Code, Codex CLI, and Gemini CLI.

**Approval workflow** (from `AI_COLLABORATION.md`):
```
[Propose Change]
    ↓
[All AIs Review] → Gemini flags hardware concerns, Codex reviews firmware
    ↓
[Claude + Codex Approve] (Gemini advisory only)
    ↓
[Implement] → Either Claude or Codex makes changes
    ↓
[Verify] → Run all scripts, confirm PASS
    ↓
[Document] → Update AI_COLLABORATION.md
```

**When making changes**:
- Document proposals in `AI_COLLABORATION.md` as `[PROPOSAL-NNN]`
- Tag status: 🔴 Needs Review, ✅ Approved, 🚀 Implemented
- Run verification scripts and paste results
- Wait for Codex acknowledgment before proceeding with critical firmware/hardware changes

---

## Common Tasks

### Adding a New GPIO Pin

1. Update `docs/SEDU_Single_PCB_Parity_Corrected_RevC4a_Final.md` GPIO table
2. Update `firmware/include/pins.h` with constant definition
3. Update `hardware/Net_Labels.csv` with net name
4. Run `python scripts/check_pinmap.py` (must PASS)
5. Run `python scripts/check_netlabels_vs_pins.py` (must PASS)
6. Document in `AI_COLLABORATION.md` if coordination needed

### Modifying Firmware Safety Logic

1. Read existing safety interlocks in `firmware/src/main.ino` (lines 77-98)
2. Verify change doesn't bypass motor/actuator interlock
3. Add debouncing if introducing new digital inputs (300ms / 3 samples)
4. Test watchdog timing (5s timeout)
5. Document rationale in commit message with `[safety]` tag

### Updating Component Values

**Locked values** (checked by `scripts/check_value_locks.py`):
- LM5069 RS_IN: 3.0mΩ (ILIM = 55mV / 3.0mΩ = 18.3A)
- DRV8873 R_ILIM: 1.58kΩ (3.3A limit)
- DRV8873 R_IPROPI: 1.00kΩ
- Board outline: 80×50mm
- M3 holes: 4× at specified positions

Changes to these require:
1. Update `hardware/BOM_Seed.csv`
2. Update lock in verification script
3. Recalculate dependent values (ILIM, power dissipation)
4. Document in technical note under `docs/`

### Hardware Bring-Up Checklist

Follow `docs/BRINGUP_CHECKLIST.md`:
1. Visual inspection (no shorts, all components placed)
2. Battery disconnected: USB programming test
3. Battery connected: verify 3.3V rail
4. DRV8353 SPI communication (read ID register)
5. Battery ADC calibration (verify 18V-25.2V range)
6. Hall sensor verification (spin motor, check edge count)
7. Actuator test pulse (150ms, verify IPROPI reading)
8. Motor current sense (verify CSA 20V/V gain)
9. Safety interlock verification (motor blocks actuator)

---

## File Organization

```
C:\SEDU\
├─ docs/                      # Specifications, guides, reports
│   ├─ SEDU_Single_PCB_*.md   # SSOT specification
│   ├─ DEVIATIONS_FROM_LEGACY.md
│   ├─ BRINGUP_CHECKLIST.md
│   ├─ SESSION_STATUS.md      # Current development state
│   └─ archive/               # Historical documents
├─ firmware/
│   ├─ include/pins.h         # GPIO constants
│   └─ src/*.{cpp,h,ino}      # Modular firmware
├─ hardware/
│   ├─ BOM_Seed.csv           # Bill of materials
│   ├─ Net_Labels.csv         # Net names
│   ├─ SEDU_PCB_Sheet_Index.md
│   └─ *.kicad_*              # KiCad project files (to be created)
├─ scripts/
│   └─ check_*.py             # Verification scripts
├─ reports/                   # Agent verification reports
├─ AI_COLLABORATION.md        # Multi-AI coordination log
├─ README_FOR_CODEX.md        # Codex CLI guide
├─ INIT.md                    # Session initialization
└─ AGENTS.md                  # Contributor guidelines
```

**Documentation index**: `docs/DOCS_INDEX.md` tracks all files (update when adding/removing).

---

## Anti-Drift Rules (Critical)

**Never reintroduce**:
- VESC fallback modes or PPM/PWM headers
- USB powering the tool during operation
- TLV757xx parts (wrong LDO for USB rail)
- GPIO35-37 usage (unavailable with PSRAM module)

**Always verify**:
```bash
# Banned string check
rg -n "TLV757|VESC fallback|PPM|PWM header" -S

# USB policy present
rg -n "TLV75533|TPS22919" -S docs/ hardware/

# LCD configuration
rg -n "GC9A01|MISO NC|CS_LCD|GPIO16" -S docs/
```

**Pin change protocol**:
- Update pins.h AND SSOT in same commit
- Run `check_pinmap.py` before committing
- Tag commit: `[pins sync]` or `[gpio]`

---

## Known Issues & Warnings (From Recent Verification)

**Fixed in PROPOSAL-031** (2025-11-11):
- ✅ DRV8353 gain now configured via SPI (20V/V)
- ✅ Hall pole count corrected (24 edges/rev for 8-pole motor)
- ✅ Battery ADC underflow clamping added
- ✅ Ladder fault debouncing implemented (300ms)
- ✅ Test pulse race condition resolved

**BOM Warnings** (hardware/BOM_Seed.csv):
- J_MOT: MicroFit 3P rated 8A, peak 20A → use 3×2P or higher-rated connector
- J_BAT: Requires 14 AWG wire minimum for 23A peak
- RS_U/V/W: ✅ CSS2H-2512K-2L00F verified 5W rated (525% margin @ 20A peaks, confirmed 2025-11-12)

**Missing Features** (not critical for first prototype):
- NTC temperature monitoring (GPIO10 defined but not read)
- Motor PWM/FOC implementation (hardware ready, firmware stub only)
- LED/Buzzer user feedback (GPIOs defined but unused)
- Configuration storage (NVS/EEPROM for calibration persistence)

---

## Build System & Toolchain

**Current State**: Documentation-driven, no CI/CD yet.

**Expected Tools**:
- Arduino IDE 2.x or arduino-cli
- ESP32 board support: `esp32:esp32:esp32s3`
- KiCad 8.0+ (record version in `docs/TOOL_VERSIONS.md`)
- Python 3.9+ for verification scripts

**Pre-commit hooks** (optional):
```bash
pip install pre-commit
pre-commit install
```

Runs verification scripts automatically on commit (`.pre-commit-config.yaml` if configured).

---

## Resuming Work

1. **Run verification suite** to confirm system integrity:
   ```bash
   python scripts/run_all_verification.py
   ```
   All 9 scripts must PASS before starting work.

2. **Read context documents**:
   - `QUICKSTART.md` - Quick reference guide
   - `VERIFICATION_SYSTEM_COMPLETE.md` - Database system overview
   - `docs/SESSION_STATUS.md` - Current development state
   - `AI_COLLABORATION.md` - Pending proposals/discussions
   - `docs/archive/CHANGELOG.md` - Latest decisions

3. **Confirm database-driven workflow**:
   - Only edit `design_database.yaml` (single source of truth)
   - Run `python scripts/generate_all.py` after database changes
   - Never manually edit generated files (BOM, pins.h, etc.)

---

## Power Design Workflow (Critical)

**Problem**: Multiple power issues discovered late (battery divider, connector ratings, thermal limits).

**Solution**: Mandatory power-first design workflow:

1. **Before Schematic**: Create power budget in `docs/POWER_BUDGET_MASTER.md`
2. **Component Selection**: Document voltage/current/power margins for every component
3. **Schematic Review**: Run `python scripts/check_power_budget.py` (must PASS)
4. **PCB Layout**: Implement thermal design rules (vias, trace width, Kelvin routing)
5. **Pre-Order**: Peer review, datasheet verification, firmware safety check

**Key Documents**:
- `docs/POWER_BUDGET_MASTER.md` - All power calculations (single source of truth)
- `docs/DESIGN_REVIEW_WORKFLOW.md` - Step-by-step process to prevent power issues
- `scripts/check_power_budget.py` - Automated verification of component ratings

**Derating Policy**:
- Voltage: 80% of absolute max (20% margin)
- Current: 80% of continuous rating
- Power: 50% of rated power
- Thermal: Tj < 85% of max

**Run this BEFORE any component change or PCB order**: `python scripts/check_power_budget.py`

---

## References

- **SSOT**: `docs/SEDU_Single_PCB_Parity_Corrected_RevC4a_Final.md`
- **Power Budget**: `docs/POWER_BUDGET_MASTER.md` (NEW - single source for power calcs)
- **Design Workflow**: `docs/DESIGN_REVIEW_WORKFLOW.md` (NEW - prevent power issues)
- **Codex Guide**: `README_FOR_CODEX.md`
- **Session Init**: `INIT.md`
- **Multi-AI Log**: `AI_COLLABORATION.md`
- **Datasheet Notes**: `Datasheet_Notes.md`
- **Bring-Up**: `docs/BRINGUP_CHECKLIST.md`

---

**Last Updated**: 2025-11-11 (Added power-first design workflow to prevent recurring issues)
