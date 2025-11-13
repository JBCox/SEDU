# SEDU Single-PCB Feed Drill Controller — Rev C.4a Canonical Spec

**Scope:** Single printed circuit board that replaces the legacy VESC + ESP32-C6 dev board + DRV8871 harness while preserving identical operator states, safety interlocks, and UI behavior for the aerospace positive-feed drill. Board size: **80 × 50 mm** (optimized from 80×60mm baseline via 75×55mm intermediate; 17% area reduction), fits within credit card footprint.

## 1. Locked Decisions (do not drift)
- **Power during operation:** 6S (18–25.2 V) battery only. USB is programming-only and never allowed to power the drill hardware while in use.
- **Programming rail:** USB-C VBUS → TPS22919 load switch → TLV75533 3.3 V LDO. Radios are forced off whenever the board is USB-powered.
- **Actuator driver:** DRV8873-Q1 (PH/EN). Legacy DRV8871 is retired; note this deviation wherever BOMs or schematics are published.
- **Motor stage:** Integrated DRV8353RS + external MOSFETs + 2 mΩ phase shunts; no external VESC fallback.
- **MCU:** ESP32-S3-WROOM-1-N16R8 (chip antenna) with optional -1U stuffing for u.FL.
- **GPIO map:** See §4 table; MCPWM on GPIO38–43, CSA ADC inputs on GPIO5/6/7, battery ADC on GPIO1, button ladder on GPIO4.
- **UI parity:** Start/Stop ladder behavior and discrete Start/Stop lines must mirror the original drill (Start drives both motor + actuator; Stop forces immediate halt). LCD must continue showing battery %, motor RPM/current, and state text.
- **Display:** GC9A01 240×240 SPI panel, 3.3 V logic, LEDK backlight 10–20 mA; write-only SPI (MISO NC).

## 2. Power Architecture
| Stage | Part(s) | Vin → Vout | Notes |
|---|---|---|---|
| Input protection | LM5069-1 (latch-off) + TVS SMBJ33A + reverse FET | Battery → protected bus | Hot-swap, OV/UV, programmable ILIM (≈18 A using 3.0 mΩ sense). dv/dt cap sized so inrush ≤0.5·ILIM. UV turn‑on ≈ 19.0 V (RUV 140k/10k), OV trip ≈ 29.2 V (ROV 221k/10k). |
| Logic buck | LMR33630ADDAR | 24 V → 3.3 V | **Single-stage** 400 kHz synchronous buck, 3A capable. Feeds ESP32, LCD, logic. **5V rail eliminated** for simpler design (1 IC vs 2). DRV8353 DVDD (5V) is internally generated. Tie LGND to star point near LM5069 sense. |
| USB-only rail | TPS22919 → TLV75533 | 5 V USB → 3.3 V | Only for flashing/debug. Back-feed protection handled by load switch. Radios disabled via firmware when USB rail is active. **Note: Isolated from main 3.3V rail.** |
| Actuator rail | DRV8873-Q1 VM pin | 24 V direct | DRV8873 powered directly from protected 24V (VM pin supports 4.5-38V). No separate buck needed. |

### Power Value Locks (Rev C.4b)
- LM5069 variant: **LM5069-1 (latch‑off / latch-off)** is the default for safer fault handling. Use Rsense ≈ 55 mV / ILIM. Updated for motor peak loads: ILIM ≈ 18 A → Rsense ≈ 3.0 mΩ → stuff **3.0 mΩ**, **≥3 W**, **1%**, **4‑terminal Kelvin** (e.g., HoLRS2512-3W-3mR-1%). Circuit breaker ≈ 105 mV / Rsense (≈35 A). Start with **C_dv/dt = 33 nF** and adjust so measured inrush ≤ ~0.5·ILIM.
- LMR33630ADDAR (24→3.3 V @ 400 kHz **single-stage**): L = 10-22 µH (start with 10µH for prototype, consider 15-22µH for better efficiency); COUT ≈ 4 × 22 µF X7R (≥10 V); CIN ≥ 10 µF + 220 nF HF; BOOT = 100 nF; VCC = 1 µF; provide copper/vias (P_loss ≈ 1.35 W @ 3.3 V/3 A, η≈88%). **5V rail eliminated** - simpler design (1 IC vs 2), fewer components.
- Policy lock: "TPS22919 → TLV75533 only; USB never powers the tool; radios forced off in USB‑only mode."

## 3. Safety & Legacy Parity Requirements
- Maintain the original state machine (Idle → Arm → Run → Retract → Complete, plus Fault). Loss of Start/Stop ladder integrity, UART dropouts, or power anomalies must immediately de-energize motor and actuator.
- Keep common star ground at battery negative; route high-di/dt motor and actuator returns directly there before joining logic.
- Highlight all deviations from the legacy harness (e.g., DRV8873-Q1, discrete Start/Stop GPIOs, integrated motor stage) in schematic notes, BOM, and `docs/DEVIATIONS_FROM_LEGACY.md`.
- LCD must always display battery percentage (derived from the battery ADC divider) and motor telemetry (RPM/current) pulled from the DRV8353RS/firmware stack.

## 4. Canonical GPIO / Signal Map
| Function | ESP32-S3 Pin | Notes |
|---|---|---|
| USB D− / D+ | GPIO19 / GPIO20 | Include 22–33 Ω series resistors and ESD near connector. |
| MCPWM HS U/V/W | GPIO38 / GPIO39 / GPIO40 | IO35–37 unavailable (PSRAM). Driver EN held low at boot. |
| MCPWM LS U/V/W | GPIO41 / GPIO42 / GPIO43 | Same PWM unit; ensure spread-spectrum timing tolerance. |
| DRV8353 SPI | SCK=GPIO18, MOSI=GPIO17, MISO=GPIO21, CS=GPIO22 | Shared bus; LCD uses a separate CS. Keep GPIO‑JTAG disabled so MCPWM owns 38–43. |
| CSA ADCs | GPIO5 (ADC1_CH4), GPIO6 (ADC1_CH5), GPIO7 (ADC1_CH6) | 56–100 Ω + 470 pF RC at MCU pins. |
| Battery ADC | GPIO1 (ADC1_CH0) | Divider locked to 140 kΩ / 10.0 kΩ (1%). At 25.2 V → 1.68 V at ADC, 18.0 V → 1.20 V (no atten or 11 dB). Add 1 kΩ series + 0.1 µF to GND at pin; 2‑point cal in NVS. |
| Button ladder ADC | GPIO4 (ADC1_CH3) | Ladder voltage bands: <0.20 V fault, 0.75–1.00 V START, 1.55–2.10 V IDLE, 2.60–3.35 V STOP, >3.40 V fault. |
| LCD (GC9A01 SPI) | SCK=GPIO18, MOSI=GPIO17, CS_LCD=GPIO16 (MISO NC) | Write-only; dedicated CS avoids contention. DC/RST per connector; LEDK sink 10–20 mA. |
| Start / Stop digital | GPIO23 / GPIO24 | Mirror ladder result; both must agree before enabling motion. |
| Halls A/B/C | GPIO8 / GPIO9 / GPIO13 (PCNT) | For 6-step commutation and diagnostics. |
| FEED_SENSE | GPIO14 | Limit/Hall for actuator travel; RC-deglitch. |
| Buzzer / LEDs | GPIO25 (BUZ), GPIO26/27/28 (LEDs) | Optional UI cues. |
| Spare test pads | GPIO11, GPIO12 | Leave unconnected by default; permit debug. |

| Actuator DRV8873 PH/EN | GPIO30 / GPIO31 | EN default low at boot. |
| Actuator IPROPI ADC | GPIO2 (ADC1_CH1) | Read current mirror; route to test pad.

## 5. Actuator & Button Interface
- DRV8873-Q1 PH/EN version powered from protected 24 V bus; ILIM resistor set to 110–120% of actuator continuous rating. Include SMBJ33A clamp on the actuator supply.
- ESP32 GPIO23 (START) drives DRV8873 enable path; GPIO24 (STOP_NC) provides redundant hardware disable or gate for firmware logic.
- Two-button ladder values: R19=10 kΩ pull-up, R20=100 kΩ auxiliary pull-up, Start leg R21=5.1 kΩ to GND (NO), Stop leg R11=10 kΩ to GND (NC), C19=100 nF to GND. Firmware treats unspecified voltages (1.00–1.55 V and 2.10–2.60 V) as hard faults; <0.20 V is fault-low and >3.40 V is fault-open.

### DRV8873‑Q1 Current Feedback (Rev C.4b)
- Use IPROPI mirror or ITRIP levels. Size R_IPROPI so V_IPROPI ≤ 3.3 V across expected current (k≈1100 A/A). Example: 3 A ⇒ R_IPROPI ≤ ~1.21 kΩ; conservative 910 Ω–1.0 kΩ gives ~2.7–3.0 V at 3 A.
**Locks for 24 V default build:**
- R_IPROPI = **1.00 kΩ (1%)** → V_IPROPI ≈ (I_A × R)/1100 ≈ 2.7 V @ 3.0 A and ≈ 3.0 V @ 3.3 A (ADC_11db FS ≈ 3.5–3.6 V margin).
- ILIM set by R_ILIM ≈ 5200 / I_lim(A). Choose **R_ILIM = 1.58 kΩ (E96, 1%)** ⇒ I_lim ≈ **3.3 A**.

### Actuator Supply Options (24 V default; 12 V optional)
- Default assembly: **24 V actuator**. DRV8873 VM is tied directly to `VBAT_PROT` (protected 24 V) via a 0 Ω link. **First spin omits 12 V buck footprints** to minimize area.
- Optional 12 V assembly (future spin): populate a dedicated 12 V buck (`VACT_12V`) when using a 12 V actuator. In this case, tie DRV8873 VM to `VACT_12V` via a DNI/0 Ω link.
- If 12 V option populated: size the 12 V buck for ≥2.5 A peak; start with LMR33630AF set to 12 V (L≈10–15 µH, COUT≥2×22 µF X7R ≥16 V). Verify thermals during bring‑up.

## 6. Display & Telemetry
- GC9A01 240×240 IPS, SPI write-only. Pinout: VCC=3.3 V, GND, SCK (GPIO18), MOSI (GPIO17), **CS_LCD (GPIO16)**, DC, RST, LEDK. LEDK backlight sink 10–20 mA through transistor or MCU-controlled FET if dimming needed.
- Add 22–33 Ω series resistors on SCK/MOSI at the MCU when the LCD is cabled; route far from phase nodes. Document connector family and pin numbering in schematic notes.
- Minimum telemetry set: Ready/Run/Fault text, battery percentage (from GPIO1 ADC), motor RPM/current (firmware derived from DRV8353 telemetry or Halls).

## 6.1 UI Daughterboard (Buttons + LCD Carrier)
- The LCD and physical buttons are mounted on a small daughterboard connected by cables to the main PCB.
- Provide two connectors on the main board:
  - `J_LCD` (8 pos): 3V3, GND, SCK, MOSI, CS_LCD, DC, RST, LEDK/PWM. Place 22–33 Ω series on SCK/MOSI at the MCU; optional 47 pF to GND near panel for EMI if cable >150 mm.
  - `J_UI` (8 pos): 3V3, GND, BTN_SENSE (ladder analog), START_DIG, STOP_NC_DIG, BUZZER, LED1, LED2. Keep BTN_SENSE twisted with GND; add 100 nF to GND at the main board ADC pin and 100–220 Ω series at the connector.
- Cable guidance: keep each cable ≤200 mm; use JST‑GH/PH or equivalent locking connectors. Route away from motor phase nodes. Add ESD arrays on lines that exit the enclosure (USB, BTN_SENSE, START/STOP, SPI if exposed).

## 7. Mechanical Envelope & Mounting
- Board size target: **80 × 50 mm** (optimized from 80×60mm baseline via 75×55mm intermediate; 17% area reduction, fits within credit card footprint 85.6×54mm).
- Layers: **4‑layer** recommended (L1 signals + short pours; L2 solid GND; L3 3V3 plane and sense stitching **(5V plane removed)**; L4 signals/returns).
- Mounting: **4× M3** holes (3.2 mm finished) with ≥1.5 mm keep‑out annulus; nominal centers at (4,4), (76,4), (4,46), (76,46). Tented vias near holes.
- Keep‑outs: ESP32 antenna per datasheet; LCD and UI connectors away from high di/dt phase regions; star ground at battery‑negative shunt.

## 7. Programming & Debug
- Default programming via USB-C CDC bootloader. If USB is removed, expose a Tag-Connect SWD/JTAG header tied to EN/BOOT/USB pins per Espressif design guide.
- When powered by USB-only rail, firmware disables motor/actuator outputs, RF subsystems, and indicates “USB DEV MODE” on LCD.
- Maintain test pads for 3V3, 24V, RX, TX, BTN_SENSE, IPROPI. **(5V test pad removed - rail eliminated)**

## 8. Bring-Up Checklist (Summary)
1. Unpowered: continuity, correct orientation, verify star ground nodes.
2. 24 V applied, drivers held in reset: confirm LM5069 inrush profile, buck rails, no unexpected heating.
3. Logic validation: USB enumeration, ladder readings, LCD splash, Hall edge capture.
4. Motor: DRV8353 SPI communication, PWM outputs, incremental current tests, over-current trip exercise.
5. Actuator: ILIM validation, FEED_SENSE transitions, Start/Stop redundancy tests.
   - 24 V default build: start with R_IPROPI=1.0 kΩ; set ILIM≈3.0–3.6 A; confirm steady current and thermal margin.
   - 12 V optional build: verify `VACT_12V` ripple and peak current during extend; start with R_IPROPI=1.0 kΩ and ILIM≈3.0–3.3 A.
6. EMI/ESD: surge tests on battery input, radiated pre-scan; verify antenna keep-out effectiveness.

## 9. Motor Stage Implementation Notes (Rev C.4b)
- MOSFET voltage rating: 60 V only (6S + transients). Replace any 40 V examples with 60 V SuperSO8 (e.g., Infineon BSC016N06NS / BSC059N06LS3 G, onsemi NTMFS5C628NL, Vishay SQJQ480E) or automotive 60 V in DPAK/TO‑220.
- DRV8353RS decoupling: CPL‑CPH = 47 nF (≥100 V X7R); VCP‑VDRAIN = 1 µF (≥16 V); VGLS‑GND = 1 µF (≥16–25 V); DVDD = 1 µF (≥6.3 V). Place tight to pins.
- Gate drive: target 100–300 ns rise; start mid‑IDRIVE, add gate resistors so t_rise ≈ Qgd·R_total/11 V; tune on bench, add snubbers if ringing.

This document is the canonical reference for Rev C.4a/C.4b. Update subordinate docs, firmware, and CAD directly from these values to avoid drift.
