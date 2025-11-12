# Order Checklist (FAB/Assembly Prep)

1) KiCad Schematic
- ERC clean (LCD MISO allowed NC; PWR_FLAGs placed).
- Net labels match `hardware/Net_Labels.csv`.
- Symbols for LM5069‑1, DRV8873‑Q1, DRV8353RS placed (SEDU lib or vendor symbols).

2) KiCad PCB
- Outline 80×60 mm, 4× M3 holes present (run `python3 scripts/check_kicad_outline.py`).
- Mounting keep‑outs around holes; antenna keep‑out per Espressif.
- High‑di/dt loops and decoupling compact; phase shunts Kelvin.

3) BOM & Footprints
- Generate BOM from schematic; verify key lines against `hardware/BOM_Seed.csv`.
- Ensure footprints match packages (MSOP‑10, HTSSOP‑28/48, VQFN/QFN, PowerPAK SO‑8, 2512, 0805/1206).

4) Fabrication/Assembly Files
- Plot Gerbers + drill + IPC netlist; zip with board name + rev.
- Export Position (Pick‑and‑Place) files.
- Include assembly notes: DNP list (12 V buck not populated), TVS orientation, connector orientations.

5) Bring‑Up
- Include `docs/BRINGUP_CHECKLIST.md` in the order folder for lab use.
- Prepare a harness or jig for USB + 24 V + motor/actuator connectors.

6) Final Sanity
- Run `python3 scripts/check_docs_index.py` and add final notes to `docs/SESSION_STATUS.md`.
