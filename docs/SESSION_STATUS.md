# Session Status — SEDU (Rev C.4b Snapshot)

## What’s Locked
- 24 V actuator default; DRV8873 VM tied to protected 24 V via 0 Ω link.
- DRV8873 locks: R_ILIM = 1.58 kΩ (≈3.3 A), R_IPROPI = 1.00 kΩ; IPROPI → ADC1_CH1 (GPIO2) and test pad.
- USB programming‑only: TPS22919 → TLV75533; radios OFF; USB never powers tool.
- DRV8353 decoupling: CPL‑CPH 47 nF; VCP, VGLS, DVDD 1 µF.
- Battery divider: 49.9 k / 6.80 k (0.1%); RC at pin 1–4.7 k + 0.1 µF.
- GPIO map: per SSOT and firmware/include/pins.h (checker PASS).

## What’s New in Hardware/
- README.md: KiCad scaffold plan, sheet list, nets, connectors, ERC/DRC expectations, “how to resume”.
- SEDU_PCB_Sheet_Index.md: per‑sheet component/value summary.
- Net_Labels.csv: canonical nets matching pins.h & SSOT.
- Connectors_J_LCD_J_UI.md: pinouts and cable rules for the daughterboard.
- Mounting_And_Envelope.md: outline, holes, stack guidance.
- BOM_Seed.csv: seed list for key ICs and passives (first spin).
- Schematic_Place_List.csv: symbol/value placement list by sheet.
- Symbol_Map.md: drop‑in symbol/footprint suggestions from stock KiCad libs.
- ERC_Notes.md: what to mark No‑ERC and where to place PWR_FLAG.
- SCHEMATIC_WIRING_GUIDE.md: exact nets and connections per sheet to wire quickly.
- sym-lib-table: project adds the local `SEDU` symbol lib automatically.
- SEDU_Placeholders.kicad_sym: default Footprint fields set for LM5069‑1, DRV8873‑Q1, DRV8353RS.
- Footprint_Assignments.csv: mapping for common refs → footprints (to copy/paste into Field Editor if desired).
- U1 MCU footprint/symbol: set to `RF_Module:ESP32-S3-WROOM-1` (no placeholder). Verify memory variant (N16R8) compatibility; package is common across variants.

## Next Actions (Me)
- Create KiCad project files and draw the hierarchical sheets.
- Place board outline (≤80×60), 4× M3 holes, and connectors (edge‑aligned).
- Run ERC and record notes under this file; adjust symbols/flags until clean.

## Next Actions (You)
- Confirm UI/LCD cable length target (≤200 mm); I’ll finalize connector series/footprints.
- If available, provide a photo/drawing of available mounting space/holes; I’ll place the 4 M3s accordingly.

## Resuming Later
- Read this file and hardware/README.md for exact state.
- Run `python3 scripts/check_pinmap.py` to confirm no drift if you touch pins.
