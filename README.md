# SEDU Single-PCB Feed Drill

**Aviation-grade 24V battery-powered handheld tool**
**Rev C.4b - Frozen Design State**

---

## Quick Start

**New Session?** Run `python scripts/run_all_verification.py` then read `QUICKSTART.md`
**For AI Agents**: Read `CLAUDE.md` or `README_FOR_CODEX.md` first
**For Humans**: Read `INIT.md` to understand project status
**For Fabrication**: Check `MANDATORY_PREFAB_CHECKLIST.md` before ordering PCBs

---

## Project Overview

Single-PCB integrated controller replacing legacy VESC-based multi-board stack:
- **MCU**: ESP32-S3-WROOM-1-N16R8 (dual-core, 16MB flash, 8MB PSRAM)
- **Motor Driver**: DRV8353RS 3-phase gate driver + 6× MOSFETs (20A peak)
- **Actuator Driver**: DRV8873-Q1 H-bridge (3.3A continuous)
- **Protection**: LM5069-1 hot-swap controller (18.3A ILIM, UV/OV, latch-off)
- **Power**: LMR33630 buck (24V→3.3V single-stage, 5V rail eliminated)
- **Safety**: Redundant stop, motor/actuator interlock, watchdog, fault latching

**Board**: 80mm × 50mm, 4× M3 mounting holes, credit-card compatible
**Input**: 24V nominal (6S LiPo, 18V-25.2V range)
**Display**: GC9A01 240×240 SPI LCD with backlight
**I/O**: Resistor ladder button input + discrete Start/Stop

---

## Database-Driven Workflow

**Problem Solved**: Eliminates 78-error verification loop and documentation drift

**How it works**:
1. **Edit ONE file**: `design_database.yaml` (117 components, 35 GPIOs, 7 ICs, all design values)
2. **Run generators**: `python scripts/generate_all.py` (creates BOM, pins.h, netlabels, reports)
3. **Verify**: `python scripts/run_all_verification.py` (9 database-driven scripts, all must PASS)
4. **Commit**: All files guaranteed consistent

**Benefits**:
- Zero documentation drift (impossible by design)
- Proven bug detection (found 2 critical bugs during migration)
- Auto-updating verification (reads database directly)

**See**: `VERIFICATION_SYSTEM_COMPLETE.md` for full migration report
**See**: `docs/NEW_WORKFLOW_GUIDE.md` for complete usage guide

---

## Project Structure

```
SEDU/
├── design_database.yaml             ← SINGLE SOURCE OF TRUTH (edit this)
├── CLAUDE.md                         ← AI agent guide
├── INIT.md                           ← Session initialization
├── QUICKSTART.md                     ← Quick reference guide (NEW)
├── FROZEN_STATE_REV_C4b.md          ← Frozen design state
├── VERIFICATION_SYSTEM_COMPLETE.md  ← Verification migration report (NEW)
├── MANDATORY_PREFAB_CHECKLIST.md    ← Pre-fabrication checklist
├── Component_Report.md               ← Generated component report
│
├── docs/                             ← Specifications & guides
│   ├── NEW_WORKFLOW_GUIDE.md         ← How to use database system
│   ├── POWER_BUDGET_MASTER.md        ← Power calculations
│   ├── BRINGUP_CHECKLIST.md          ← Bring-up procedures
│   └── DOCS_INDEX.md                 ← Complete file index
│
├── hardware/                         ← KiCad project
│   ├── SEDU_PCB.kicad_pcb            ← PCB layout (80×50mm)
│   ├── SEDU_PCB.kicad_sch            ← Top-level schematic
│   ├── BOM_Seed.csv                  ← Generated BOM (117 components)
│   └── [hierarchical sheets]
│
├── firmware/                         ← ESP32-S3 code
│   ├── include/pins.h                ← Generated GPIO definitions (35 pins)
│   └── src/                          ← Modular firmware
│
├── scripts/                          ← Generators & verification
│   ├── generate_all.py               ← Master generator
│   ├── run_all_verification.py       ← Verification suite runner (NEW)
│   ├── check_database_schema.py      ← Database validator
│   ├── check_value_locks.py          ← Locked values checker
│   ├── check_pinmap.py               ← GPIO validator
│   └── [6 more verification scripts]
│
└── reports/                          ← Verification reports (dated)
    ├── 2025-11-14/                   ← Latest (database system)
    ├── 2025-11-13/                ← BOM completeness fix
    └── 2025-11-12/                ← Board optimization
```

**See**: `docs/DOCS_INDEX.md` for complete file listing and descriptions

---

## Design Status

**Revision**: C.4b
**State**: **FROZEN** for PCB fabrication
**Schematics**: Title blocks only (need schematic entry)
**PCB Layout**: Outline + mounting holes placed (80×50mm)
**BOM**: 117 components (all in database)
**Verification**: 9 database-driven scripts + 2 optional (11 total)

**Latest Verification** (2025-11-15):
- ✅ Database schema valid (7 ICs, 117 components, 35 GPIOs)
- ✅ 17 locked values correct
- ✅ 35 GPIO pins validated (firmware ↔ database)
- ✅ 44 net labels complete
- ✅ Board geometry correct (80×50mm)
- ✅ 5V rail eliminated
- ✅ Button ladder verified (database ↔ firmware)
- ✅ 8 power calculations verified
- ✅ 61 critical BOM components present
- ✅ All 9 verification scripts passing (100%)

---

## Key Features

**Safety-Critical**:
- Redundant NC stop button (ladder + discrete GPIO)
- Motor/actuator mutual exclusion (prevent 23A simultaneous draw)
- Battery UV cutoff (19.5V = 3.25V/cell)
- Actuator 10s timeout
- 5s watchdog
- Fault latching with 300ms debounce

**Motor Control**:
- DRV8353RS 3-phase driver (CSA gain 20V/V via SPI)
- 6× BSC016N06NS MOSFETs (60V, 2mΩ)
- 3× CSS2H-2512K-2L00F shunts (2mΩ, 5W verified)
- Hall sensors on GPIO8/9/13 (24 edges/rev for 8-pole motor)
- MCPWM outputs GPIO38-43 (6-step commutation, FOC-ready)

**Power Architecture**:
- LM5069-1: 18.3A ILIM (3.0mΩ Kelvin sense), UV/OV window, dV/dt control
- LMR33630: Single-stage 24V→3.3V @ 3A (5V rail eliminated)
- USB isolation: TPS22919 load switch → TLV75533 LDO (programming only)
- Battery monitor: 140kΩ/10kΩ divider (18V-25.2V → 1.20V-1.68V @ ADC)

**I/O**:
- Resistor ladder: 6-button input (Idle/Start/Stop/F1/F2/F3/Fault)
- Discrete inputs: Start (GPIO23), NC Stop (GPIO24)
- LCD: GC9A01 240×240 SPI (GPIO16/32/33/34)
- Fault monitoring: nFAULT pins from DRV8353/DRV8873, PGD from LM5069

---

## Workflow

### Making Changes

**Step 1**: Edit the database
```bash
notepad design_database.yaml  # Change component values, GPIO pins, etc.
```

**Step 2**: Regenerate files
```bash
python scripts/generate_all.py
```
Generates:
- `hardware/BOM_Seed.csv`
- `firmware/include/pins.h`
- `hardware/Net_Labels.csv`
- `Component_Report.md`

**Step 3**: Verify (CRITICAL - all 9 scripts must PASS)
```bash
python scripts/run_all_verification.py
```

**Step 4**: Commit (if verification passes)
```bash
git add -u && git commit && git push
```

**See**: `docs/NEW_WORKFLOW_GUIDE.md` for detailed instructions
**See**: `QUICKSTART.md` for quick reference

### Verification Suite

**Database-driven** (all 9 scripts read from design_database.yaml):
1. `check_database_schema.py` - Database structure (117 components, 35 GPIO, 7 ICs)
2. `check_value_locks.py` - 17 locked component values
3. `check_pinmap.py` - 35 GPIO pin assignments
4. `check_netlabels_vs_pins.py` - 44 required net labels
5. `check_kicad_outline.py` - 80×50mm board geometry
6. `check_5v_elimination.py` - 5V rail elimination
7. `check_ladder_bands.py` - Button ladder voltage bands
8. `verify_power_calcs.py` - 8 power calculations
9. `check_bom_completeness.py` - 61 critical IC components

**Run all**: `python scripts/run_all_verification.py` (recommended)

**Optional** (not in main suite):
- `check_power_budget.py` - Component stress analysis
- `check_frozen_state_violations.py` - Obsolete value detection

---

## Critical Values (Locked)

| Component | Value | Purpose |
|-----------|-------|---------|
| RS_IN | 3.0mΩ | LM5069 ILIM = 18.3A |
| R_ILIM | 1.58kΩ | DRV8873 ILIM = 3.3A |
| R_IPROPI | 1.00kΩ | DRV8873 current mirror |
| R_VBAT_TOP | 140kΩ | Battery voltage divider |
| R_VBAT_BOT | 10kΩ | Battery voltage divider |
| RS_U/V/W | 2.0mΩ | Motor phase shunts (5W) |
| RFBT | 100kΩ | LMR33630 feedback (3.3V) |
| RFBB | 43.2kΩ | LMR33630 feedback (3.3V) |
| Board | 80×50mm | Credit-card compatible |

**Changing locked values requires**:
1. Update `design_database.yaml`
2. Regenerate files
3. Update `FROZEN_STATE_REV_C4b.md`
4. Document rationale

---

## Documentation

**Essential (root directory)**:
- `CLAUDE.md` - AI agent guide, verification workflow
- `QUICKSTART.md` - Quick reference (verification, common tasks)
- `VERIFICATION_SYSTEM_COMPLETE.md` - Database migration report (9/9 passing)
- `FROZEN_STATE_REV_C4b.md` - Authoritative frozen design
- `MANDATORY_PREFAB_CHECKLIST.md` - Pre-fabrication checks
- `INIT.md` - Session initialization
- `design_database.yaml` - Single source of truth (117 components, 35 GPIOs, 7 ICs)

**Guides (docs/)**:
- `NEW_WORKFLOW_GUIDE.md` - Database system usage
- `POWER_BUDGET_MASTER.md` - Power calculations
- `BRINGUP_CHECKLIST.md` - Bring-up procedures
- `DESIGN_REVIEW_WORKFLOW.md` - Design review process

**Reports (reports/)**:
- `2025-11-14/` - Latest (database system test results)
- `2025-11-13/` - BOM completeness fix (23 components)
- `2025-11-12/` - Board optimization, 5V elimination

**Complete index**: See `docs/DOCS_INDEX.md`

---

## Dependencies

**Hardware**:
- KiCad 8.0+ (PCB design)
- ESP32-S3 board support for Arduino IDE

**Software**:
- Python 3.9+ (verification scripts, generators)
- PyYAML (`pip install pyyaml`)
- Arduino IDE 2.x or arduino-cli

**Optional**:
- Pre-commit hooks (automatic verification)
- Git LFS (for large datasheet PDFs)

---

## Getting Started

**New Session (AI Agents or Humans)**:
1. Run `python scripts/run_all_verification.py` (verify system integrity - all 9 must PASS)
2. Read `QUICKSTART.md` (quick reference for verification and common tasks)
3. Read `INIT.md` (project status, current locks)

**For AI Agents**:
1. Read `CLAUDE.md` (workflow, anti-drift rules, verification)
2. Read `VERIFICATION_SYSTEM_COMPLETE.md` (database system architecture)
3. Read `docs/NEW_WORKFLOW_GUIDE.md` (understand database workflow)

**For Humans**:
1. Read `QUICKSTART.md` (quick start guide)
2. Review `FROZEN_STATE_REV_C4b.md` (frozen design state)
3. Check `MANDATORY_PREFAB_CHECKLIST.md` before ordering PCBs

**For Firmware Development**:
1. Review `firmware/include/pins.h` (35 GPIO assignments - auto-generated)
2. See `CLAUDE.md` Section "Firmware Development"
3. Read `docs/BRINGUP_CHECKLIST.md` (safety verification)

**For Hardware Design**:
1. Read `hardware/README.md` (schematic scaffold plan)
2. Review `docs/POWER_BUDGET_MASTER.md` (power calculations)
3. Check `docs/DESIGN_REVIEW_WORKFLOW.md` (design process)

---

## Project History

**Nov 15, 2025**: Database migration complete - all 9 verification scripts now database-driven (100% passing)
**Nov 14, 2025**: Single-source-of-truth database system implemented
**Nov 13, 2025**: BOM completeness verification (23 missing components found & fixed)
**Nov 12, 2025**: Board optimization (80×50mm), 5V rail elimination, thermal verification
**Nov 11, 2025**: Comprehensive verification suite established
**Nov 10, 2025**: Power budget analysis, component stress verification
**Nov 9, 2025**: Initial commit, project scaffold created

**See**: `VERIFICATION_SYSTEM_COMPLETE.md` for database migration report
**See**: `reports/` directory for detailed verification reports by date

---

## License & Warnings

**AVIATION TOOL - SAFETY CRITICAL**

This design includes mandatory safety features:
- Redundant stop inputs
- Motor/actuator interlocks
- Fault latching
- Watchdog timers

**DO NOT BYPASS SAFETY FEATURES**

Firmware must enforce:
- Battery UV cutoff (19.5V minimum)
- Motor/actuator mutual exclusion
- Actuator 10s timeout
- Fault state requires IDLE to clear

**See**: `docs/BRINGUP_CHECKLIST.md` for safety verification procedures

---

## Contact & Support

**GitHub**: https://github.com/JBCox/SEDU
**Issues**: Use GitHub Issues for bug reports
**Documentation**: See `docs/DOCS_INDEX.md` for complete file index

**For AI agents**: All workflows documented in `CLAUDE.md` and `README_FOR_CODEX.md`

---

**Last Updated**: 2025-11-15
**Revision**: C.4b (Frozen)
**Verification**: 9/9 scripts passing (100%) - database migration complete
**Status**: Ready for schematic entry
**Next Step**: Implement KiCad schematics per `hardware/README.md` scaffold plan
