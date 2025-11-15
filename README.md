# SEDU Single-PCB Feed Drill

**Aviation-grade 24V battery-powered handheld tool**
**Rev C.4b - Frozen Design State**

---

## Quick Start

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

## Single-Source-of-Truth Workflow (NEW)

**Problem Solved**: Eliminates documentation drift and endless verification cycles

**How it works**:
1. **Edit ONE file**: `design_database.yaml` (53 components, 35 GPIOs, all design values)
2. **Run generators**: `python scripts/generate_all.py` (creates BOM, pins.h, netlabels, reports)
3. **Verify**: Run 3 database-driven verification scripts
4. **Commit**: All files guaranteed consistent

**See**: `docs/NEW_WORKFLOW_GUIDE.md` for complete guide

---

## Project Structure

```
SEDU/
├── design_database.yaml          ← SINGLE SOURCE OF TRUTH (edit this)
├── CLAUDE.md                      ← AI agent guide
├── FROZEN_STATE_REV_C4b.md       ← Frozen design state
├── MANDATORY_PREFAB_CHECKLIST.md ← Pre-fabrication checklist
├── Component_Report.md            ← Generated component report
│
├── docs/                          ← Specifications & guides
│   ├── NEW_WORKFLOW_GUIDE.md      ← How to use database system
│   ├── POWER_BUDGET_MASTER.md     ← Power calculations
│   ├── BRINGUP_CHECKLIST.md       ← Bring-up procedures
│   └── DOCS_INDEX.md              ← Complete file index
│
├── hardware/                      ← KiCad project
│   ├── SEDU_PCB.kicad_pcb         ← PCB layout (80×50mm)
│   ├── SEDU_PCB.kicad_sch         ← Top-level schematic
│   ├── BOM_Seed.csv               ← Generated BOM (53 components)
│   └── [hierarchical sheets]
│
├── firmware/                      ← ESP32-S3 code
│   ├── include/pins.h             ← Generated GPIO definitions
│   └── src/                       ← Modular firmware
│
├── scripts/                       ← Generators & verification
│   ├── generate_all.py            ← Master generator
│   ├── check_database_schema.py   ← Database validator
│   ├── check_value_locks.py       ← Locked values checker
│   └── check_pinmap.py            ← GPIO validator
│
└── reports/                       ← Verification reports (dated)
    ├── 2025-11-14/                ← Latest (database system)
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
**BOM**: 117 components (53 in database, 64 to migrate)
**Verification**: 10 scripts (3 database-driven, 7 legacy)

**Latest Verification** (2025-11-14):
- ✅ Database schema valid (7 ICs, 53 components, 35 GPIOs)
- ✅ 17 locked values correct
- ✅ 35 GPIO pins validated (no conflicts)
- ✅ Frozen state compliant

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

**Step 3**: Verify
```bash
python scripts/check_database_schema.py
python scripts/check_value_locks.py
python scripts/check_pinmap.py
```

**Step 4**: Commit
```bash
git add -u && git commit && git push
```

**See**: `docs/NEW_WORKFLOW_GUIDE.md` for detailed instructions

### Verification

**Database-driven** (checks design values, not file format):
- `check_database_schema.py` - Validates database structure
- `check_value_locks.py` - Checks 17 locked components
- `check_pinmap.py` - Validates 35 GPIO assignments

**Legacy** (still read old files, will be updated):
- `check_power_budget.py`
- `check_frozen_state_violations.py`
- `check_bom_completeness.py`
- ...and 4 more

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
- `FROZEN_STATE_REV_C4b.md` - Authoritative frozen design
- `MANDATORY_PREFAB_CHECKLIST.md` - Pre-fabrication checks
- `INIT.md` - Session initialization
- `design_database.yaml` - Single source of truth

**Guides (docs/)**:
- `NEW_WORKFLOW_GUIDE.md` - Database system usage
- `POWER_BUDGET_MASTER.md` - Power calculations
- `BRINGUP_CHECKLIST.md` - Bring-up procedures
- `DESIGN_REVIEW_WORKFLOW.md` - Design review process

**Reports (reports/)**:
- `2025-11-14/` - Latest verification (database system)
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

**For AI Agents**:
1. Read `CLAUDE.md` (workflow, anti-drift rules, verification)
2. Run `python scripts/check_database_schema.py` (validate current state)
3. Read `docs/NEW_WORKFLOW_GUIDE.md` (understand database system)

**For Humans**:
1. Read `INIT.md` (project status, current locks)
2. Review `FROZEN_STATE_REV_C4b.md` (frozen design state)
3. Check `MANDATORY_PREFAB_CHECKLIST.md` before ordering PCBs

**For Firmware Development**:
1. Read `firmware/README.md` (if present)
2. See `CLAUDE.md` Section "Firmware Development"
3. Review `firmware/include/pins.h` (GPIO assignments)

**For Hardware Design**:
1. Read `hardware/README.md` (schematic scaffold plan)
2. Review `docs/POWER_BUDGET_MASTER.md` (power calculations)
3. Check `docs/DESIGN_REVIEW_WORKFLOW.md` (design process)

---

## Project History

**Nov 14, 2025**: Single-source-of-truth database system implemented
**Nov 13, 2025**: BOM completeness verification (23 missing components found & fixed)
**Nov 12, 2025**: Board optimization (80×50mm), 5V rail elimination, thermal verification
**Nov 11, 2025**: Comprehensive verification suite established
**Nov 10, 2025**: Power budget analysis, component stress verification
**Nov 9, 2025**: Initial commit, project scaffold created

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

**Last Updated**: 2025-11-14
**Revision**: C.4b (Frozen)
**Status**: Ready for schematic entry
**Next Step**: Implement KiCad schematics per `hardware/README.md` scaffold plan
