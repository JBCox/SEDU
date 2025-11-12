# SEDU Hardware — KiCad Scaffold Plan

This folder documents the exact KiCad structure to build. First spin omits 12 V actuator buck footprints to minimize size; the DRV8873 VM ties to protected 24 V by default.

## Project Layout (to create in KiCad)
- `SEDU_PCB.kicad_pro` — top‑level project
- `SEDU_PCB.kicad_sch` — top sheet with hierarchical blocks below
- `SEDU_PCB.kicad_pcb` — board file (75×55 mm target outline + 4× M3 holes)

## Hierarchical Sheets
- Power_In (LM5069‑1 + TVS + reverse FET)
- Bucks (LMR33630AF 24→5 V; TPS62133 5→3.3 V)
- USB_Prog (TPS22919 → TLV75533)
- MCU (ESP32‑S3‑WROOM‑1)
- Motor_Driver (DRV8353RS + 6× 60 V MOSFETs + 3× 2 mΩ shunts)
- Actuator (DRV8873‑Q1 + R_ILIM 1.58 kΩ + R_IPROPI 1.00 kΩ + IPROPI test pad; VM→24 V link)
- LCD_Connector (GC9A01 SPI; LEDK driver)
- IO_UI (button ladder, Start/Stop digital, buzzer/LEDs; J_UI connector)

See `hardware/SEDU_PCB_Sheet_Index.md` for per‑sheet details and refs.

## Nets & Pins
- Net labels must match `docs/SEDU_Single_PCB_Parity_Corrected_RevC4a_Final.md` table and `firmware/include/pins.h`.
- Canonical list in `hardware/Net_Labels.csv`.

## Connectors
- J_LCD (8): 3V3, GND, SCK, MOSI, CS_LCD, DC, RST, LEDK/PWM
- J_UI (8): 3V3, GND, BTN_SENSE, START_DIG, STOP_NC_DIG, BUZZER, LED1, LED2
  - Cable ≤200 mm; BTN_SENSE twisted with GND; 100–220 Ω series at J_UI; 100 nF at MCU ADC pin.

## Board Outline & Holes
- Board outline: **75×55 mm** (optimized from 80×60mm baseline; 14% area reduction)
- Optimization leverages 5V rail elimination (~12-15mm space savings in power section)
- Thermal analysis confirms adequate copper area (470mm²/W) for 8.5W dissipation
- Four M3 holes (3.2 mm finished) at positions: (4,4), (71,4), (4,51), (71,51) mm from corner
- Keep‑out annulus ≥1.5 mm around holes. Tented vias near holes.
- **Note**: Mounting holes NOT constrained by enclosure - tool designed around board

## ERC/DRC Expectations
- ERC should pass with LCD MISO unconnected (write‑only). Add PWR_FLAGs as needed.
- DRC pending layout; keep DRV8353 decoupling and gate loops tight; star ground at LM5069 sense.

## Routing Rules & Net Classes
- Copper weight: default 1 oz. If 2 oz is chosen, widths below may be halved.
- Net classes (see `hardware/SEDU_PCB.kicad_pcb` → rules):
  - `VBAT_HP`: clearance ≥0.50 mm; trace ≥4.00 mm; via dia ≥1.6 mm (drill ≥0.8 mm). Use pours on both layers and stitch with via grid ~1.0 mm.
  - `MOTOR_PHASE`: clearance ≥0.50 mm; trace ≥3.00 mm; via dia ≥1.2 mm (drill ≥0.6 mm). Symmetric pours to connector.
  - `ACTUATOR`: clearance ≥0.40 mm; trace ≥1.50 mm; via dia ≥1.0 mm (drill ≥0.5 mm).
  - `BUCK_SW_24V`: clearance ≥0.50 mm; trace ≥1.00 mm; SW island minimal, loop area small.
  - `SENSE_KELVIN`: clearance ≥0.20 mm; trace ≥0.25 mm; guard with GND; true Kelvin sense.
  - `USB_DIFF`: clearance ≥0.20 mm; trace ≥0.20 mm; place 22–33 Ω series at MCU; ESD at connector.

Assign nets:
- `VBAT_HP`: `VBAT`, `VBAT_PROT`.
- `MOTOR_PHASE`: label phase outputs `PHASE_U`, `PHASE_V`, `PHASE_W` at MOSFET bridge.
- `ACTUATOR`: label DRV8873 outputs `ACT_OUT_A`, `ACT_OUT_B`.
- `BUCK_SW_24V`: label LMR33630 switch node `SW_24V`.
- `SENSE_KELVIN`: `CSA_U_ADC`, `CSA_V_ADC`, `CSA_W_ADC`, `BAT_ADC`, `BTN_SENSE`, `IPROPI_ADC`, `NTC_ADC`.
- `USB_DIFF`: `USB_D+`, `USB_D-`.

Planes, pours, and keep‑outs:
- Separate `PGND` and `LGND` pours; join at a single star near the LM5069 sense return.
- Keep SW islands away from ADC traces; guard ADC nets with ground copper and vias.
- Keep `BTN_SENSE` ≥10 mm from SW and phase pours; populate 100–220 Ω series + 0.1 µF at the MCU pin.
- Respect antenna keep‑outs if the u.FL module variant is used in the future.

## Antenna Keep-Out (ESP32‑S3‑WROOM‑1)
- For the chip-antenna module: define a no-copper keep‑out on both layers extending ≥15 mm in front of the antenna end and ≥5 mm margin around the antenna edge of the module.
- Do not place ground pour, traces, or tall components in this region.
- If using the u.FL variant in the future, keep RF trace impedance-controlled and maintain a ground reference; still avoid large copper under the antenna area.

## Pre‑release DFM & High‑Power Safety Checklist
- Star ground: exactly one tie between `PGND` and `LGND` near LM5069 sense; verify plane separation.
- Shunt Kelvin: sense traces do not share power current path; short and symmetric to DRV8353/ADC RC.
- Buck SW: minimal copper on SW nodes, oriented away from ADC traces; tight VIN/COUT loops.
- Phases: symmetric pours; short, equal gate traces; gate resistors at FET gates.
- BTN_SENSE: guarded route; series 100–220 Ω + 0.1 µF populated; ≥10 mm from high‑di/dt pours.
- ESD/series resistors: USB ESD at connector; 22–33 Ω series at MCU D+/D−.
- TVS: SMBJ33A at battery and actuator connectors with shortest GND return path.
- Test pads: 3V3/24V/RX/TX/`BTN_SENSE`/`IPROPI` reachable with probe clips. **(5V test pad removed - rail eliminated)**
- Thermals: vias under hot parts (inductors, driver, MOSFETs as applicable) with fab‑compatible constraints.
 - Silkscreen: Pin‑1 indicators clearly marked on J_LCD and J_UI; verify orientation against connector drawings.

## Thermal Via Guidance
- For heat-spreading pads (MOSFET drains, buck IC exposed pads, inductors):
  - Use via arrays 3×3 to 4×4, pitch ≈ 1.0 mm.
  - Finished hole Ø ≈ 0.30 mm (drill 0.20–0.25 mm) where the fab allows; tent or fill as per capability to avoid solder wicking.
  - Connect to internal/bottom copper to spread heat into planes; avoid stitching into sensitive analog areas.
- For SuperSO8 MOSFETs without via-in-pad, consider “dogbone” pads to nearby via arrays.

## Gate Drive Guidance (DRV8353RS + MOSFETs)
- Gate resistors: start with 5–10 Ω per FET; place each resistor as close as possible to its MOSFET gate pin.
- Keep HS/LS gate traces short and matched within ±2 mm to minimize skew; avoid loops and stubs.
- Route gate return currents tightly with their source references; avoid crossing sensitive analog.
- Place DRV8353RS close to the bridge; place VGLS/VCP/DVDD decoupling at pins with direct vias.

## Placement Zones (75×55 mm optimized outline)
- Power Entry + Star: Place LM5069, TVS, reverse FET, and battery connector along one short edge. The PGND↔LGND NetTie_2 star sits immediately downstream of the sense resistor. Keep VBAT/VBAT_PROT pours wide with via stitching.
- Buck (24→3.3V): Next to power entry, with SW island oriented inward (away from MCU/ADC). Provide local copper for thermal spread. **8× thermal vias (Ø0.3mm) under LMR33630 PowerPAD mandatory.**
- Bridge + Shunts: Place DRV8353RS + MOSFETs + shunts together on the side opposite the MCU/antenna. Keep gate resistors at gates; true Kelvin from shunts; phase pours to motor connector.
- MCU + LCD/UI: Opposite phases/SW nodes; enforce antenna keep‑out (≥15 mm forward, ≥5 mm perimeter). Route BTN_SENSE/IPROPI/CSA far from SW/phase pours; guard with GND and stitch vias.
- Connectors: J_UI and J_LCD away from motor/actuator connectors; ESD arrays at connectors; series resistors near pins.

### Initial Placement Checklist (Day‑One)
- Place LM5069 + battery connector + star (NetTie_2) along one edge; verify star location.
- Place LMR33630 with SW island facing away from MCU; add copper for thermals. **(TPS62133 removed - 5V rail eliminated)**
- Place DRV8353RS, MOSFETs, shunts as a cluster; gate resistors at FET gates; plan phase pours.
- Respect antenna keep‑out; position MCU/LCD/UI far from SW/phase; guard ADC nets with GND + vias.
- Place J_UI/J_LCD away from motor/actuator connectors; put ESD/series parts at connector side.
- Drop TP_* pads (3V3/24V/BTN/IPROPI/RX/TX) and check probe access. **(5V removed)**

## How to Resume
1) Open KiCad and create `SEDU_PCB.kicad_pro` in this folder.
2) Add the hierarchical sheets per this README (use the same names).
3) Name nets according to `hardware/Net_Labels.csv`.
4) Place mounting holes and set the board outline per `hardware/Mounting_And_Envelope.md`.
5) Run ERC and record notes in `docs/BRINGUP_CHECKLIST.md`.
