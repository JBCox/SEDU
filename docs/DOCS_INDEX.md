# Documentation Index

**Last Updated**: 2025-11-15
**Organization**: Cleaned up and reorganized for clarity

---

## Root Directory (Essential Files Only)

**Core Documentation**:
- `CLAUDE.md` — AI agent guide (workflow, verification, anti-drift rules)
- `README_FOR_CODEX.md` — Codex CLI agent guide
- `AGENTS.md` — Contributor rules and conventions
- `INIT.md` — Session initialization steps and current locks summary

**Critical Design State**:
- `FROZEN_STATE_REV_C4b.md` — Authoritative frozen design state (Rev C.4b)
- `MANDATORY_PREFAB_CHECKLIST.md` — 10-section pre-fabrication verification checklist

**Quick Reference**:
- `QUICKSTART.md` — Quick start guide for new sessions (verification workflow, common tasks)
- `Datasheet_Notes.md` — Distilled notes from vendor datasheets
- `Component_Report.md` — Per-IC project roles and locked values (GENERATED)
- `VERIFICATION_SYSTEM_COMPLETE.md` — Database migration completion report (9/9 scripts passing)

**Database & Workflow**:
- `design_database.yaml` — Single source of truth for all design values (117 components, 35 GPIOs, 7 ICs)

---

## docs/ Directory (Specifications & Guides)

### Canonical Specifications
- `SEDU_Single_PCB_Parity_Corrected_RevC4a_Final.md` — SSOT (pins/spec/locks)
- `POWER_BUDGET_MASTER.md` — Comprehensive power calculations and stress analysis
- `DEVIATIONS_FROM_LEGACY.md` — Explicit differences from legacy design

### Workflow & Process
- `NEW_WORKFLOW_GUIDE.md` — Single-source-of-truth database workflow (COMPLETE GUIDE)
- `DESIGN_REVIEW_WORKFLOW.md` — Step-by-step design review process
- `PROJECT_RULES.md` — Documentation workflow and tool-version capture
- `SESSION_STATUS.md` — Snapshot of current state and next actions

### Checklists & Guides
- `BRINGUP_CHECKLIST.md` — Step-by-step bring-up instructions
- `ORDER_CHECKLIST.md` — Go/no-go steps for fabrication and assembly handoff
- `SCHEMATIC_WIRING_GUIDE.md` — Explicit net-by-net wiring instructions

### Reference
- `DATASHEET_LINKS.md` — Authoritative product/datasheet links
- `TOOL_VERSIONS.md` — Record of KiCad/Python versions for reproducibility

### Archive
- `docs/archive/` — Superseded documentation and implementation notes
  - `AI_COLLABORATION.md` — Historical multi-AI coordination log (196KB)
  - `BRINGUP_CHECKLIST_ENHANCEMENT.md` — Implementation notes
  - `GITHUB_ISSUES.md` — Issue tracking notes
  - `IMPLEMENTATION_SUMMARY.md` — Implementation summaries
  - `CHANGELOG.md` — Running change log (if present)

---

## reports/ Directory (Verification Reports)

### 2025-11-14 (Latest - Database System)
- `WORKFLOW_TEST_RESULTS.md` — Single-source-of-truth workflow test results

### 2025-11-13 (BOM Completeness & Multi-Agent Verification)
- `BOM_COMPLETENESS_ISSUE_RESOLUTION.md` — 23 missing components found and resolved
- `CLEAN_SWEEP_FINAL_STATUS.md` — Systematic cleanup report
- `DEEP_VERIFICATION_REPORT.md` — Datasheet-driven ground truth verification
- `FINAL_MULTI_AGENT_VERIFICATION_REPORT.md` — 4 parallel agent comprehensive verification
- `AGENT_3_COMPONENT_VALUE_VERIFICATION.md` — Component values cross-check
- `AGENT_3_EXECUTIVE_SUMMARY.md` — Component verification executive summary
- `THERMAL_EXECUTIVE_SUMMARY_2025-11-13.md` — Thermal verification summary
- `THERMAL_VERIFICATION_AGENT1_COMPREHENSIVE_REPORT.md` — Comprehensive thermal analysis
- `AGENT5_DESIGN_INTEGRATION_REPORT.md` — Design integration verification

### 2025-11-12 (Board Optimization & 5V Elimination)
- `80x50mm_BOARD_VERIFICATION_SUMMARY.md` — Board size optimization (optimized from 75×55mm to 80×50mm)
- `THERMAL_VIA_VERIFICATION_REPORT_2025-11-12.md` — Thermal via requirements
- `VERIFICATION_AGENT_V5_FINAL_REPORT.md` — Comprehensive verification
- `Board_Critical_Dimensions_Check.txt` — Dimensional verification
- `Board_Layout_Zones_80x50mm.txt` — Layout zone definitions
- `COMPONENT_VERIFICATION_REPORT_2025-11-12.md` — Component verification

### 2025-11-11 (Earlier Verifications)
- `COMPREHENSIVE_VERIFICATION_REPORT_2025-11-11.md`
- `FINAL_VERIFICATION_REPORT_2025-11-11.md`
- `CRITICAL_FINDINGS_2025-11-11.md`
- `TECHNICAL_AUDIT_2025-11-11.md`

### Other Reports
- `GPIO_VERIFICATION_REPORT.txt` — GPIO pin verification
- `README.md` — Reports directory index

---

## hardware/ Directory (KiCad Project)

### KiCad Project Files
- `SEDU_PCB.kicad_pro` — KiCad project file
- `SEDU_PCB.kicad_pcb` — PCB layout (80×50mm outline, 4× M3 holes)
- `SEDU_PCB.kicad_sch` — Top-level schematic (hierarchical sheets)

### Hierarchical Sheets
- `Power_In.kicad_sch` — LM5069-1 / input protection
- `Bucks.kicad_sch` — LMR33630ADDAR 24V→3.3V single-stage
- `USB_Prog.kicad_sch` — TPS22919 → TLV75533 (USB-only)
- `MCU.kicad_sch` — ESP32-S3-WROOM-1 connections
- `Motor_Driver.kicad_sch` — DRV8353RS + MOSFET bridge + shunts
- `Actuator.kicad_sch` — DRV8873-Q1
- `LCD_Connector.kicad_sch` — GC9A01 SPI connector and backlight
- `IO_UI.kicad_sch` — Button ladder, Start/Stop, buzzer/LEDs

### Design Data (GENERATED from design_database.yaml)
- `BOM_Seed.csv` — Bill of materials (117 components) **[AUTO-GENERATED]**
- `Net_Labels.csv` — Canonical net names (44 nets) **[AUTO-GENERATED]**

### Reference Files
- `Schematic_Place_List.csv` — Per-sheet placement list
- `Symbol_Map.md` — Symbol and footprint suggestions
- `Connectors_J_LCD_J_UI.md` — Daughterboard connector pinouts
- `Mounting_And_Envelope.md` — Board size, holes, stackup, keep-outs
- `SEDU_PCB_Sheet_Index.md` — Per-sheet notes and locked values
- `ERC_Notes.md` — How to mark No-ERC and add PWR_FLAGs
- `Symbol_Footprint_Notes.md` — Package choices and assembly practicality
- `Footprint_Assignments.csv` — Ready-to-paste footprint mappings
- `ASSEMBLY_NOTES.md` — Critical assembly requirements [LOCKED]

### Library Files
- `sym-lib-table` — Project symbol library table
- `fp-lib-table` — Footprint library table
- `lib/SEDU_Placeholders.kicad_sym` — Local symbol library
- `lib/SEDU.pretty/R_2728_4T_Kelvin.kicad_mod` — Custom Kelvin sense footprint
- `Library_Setup.md` — How to add local symbol lib

### Documentation
- `README.md` — Scaffold plan, nets, connectors, ERC/DRC expectations

---

## firmware/ Directory (ESP32-S3 Code)

### Core Files
- `include/pins.h` — GPIO pin definitions (35 pins) **[AUTO-GENERATED]**
- `src/main.ino` — Main control loop, safety interlocks

### Modules
- `src/sensors.{cpp,h}` — Battery/ladder/IPROPI ADC, motor CSA
- `src/rpm.{cpp,h}` — Hall edge counting (24 edges/rev for 8-pole motor)
- `src/actuator.{cpp,h}` — DRV8873 PH/EN control
- `src/input_ladder.{cpp,h}` — Button voltage classification
- `src/lcd_gc9a01.{cpp,h}` — GC9A01 240×240 SPI display
- `src/spi_drv8353.{cpp,h}` — DRV8353RS SPI config (gain=20V/V)

---

## scripts/ Directory (Verification & Generation)

### Database System
**Master Generator**:
- `generate_all.py` — Runs all 4 generators in sequence

**Individual Generators**:
- `generate_bom.py` — Creates hardware/BOM_Seed.csv from database
- `generate_pins_h.py` — Creates firmware/include/pins.h from database
- `generate_netlabels.py` — Creates hardware/Net_Labels.csv from database
- `generate_component_report.py` — Creates Component_Report.md from database

### Database-Driven Verification (9 scripts - ALL PASSING)
**Master Verification Runner**:
- `run_all_verification.py` — Runs all 9 verification scripts with summary (RECOMMENDED)

**Core Verification Suite** (all read from design_database.yaml):
- `check_database_schema.py` — Validates design_database.yaml structure (117 components, 35 GPIO, 7 ICs)
- `check_value_locks.py` — Checks 17 locked component values
- `check_pinmap.py` — Validates 35 GPIO assignments (firmware ↔ database)
- `check_netlabels_vs_pins.py` — Confirms 44 net labels exist (auto-built from database)
- `check_kicad_outline.py` — Verifies PCB outline 80×50mm and M3 holes (reads database)
- `check_5v_elimination.py` — Verifies 5V rail elimination (reads banned lists from database)
- `check_ladder_bands.py` — Verifies button ladder voltage bands (database ↔ firmware)
- `verify_power_calcs.py` — Verifies 8 power calculations (all values from database)
- `check_bom_completeness.py` — Verifies 61 critical IC components present (reads database)

### Optional Verification Scripts
**Note**: Not in main suite, run separately as needed.

- `check_power_budget.py` — Component power ratings vs applied stress (exit code 1 expected for known thermal issues)
- `check_frozen_state_violations.py` — Scans docs for obsolete values (prevents drift)

### Utility Scripts
- `check_kicad_versions.py` — Prints KiCad file format versions
- `check_policy_strings.py` — Blocks banned strings outside allowlisted files
- `check_docs_index.py` — Verifies DOCS_INDEX.md and reports unindexed artifacts
- `thermal_analysis.py` — Thermal calculations for power components

---

## Datasheets

**Location**: `docs/datasheets/`

- `DRV8353RS_datasheet.pdf`
- `DRV8873-Q1_datasheet.pdf`
- `LM5069_datasheet.pdf`
- `LMR33630AF_datasheet.pdf`
- `TPS22919_datasheet.pdf`
- `Electrocraft - RPX32-DataSheet-US.pdf`
- ~~`TPS62133_datasheet.pdf`~~ (OBSOLETE - 5V rail eliminated)

**Archive**: `archive/datasheets/` contains extracted text and obsolete parts

---

## Archive

**Location**: `archive/`

- `datasheets/` — Extracted text and obsolete datasheet files
- `legacy-docs/` — Original harness translation and legacy wiring diagrams

---

## Database-Driven Workflow

**Single Source of Truth**: `design_database.yaml`

**To make design changes**:
```bash
# 1. Edit database (ONLY file to manually edit)
notepad design_database.yaml

# 2. Regenerate all files
python scripts/generate_all.py

# 3. Verify (CRITICAL - all 9 scripts must PASS)
python scripts/run_all_verification.py

# 4. Commit (if verification passes)
git add -u && git commit && git push
```

**Generated files** (DO NOT edit manually):
- `hardware/BOM_Seed.csv` (117 components)
- `firmware/include/pins.h` (35 GPIO pins)
- `hardware/Net_Labels.csv` (44 net labels)
- `Component_Report.md` (per-IC documentation)

**Benefits**:
- Zero documentation drift (impossible by design)
- Auto-updating verification (reads database directly)
- Single point of edit (only modify design_database.yaml)
- Proven bug detection (found 2 critical bugs during migration)

**See**: `docs/NEW_WORKFLOW_GUIDE.md` for complete usage guide
**See**: `VERIFICATION_SYSTEM_COMPLETE.md` for system architecture and migration report

---

## Quick Navigation

**Starting a new session?**
→ Read `INIT.md` then run `python scripts/run_all_verification.py`

**Quick reference guide?**
→ Read `QUICKSTART.md` (verification workflow, common tasks, troubleshooting)

**Understanding the verification system?**
→ Read `VERIFICATION_SYSTEM_COMPLETE.md` (database migration, 9/9 scripts passing)

**Making design changes?**
→ Read `docs/NEW_WORKFLOW_GUIDE.md` (database-driven workflow)

**Understanding frozen state?**
→ Read `FROZEN_STATE_REV_C4b.md` (locked design values for Rev C.4b)

**Pre-fabrication checks?**
→ Read `MANDATORY_PREFAB_CHECKLIST.md` (10-section checklist)

**Power calculations?**
→ Read `docs/POWER_BUDGET_MASTER.md` (comprehensive power analysis)

**Firmware development?**
→ See `firmware/` directory and `CLAUDE.md` Section "Firmware Development"

**Verification status?**
→ Run `python scripts/run_all_verification.py` for current status

---

**Document Status**: Current as of 2025-11-15
**Organization**: Root cleaned (11 essential files), database-driven verification (9/9 passing), guides in docs/
**Verification System**: Database migration complete - all scripts read from design_database.yaml
**Maintenance**: Update this index when adding/removing/moving documentation files
