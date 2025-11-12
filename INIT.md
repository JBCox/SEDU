# Session Init

1. Read `AGENTS.md` for contributor expectations.  
2. Review `docs/PROJECT_RULES.md` to understand documentation layers, change logging, and tool-version recording.  
3. Check `docs/archive/CHANGELOG.md` for the latest decisions before editing anything.  
4. Log new findings (calculations, tool behaviors, design changes) in a dated note under `docs/`, then summarize in the changelog when finalized.  
5. Treat legacy VESC information as reference only; all forward work must align with `New Single Board Idea.md` and `Datasheet_Notes.md`.
6. Legacy hardware stack = 24 V battery -> VESC 4.12 -> ElectroCraft RPX32 BLDC, VESC 5 V -> ESP32-C6 dev board (UART to VESC, SPI to GC9A01 LCD, GPIO to DRV8871 actuator driver), plus the two-button resistor ladder into one ADC; preserve this behavior in every redesign note.
7. The single-board effort must keep identical operator states/safety interlocks as the aerospace PFD harness while integrating quality-of-life upgrades (dedicated bucks, hot-swap, better docs); call out any deviation from the original wiring/BOM in both schematic notes and component logs.

## ⚠️ MANDATORY VERIFICATION AFTER ANY FIX

**Rule**: After fixing ANY bug, updating ANY component value, or changing ANY design parameter, you MUST run ALL verification scripts to ensure documentation consistency across the project.

**Why**: Past issues (e.g., battery divider mismatch: firmware had 140kΩ/10kΩ, but spec said 49.9kΩ/6.8kΩ) were caused by updating one file but missing others. This rule prevents documentation drift.

**Required Commands** (ALL must PASS before considering fix complete):
```bash
# Core verification suite (run in order)
python scripts/check_value_locks.py      # Critical component values consistent
python scripts/check_pinmap.py           # Firmware ↔ documentation GPIO map
python scripts/check_power_budget.py     # Component ratings vs applied stress
python scripts/check_netlabels_vs_pins.py # Schematic net label consistency
python scripts/check_kicad_outline.py    # PCB geometry (80×60mm, M3 holes)
python scripts/verify_power_calcs.py     # Power calculations verification
```

**When Each Script Fails**:
- `check_value_locks.py` → Fix inconsistency in BOM, SSOT, or firmware immediately
- `check_pinmap.py` → Update GPIO tables in docs to match firmware or vice versa
- `check_power_budget.py` → Exit code 1 is EXPECTED if known issues exist (DRV8873 thermal, J_MOT rating); verify new issues weren't introduced
- Others → Follow script output to resolve

**Examples of Changes Requiring Verification**:
- ✅ Changed resistor value (R_ILIM, battery divider, etc.)
- ✅ Swapped IC or component package
- ✅ Modified firmware GPIO assignment
- ✅ Updated power calculations or current limits
- ✅ Fixed calibration constants
- ✅ Changed connector or wire gauge

**Document Updates in AI_COLLABORATION.md**: After running verification and confirming PASS, log the fix as a new PROPOSAL entry with verification results.

---

## Current Lock-Ins (Rev C.4a + C.4b)

- Battery-only operation. USB-C is programming-only and never powers the tool.  
- USB programming rail: `TPS22919 -> TLV75533 (3.3 V)`; radios OFF when on USB.  
- Motor stage: `DRV8353RS` + external 60 V MOSFETs; 3 × 2 mΩ shunts; CSA gain 20 V/V.  
- Actuator: `DRV8873-Q1 (PH/EN)`; 24 V default supply (VM tied to protected 24 V). Locks for first spin: `R_ILIM = 1.58 kΩ (≈3.3 A)`, `R_IPROPI = 1.00 kΩ`; IPROPI routed to `GPIO2` and a test pad.  
- Display: `GC9A01` 240×240 SPI (write-only, MISO NC); `CS_LCD=GPIO16`; backlight 10–20 mA.  
- MCU: `ESP32-S3-WROOM-1-N16R8`; keep GPIO-JTAG disabled so MCPWM owns `GPIO38–43`.  
- ADC locks: Battery divider `140 kΩ / 10.0 kΩ (1%)` with 1 kΩ series + 0.1 µF at the pin; ladder on `GPIO4` with fault bands `<0.20 V` and `>3.40 V`.
- SPI: DRV CS `GPIO22`; LCD CS `GPIO16`; `SCK=GPIO18`, `MOSI=GPIO17`, `MISO=GPIO21` (write-only LCD).  

Mechanical/PCB locks (first spin):  
- Board outline target: **80 × 60 mm**; 4 × M3 holes (3.2 mm finished) at approx. (4,4), (76,4), (4,56), (76,56).  
- 4-layer stack recommended; antenna keep-out per Espressif.  
- 12 V actuator buck footprints: **omitted** to minimize area (24 V actuator default).  

Bring-up confirmations (locked values; verify on bench):
- LM5069 variant: **LM5069-1 (latch-off)** is locked. Start with **C_dv/dt = 33 nF**; adjust to keep inrush ≤ ~0.5×ILIM.  
- DRV8873 current limit: **R_ILIM = 1.58 kΩ (~3.3 A)** and **R_IPROPI = 1.00 kΩ** are locked; verify actual actuator steady current and adjust in Rev B if needed.  

## Quick Start (Novice-Friendly)

1. Run verifiers (see "MANDATORY VERIFICATION AFTER ANY FIX" section above):
   - `python3 scripts/check_value_locks.py` (LM5069-1, DRV8873 ILIM/IPROPI, battery divider 140kΩ/10kΩ, board size)
   - `python3 scripts/check_pinmap.py` (doc ↔ firmware pins)
   - `python3 scripts/check_power_budget.py` (component ratings vs stress; exit code 1 expected for known issues)
   - `python3 scripts/check_netlabels_vs_pins.py` (required net labels exist)
   - `python3 scripts/check_kicad_outline.py` (board size ≤80×60 mm and 4× M3 holes present)
   - `python3 scripts/verify_power_calcs.py` (power calculations verification)
   - `python3 scripts/check_policy_strings.py` (no banned legacy strings reintroduced)
   - `python3 scripts/check_kicad_versions.py` (report file format versions; ok to upgrade on save)
   - `rg -n -S "TLV75533|TPS22919" docs/ Component_Report.md` (USB policy present)
   - `rg -n -S "GC9A01|MISO NC|CS_LCD|GPIO16" docs/ New\ Single\ Board\ Idea.md Component_Report.md` (LCD locks present)  
2. Program firmware (battery disconnected): plug USB-C; confirm logs show battery %, ladder state, RPM=0.  
3. Battery-only test: disconnect USB; power from battery; verify the tool cannot power from USB alone.  
4. Buttons: press Start/Stop; confirm ladder bands and discrete GPIOs both gate motion.  
5. Actuator sanity: brief extend pulses; adjust ILIM in firmware once current is known.  

## Tools & File Layout

- KiCad projects live under `hardware/` (create `SEDU_PCB.kicad_pro`).  
- Datasheets: prefer linking; PDFs that must be stored go in the project root per `AGENTS.md`.  
- Record tools used in `docs/TOOL_VERSIONS.md` (KiCad version especially).  
- Single source of truth: `docs/SEDU_Single_PCB_Parity_Corrected_RevC4a_Final.md` governs pins/spec.  

UI Daughterboard interfaces (locked):  
- `J_LCD` (8): 3V3, GND, SCK, MOSI, CS_LCD, DC, RST, LEDK/PWM; SCK/MOSI series 22–33 Ω near MCU; LCD MISO NC.  
- `J_UI` (8): 3V3, GND, BTN_SENSE, START_DIG, STOP_NC_DIG, BUZZER, LED1, LED2; BTN_SENSE twisted with GND; 100–220 Ω series + 100 nF at MCU.  

See also: `README_FOR_CODEX.md` for anti-drift rules and the verification commands Codex must run after edits.

## Optional: Git Hooks (Pre-commit)

- Install once: `pip install pre-commit` then `pre-commit install` in the repo root.  
- This runs the same checks before each commit (`.pre-commit-config.yaml`).  

## Artifact Registry & Resumption Rules

- Canonical artifact index: `docs/DOCS_INDEX.md` (list of every doc/script/hardware file and what it is for).  
- Session status: `docs/SESSION_STATUS.md` (what changed in this session, next actions).  
- Rule: whenever we add/rename/remove a file under `docs/`, `hardware/`, `firmware/`, or `scripts/`, update both:  
  - Add the entry to `docs/DOCS_INDEX.md` under the correct section.
  - Append a short note to `docs/SESSION_STATUS.md` (date, reason).  
- Drift check (optional but recommended): run `python3 scripts/check_docs_index.py` to confirm the index references actual files and to list any unindexed artifacts.
