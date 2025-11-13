# Documentation Index (What each file is for)

## Top-level
- `AGENTS.md` — contributor rules and conventions for this repo.
- `INIT.md` — session init steps, current locks summary, novice quick start.
- `README_FOR_CODEX.md` — canonical agent guide; anti-drift rules, verifications.
- `Datasheet_Notes.md` — distilled notes from vendor datasheets.
- `Component_Report.md` — per-IC project roles and locked values.
- `Original_Schematic_Translation.md` — legacy harness translation and behavior.
- `docs/DOCS_INDEX.md` — this file; single index of artifacts.
- `docs/BRINGUP_CHECKLIST.md` — step-by-step bring-up instructions.
- `docs/archive/CHANGELOG.md` — running change log (if present).

## Canonical spec & change logs
- `docs/SEDU_Single_PCB_Parity_Corrected_RevC4a_Final.md` — SSOT (pins/spec/locks).
- `docs/DEVIATIONS_FROM_LEGACY.md` — explicit differences from legacy.
- `docs/PROJECT_RULES.md` — doc workflow and tool-version capture.
- `docs/SESSION_STATUS.md` — snapshot of where we are and next actions.
- `docs/SCHEMATIC_WIRING_GUIDE.md` — explicit net‑by‑net wiring instructions per sheet.
- `docs/ORDER_CHECKLIST.md` — go/no‑go steps for fabrication and assembly handoff.
- `docs/DATASHEET_LINKS.md` — authoritative product/datasheet links (preferred to adding new PDFs).
- `docs/TOOL_VERSIONS.md` — record KiCad/Python versions used for reproducibility.
- `docs/DESIGN_REVIEW_WORKFLOW.md` — step-by-step design review process to prevent power issues.
- `docs/POWER_BUDGET_MASTER.md` — comprehensive power calculations and component stress analysis (SSOT for power).

## Hardware (KiCad)
- `hardware/SEDU_PCB.kicad_pro` — KiCad project file.
- `hardware/SEDU_PCB.kicad_sch` — top schematic (add hierarchical sheets here).
- `hardware/Power_In.kicad_sch` — LM5069-1 / input protection sheet.
- `hardware/Bucks.kicad_sch` — LMR33630ADDAR 24→3.3 V single-stage (5V rail eliminated).
- `hardware/USB_Prog.kicad_sch` — TPS22919 → TLV75533 (USB-only) sheet.
- `hardware/MCU.kicad_sch` — ESP32-S3-WROOM-1 connections.
- `hardware/Motor_Driver.kicad_sch` — DRV8353RS + MOSFET bridge + shunts.
- `hardware/Actuator.kicad_sch` — DRV8873-Q1 with R_ILIM/R_IPROPI.
- `hardware/LCD_Connector.kicad_sch` — GC9A01 SPI connector and backlight.
- `hardware/IO_UI.kicad_sch` — button ladder, Start/Stop, buzzer/LEDs.
- `hardware/SEDU_PCB.kicad_pcb` — PCB outline and 4× M3 holes placed (80×60 mm).
- `hardware/sym-lib-table` — project symbol library table (adds SEDU placeholders).
- `hardware/README.md` — scaffold plan, nets, connectors, ERC/DRC expectations, resume steps.
- `hardware/SEDU_PCB_Sheet_Index.md` — per-sheet notes and locked values.
- `hardware/Net_Labels.csv` — canonical net names to use while wiring.
- `hardware/Connectors_J_LCD_J_UI.md` — daughterboard connector pinouts.
- `hardware/Mounting_And_Envelope.md` — board size, holes, stackup, keep-outs.
- `hardware/BOM_Seed.csv` — seed BOM for first spin.
- `hardware/Schematic_Place_List.csv` — per-sheet placement list (refs/values).
- `hardware/Symbol_Map.md` — symbol and footprint suggestions to avoid library hunting.
- `hardware/ERC_Notes.md` — how to mark No-ERC and add PWR_FLAGs.
- `hardware/Symbol_Footprint_Notes.md` — notes on package choices and assembly practicality.
- `hardware/Footprint_Assignments.csv` — ready-to-paste footprint mappings for common refs.
- `hardware/fp-lib-table` — KiCad footprint library table (links custom footprint libraries).
- `hardware/lib/SEDU_Placeholders.kicad_sym` — tiny local symbol lib (LM5069‑1, DRV8873‑Q1, DRV8353RS).
- `hardware/lib/SEDU.pretty/R_2728_4T_Kelvin.kicad_mod` — custom 4-terminal Kelvin sense resistor footprint (2728 package).
- `hardware/Library_Setup.md` — how to add the local symbol lib in KiCad.

## Firmware & scripts
- `firmware/include/pins.h` — locked pins; used by the checker.
- `firmware/src/main.ino` — minimal sketch orchestrating modules (battery, ladder, RPM, IPROPI).
- `firmware/src/input_ladder.h` — ladder thresholds, classification, fault mapping.
- `firmware/src/input_ladder.cpp` — ladder thresholds, classification, fault mapping.
- `firmware/src/sensors.h` — ADC setup + conversions (battery V/% , ladder V, IPROPI A).
- `firmware/src/sensors.cpp` — ADC setup + conversions (battery V/% , ladder V, IPROPI A).
- `firmware/src/actuator.h` — DRV8873 PH/EN control helper.
- `firmware/src/actuator.cpp` — DRV8873 PH/EN control helper.
- `firmware/src/rpm.h` — RPM sampling (ISR-based; optional PCNT stub for future use).
- `firmware/src/rpm.cpp` — RPM sampling (ISR-based; optional PCNT stub for future use).
- `firmware/src/lcd_gc9a01.h` — Minimal LCD init (SPI) + bring‑up splash logging.
- `firmware/src/lcd_gc9a01.cpp` — Minimal LCD init (SPI) + bring‑up splash logging.
- `firmware/src/spi_drv8353.h` — Minimal DRV8353RS SPI init and raw status/ID reads.
- `firmware/src/spi_drv8353.cpp` — Minimal DRV8353RS SPI init and raw status/ID reads.
- `scripts/check_pinmap.py` — ensures pins.h matches the SSOT table.
- `scripts/check_docs_index.py` — verifies this index and reports unindexed artifacts.
- `scripts/check_kicad_outline.py` — verifies PCB outline 75×55 mm and presence/locations of 4× M3 holes at (4,4), (71,4), (4,51), (71,51).
- `scripts/check_netlabels_vs_pins.py` — confirms required net labels exist for firmware/connector coverage.
- `scripts/check_value_locks.py` — cross-checks LM5069-1, DRV8873 R_ILIM/R_IPROPI locks, and board size across docs.
- `scripts/check_policy_strings.py` — blocks banned strings outside allowlisted files.
- `scripts/check_kicad_versions.py` — prints KiCad file format versions for SCH/PCB (upgrade guidance).
- `scripts/check_ladder_bands.py` — verifies ladder bands in SSOT match firmware constants and ordering.
- `scripts/verify_power_calcs.py` — verifies ILIM/Rsense math and worst‑case inrush assumptions.
- `scripts/check_5v_elimination.py` — verifies 5V rail removal and single-stage 24V→3.3V conversion.
- `scripts/check_power_budget.py` — validates component power ratings vs applied stress (voltage/current/power).
- `scripts/thermal_analysis.py` — thermal calculations for power components (junction temp, heatsinking).

## Datasheets
- `docs/datasheets/README.md` — notes on datasheet storage and linkage policy.
- `docs/datasheets/DRV8353RS_datasheet.pdf`
- `docs/datasheets/DRV8873-Q1_datasheet.pdf`
- `docs/datasheets/LM5069_datasheet.pdf`
- `docs/datasheets/LMR33630AF_datasheet.pdf`
- `docs/datasheets/TPS22919_datasheet.pdf`
- `docs/datasheets/TPS62133_datasheet.pdf`
- `docs/datasheets/Electrocraft - RPX32-DataSheet-US.pdf`

## Archive
- `archive/datasheets/LM5069_datasheet.txt` — extracted text (archived).
- `archive/datasheets/TLV75733P_datasheet.pdf` — wrong part (archived).
- `archive/datasheets/TPS22919_datasheet.txt` — extracted text (archived).
- `archive/legacy-docs/GEMINI.md` — legacy overview (archived).
- `archive/legacy-docs/SEDU_PFD_Wiring_and_Function_v0.1.md` — legacy wiring doc (archived).
- `archive/legacy-docs/Original_Schematic_Translation.md` — legacy harness translation (archived copy).
- `archive/legacy-docs/Old_Wiring_Diagram.jpg` — legacy wiring diagram (archived image).
- `archive/legacy-docs/Old_Wiring_Diagram_Buttons.jpg` — legacy button wiring (archived image).
