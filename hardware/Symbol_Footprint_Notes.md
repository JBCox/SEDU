# Symbols & Footprints Notes (First Spin)

- MCU: ESP32-S3-WROOM-1-N16R8 — use KiCad symbol `RF_Module:ESP32-S3-WROOM-1`; footprint `RF_Module:ESP32-S3-WROOM-1`.
- DRV8353RS: TI HTSSOP-48 (or QFN variant if preferred). Start with HTSSOP for easier assembly unless CM can place QFN.
- MOSFETs: SuperSO8 (Infineon OptiMOS, onsemi LFPAK56 alternatives). Ensure copper for heat.
- Shunts: 2512 four-terminal preferred for phase; verify library symbol supports Kelvin pads.
- LM5069-1: MSOP-10 or WSON per datasheet; pick package CM stocks.
- LMR33630AF: RNX/QFN package saves space; verify CM capability; else SOIC variant.
- TPS62133: QFN/DFN; check assembly guidelines.
- DRV8873-Q1: HTSSOP.
- Connectors: JST-GH 1.25 mm 8-pin for J_LCD and J_UI; MicroFit 3.0 for power/device connectors.
- Mounting holes: KiCad "MountingHole_3.2mm_M3" footprints already placed on PCB outline.

Footprint assignments will be finalized after schematic symbols are placed and annotated.
