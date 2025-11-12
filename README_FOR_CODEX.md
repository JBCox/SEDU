
# README_FOR_CODEX.md — Canonical Agent Guide (SEDU Single‑PCB Feed Drill)

> **Purpose:** This file tells Codex CLI *exactly* how to behave in this repo. It defines the single source of truth, non‑negotiable rules, file layout, pin maps, component locks, verification commands, and the tasks Codex should run to keep docs, firmware, and hardware in sync.

---

## 0) Single Source of Truth (SSOT)

**Authoritative spec:** `docs/SEDU_Single_PCB_Parity_Corrected_RevC4a_Final.md`  
All other docs **must** align with this file. If there’s a conflict, **Rev C.4a wins**.

**Deviations from legacy:** `docs/DEVIATIONS_FROM_LEGACY.md`  
Any change from the old VESC+DRV8871 harness (e.g., DRV8873 upgrade, discrete Start/Stop lines) must be listed here.

**Never reintroduce (for size/stability):**  
- Legacy VESC PPM/PWM headers  
- “UART‑only VESC fallback” subsections/connectors  
- USB powering the tool during operation (USB is **programming‑only**)  

---

## 1) What This Board Must Do (Parity Rules)

- Control the BLDC motor and linear actuator **exactly like** the legacy tool.
- Keep **Wi‑Fi + BLE** available (ESP32 family), **Arduino‑programmable**.
- UI: **Start/Stop** buttons; **LCD shows battery % + motor RPM/current**; basic Ready/Run/Fault states.
- **Battery (24 V) is the only power during use.** USB‑C is optional and for **programming only**.
- **One PCB** (**75 × 55 mm** optimized from 80×60mm baseline) unless explicitly split in a future rev with trade‑offs.

---

## 2) Locked Electrical Architecture (Rev C.4a)

**Power & protection**  
- **LM5069-1 (latch-off)** hot‑swap / inrush / OV‑UV + **SMBJ33A TVS** at 24 V input.
- **LMR33630ADDAR** 24→3.3 V logic buck (single-stage; 5V rail eliminated).
- **USB programming‑only path:** **TPS22919 (load switch) → TLV75533 (3.3 V LDO)**. Radios **OFF** in this mode. Never back‑feed the main 3.3 V buck. Never run the tool from USB.
 - **Actuator default:** 24 V actuator (DRV8873 VM tied to protected 24 V). Optional 12 V actuator via DNI buck rail.

**Motor stage**  
- **DRV8353RS** 3‑phase gate driver (SPI + integrated CSAs).  
- 6× MOSFETs, 60 V class, ≤ 2 mΩ Rds(on) typical.  
- **Shunts:** 3 × **2 mΩ, 2512, pulse‑rated**, true Kelvin; **CSA gain = 20 V/V**.  
- **FOC‑ready:** CSAs wired to ADC1 with **56–100 Ω + 470 pF** anti‑alias at MCU pin.  
- Default **6‑step + Halls**; FOC path available in firmware.

**Actuator**  
- **DRV8873‑Q1** H‑bridge; ILIM set to **110–120% of actuator’s *continuous* current** (not stall); add TVS on supply.  
- Control: **PH/EN** (GPIO30/31 by default — see pin map).
 - Locks (24 V default): **R_ILIM = 1.58 kΩ (≈3.3 A)**, **R_IPROPI = 1.00 kΩ**.

**Buttons & safety**  
- **NC Stop + Start** on ladder **and** discrete digital GPIOs (redundant).  
- Ladder ADC bands (3.3 V ref): **<0.20 V = FAULT**, **0.75–1.00 V = START**, **1.55–2.10 V = IDLE**, **2.60–3.35 V = STOP**, **>3.40 V = OPEN FAULT**.

**LCD**  
- **GC9A01** SPI 240×240, 3.3 V logic/backlight; **write‑only** (MISO NC).  
- Share SPI SCK/MOSI with DRV bus; **dedicated CS for LCD** (default **GPIO16**) so DRV and LCD never share CS.  
- If cabled, add **22–33 Ω** series resistors on SCK/MOSI near MCU; route away from phase nodes. Backlight LEDK 10–20 mA (FET or series resistor).

**RF & layout**  
- ESP32‑S3‑WROOM‑1‑N16R8 (chip antenna) with **‑1U (u.FL) alt stuffing** option. Maintain antenna keep‑out per datasheet.  
- “Mecca” star ground at battery negative; separate **PGND/LGND**; single tie near sense. Keep high di/dt loops tight.

---

## 3) Locked GPIO / Signal Map (Rev C.4a)

> These assignments are **canonical**. If you change them, update **this table**, `firmware/include/pins.h`, and re‑run the checker.

| Function                   | ESP32‑S3 Pin(s)             | Notes |
|---                         |---                          |---|
| **USB D− / D+**            | GPIO19 / GPIO20             | Series 22–33 Ω; ESD near connector |
| **DRV8353 SPI**            | SCK=GPIO18, MOSI=GPIO17, MISO=GPIO21, **CS_DRV=GPIO22** | LCD shares SCK/MOSI only |
| **LCD (GC9A01 SPI)**       | SCK=GPIO18, MOSI=GPIO17, **CS_LCD=GPIO16**, MISO=NC     | Write‑only panel; DC/RST per panel header |
| **CSA ADCs (FOC)**         | **U=GPIO5 (ADC1_CH4), V=GPIO6 (ADC1_CH5), W=GPIO7 (ADC1_CH6)** | 56–100 Ω + 470 pF at MCU |
| **Battery ADC**            | **GPIO1 (ADC1_CH0)**        | 0.1% divider; 2‑point cal |
| **Button ladder ADC**      | **GPIO4 (ADC1_CH3)**        | Bands: <0.20 (fault), 0.75–1.00 (START), 1.55–2.10 (IDLE), 2.60–3.35 (STOP), >3.40 (fault) |
| **Start / Stop (digital)** | **GPIO23 / GPIO24**         | Redundant with ladder |
| **Halls A/B/C**            | GPIO8 / GPIO9 / GPIO13      | PCNT |
| **FEED_SENSE**             | GPIO14                      | RC deglitch |
| **Buzzer / LEDs**          | BUZ=GPIO25; LED1/2/3=GPIO26/27/28 |  |
| **MCPWM HS U/V/W**         | **GPIO38 / GPIO39 / GPIO40**| Gate driver EN pulled low at boot |
| **MCPWM LS U/V/W**         | **GPIO41 / GPIO42 / GPIO43**| IO35–37 unavailable (PSRAM) |
| **Actuator DRV8873 PH/EN** | **GPIO30 / GPIO31**         | EN default low |

> Free spares (test pads): **GPIO11, GPIO12** (ADC2_CH0/1).  
> Ensure GPIO‑JTAG remains **disabled** so MCPWM owns 38–43 (default in Arduino).

---

### Auxiliary Signals (for completeness)

These are required by firmware but omitted from the main table for brevity:

- `GPIO10 (ADC1_CH9)` → `kAdcNtc` — FET NTC sense (thermal protection)
- `GPIO2 (ADC1_CH1)` → `kAdcIpropi` — DRV8873 IPROPI current mirror
- `GPIO32` → `kLcdDc` — LCD Data/Command
- `GPIO33` → `kLcdRst` — LCD Reset

Keep these synchronized with `firmware/include/pins.h` and the SSOT narrative.

---

## 4) Firmware Constants (pins.h) — Required Names

`firmware/include/pins.h` **must** define these constants to mirror the table above:

```
kUsbDm=19, kUsbDp=20,
kSpiSck=18, kSpiMosi=17, kSpiMiso=21, kSpiCsDrv=22, kSpiCsLcd=16,
kAdcCsaU=5, kAdcCsaV=6, kAdcCsaW=7, kAdcBattery=1, kAdcLadder=4,
kStartDigital=23, kStopDigital=24, kHallA=8, kHallB=9, kHallC=13,
kFeedSense=14, kBuzzer=25, kLed1=26, kLed2=27, kLed3=28,
kMcpwmHsU=38, kMcpwmHsV=39, kMcpwmHsW=40, kMcpwmLsU=41, kMcpwmLsV=42, kMcpwmLsW=43,
kActuatorPh=30, kActuatorEn=31
```

If any constant differs in silicon/layout, **update both** the table and `pins.h` together and re‑run the checker.

---

## 5) Components — Locked Decisions

- **Hot‑swap:** LM5069 + external FET (size for surge), **SMBJ33A** TVS at 24 V.
- **24→3.3 buck (single-stage):** LMR33630ADDAR (5V rail eliminated for simpler design).
- **USB programming rail:** **TPS22919 → TLV75533**, radios **OFF**, never powers tool.  
- **Gate driver:** DRV8353RS; **CSAs gain 20 V/V**, RC at MCU.  
- **Shunts:** 2 mΩ, 2512, pulse‑rated (Bourns/Vishay/KOA).  
- **Actuator:** DRV8873‑Q1 (PH/EN).  
- **LCD:** GC9A01 SPI 240×240 (write‑only), backlight LEDK 10–20 mA.  
- **ESP32:** S3‑WROOM‑1‑N16R8 (chip antenna), **‑1U u.FL alt** allowed.  
- **Connectors:** locking/vibration‑rated families only.

If a substitute is required, **propose it with reasons** and update `docs/DEVIATIONS_FROM_LEGACY.md` if it changes behavior or wiring.

---

## 6) Repo Layout (expected)

```
/docs
  SEDU_Single_PCB_Parity_Corrected_RevC4a_Final.md   # SSOT — canonical spec
  DEVIATIONS_FROM_LEGACY.md                          # all parity changes, explicit
# Datasheets PDFs are stored at the repo root per AGENTS.md
/firmware
  /include/pins.h
  /src/main.ino
/scripts
  check_pinmap.py                                     # doc ↔ pins.h verifier (CI-safe)
/hardware
  SEDU_Board.kicad_pro (to be created)
```

---

## 7) Anti‑Drift Rules (what Codex must do)

- **Never** change `pins.h` without changing the canonical table in Rev C.4a — and vice‑versa.  
- After any change that touches pins/components:  
  1) Run: `python3 scripts/check_pinmap.py` → **must pass**.  
  2) Grep for banned strings: `rg -n "TLV757|VESC fallback|PPM|PWM header" -S` → **no hits**.  
  3) Grep USB: `rg -n "TLV75533|TPS22919" docs/ Component_Report.md` → **must be present** and consistent.  
  4) Ensure LCD lines explicitly say **GC9A01** and **MISO NC**; SPI CS for LCD is **GPIO16**.  
  5) Update the artifact index: add any new/renamed/removed files to `docs/DOCS_INDEX.md`, and run `python3 scripts/check_docs_index.py` to validate.  

- Any deviation from these rules must be called out in **both** the canonical doc and `DEVIATIONS_FROM_LEGACY.md`.

---

## 8) Verification Commands (run & report)

```
python3 scripts/check_pinmap.py
rg -n "TLV757|VESC fallback|PPM|PWM header" -S
rg -n "TLV75533|TPS22919" -S docs/ Component_Report.md
rg -n "GC9A01|MISO NC|CS_LCD|GPIO16" -S docs/ New\ Single\ Board\ Idea.md Component_Report.md
```

Codex should paste the outputs and say **PASS/FAIL** with a short fix plan if FAIL.

---

## 9) Typical Codex Tasks (paste‑ready prompts)

**A. Create KiCad skeleton**
```
Create 'hardware/SEDU_PCB.kicad_pro' with a blank board + schematic; add hierarchical sheets:
Power_In (LM5069, TVS, shunt), Bucks (LMR33630, TPS62133), USB_Prog (TPS22919→TLV75533),
MCU (ESP32‑S3 module, USB-C, ESD), Motor_Driver (DRV8353RS + FETs + shunts),
Actuator (DRV8873‑Q1), LCD_Connector (GC9A01 SPI, backlight), IO_UI (buttons, ladder, buzzer/LEDs).
Create net labels per the canonical pin names and export a netlist.
```
**Acceptance:** ERC must run clean (allowing unconnected LCD MISO), power symbols consistent.

**B. Export BOM CSV from component locks**
```
Generate docs/BOM.csv listing major ICs and key passives (values/tolerances), with columns: Ref, MPN, Qty, Notes, Substitutes. Base it on the Components — Locked Decisions section. Mark TLV75533/TPS22919 as USB-only.
```

**C. Firmware bootstrap**
```
Create firmware/include/pins.h and firmware/src/main.ino aligned to the pin table;
main.ino must: init USB CDC, read battery ADC with 2-point cal, classify ladder bands with fault latching,
debounce Start/Stop digital, read halls via PCNT (RPM estimate), stub actuator PH/EN control, and print status.
```

**D. CI pin map check**
```
Add a GitHub Actions workflow .github/workflows/pincheck.yml that runs 'python3 scripts/check_pinmap.py' on every push.
```

---

## 10) Editing Policy & Commit Messages

- **Never** edit the canonical pin table without mirroring the change in `pins.h` in the same commit.  
- Each commit affecting hardware must include: “**[pins sync]**” or “**[power path]**” or “**[lcd]**” tags.  
- Example:
  > `feat(pins sync): add CS_LCD=GPIO16; update pins.h; checker PASS`

---

## 11) Open Questions (if needed)

- If enclosure detunes the chip antenna, swap to **‑1U u.FL** and update the BOM + assembly notes.  
- If GPIO30/31 are constrained on your module variant, reassign **Actuator PH/EN** to free outputs and update SSOT + pins.h + checker in one commit.

---

## 12) Quick Sanity Recap (for Codex)

- **Battery** powers the tool; **USB** is programming‑only.  
- **No VESC fallback. No PPM/PWM legacy headers.**  
- **MCPWM on 38–43**; **CSAs on 5/6/7**; **Battery ADC 1**; **Ladder ADC 4**; **Start/Stop 23/24**; **LCD CS on 16**; **DRV CS on 22**.  
- Always run the **pin map checker** and show results when changing pins/docs.

---

*End of guide. Codex: follow this document as operational law for this repository.*
