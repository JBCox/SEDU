# Schematic Wiring Guide (Nets, Refs, and Connections)

This guide lists exactly how to wire each sheet using the canonical net names in `hardware/Net_Labels.csv`. Use it to place symbols and connect nets quickly in KiCad.

## Conventions
- Nets appear in backticks and must match `hardware/Net_Labels.csv`.
- Place PWR_FLAGs on `VBAT_PROT`, `5V`, and `3V3` as needed (see `hardware/ERC_Notes.md`).
- DNP = Do Not Populate on first spin.

---

## Power_In (LM5069-1, TVS, reverse FET)
Refs: U6=LM5069-1, RS_IN (3.0 mΩ), TVS1=SMBJ33A, QREV (optional)

- Battery input and clamp
  - `VBAT` → TVS1 anode; TVS1 cathode → `GND`.
  - `VBAT` → RS_IN high (Kelvin `RS_IN+`); RS_IN low (Kelvin `RS_IN-`) → LM5069 `SENSE` pin and path to reverse FET/series pass FET source.
- Controller pins
  - LM5069 `VIN` → `VBAT`.
  - LM5069 `SENSE` → Kelvin sense across RS_IN (to `RS_IN-`).
  - LM5069 `GATE` → pass FET gate (internal to reverse+series FET block).
  - LM5069 `TIMER` → start with **33 nF** to allow brief inrush; adjust after measuring inrush ≤ ~0.5×ILIM.
  - LM5069 `CAP`/dvdt pin → CDVDT 33 nF to `GND`.
  - UV/OV divider (locked targets for 6S battery):
    - UV turn‑on ≈ 19.0 V: use RUV_TOP = 140 kΩ, RUV_BOT = 10.0 kΩ (1%).
    - OV trip ≈ 29.2 V: use ROV_TOP = 221 kΩ, ROV_BOT = 10.0 kΩ (1%).
    - Tie each divider top to `VBAT`, bottom to `GND`, midpoint to UV / OV pins respectively.
- Reverse/series FET block
  - Source towards battery, drain towards protected bus (or use ideal‑diode config per datasheet). Output node labeled `VBAT_PROT`.
- Outputs
  - `VBAT_PROT` → feeds Bucks, DRV8353 power, DRV8873 VM (24 V default).
  - Star ground: join high‑current returns at shunt’s `GND` side; keep logic grounds tied at star.

---

## Bucks (LMR33630AF 24→5 V, TPS62133 5→3.3 V)
Refs: U4=LMR33630AF, L4=10 µH, C4x=22 µF×4, C4IN=10 µF + 220 nF; U5=TPS62133, L5=2.2 µH, C5x=22 µF×2

- LMR33630 (24→5 V)
  - VIN → `VBAT_PROT` via short trace; CIN: 10 µF to `GND` + 220 nF to `GND` near VIN.
  - VOUT → net `5V`; COUT: 4×22 µF from `5V` to `GND` near IC/inductor.
  - SW → one end of L4; other end of L4 → `5V`.
  - BOOT 100 nF (internal note; if exposed) between BOOT and SW.
  - VCC 1 µF to `GND` (per datasheet). Tie AGND/PGND appropriately; return to star.
- TPS62133 (5→3.3 V)
  - VIN → `5V` via short trace; CIN: ~10 µF to `GND` near VIN.
  - VOUT → `3V3`; COUT: 2×22 µF to `GND` near IC/inductor.
  - SW → one end of L5; other end of L5 → `3V3`.
  - PG/MODE per default (optional pull‑ups/downs); route AGND to star.

---

## USB_Prog (TPS22919 → TLV75533)
Refs: U7=TPS22919, U8=TLV75533, ESDUSB

- USB D± from connector → ESD → series 22–33 Ω → MCU `kUsbDm/kUsbDp` nets.
- VBUS → TPS22919 IN; TPS22919 OUT → TLV75533 IN.
- TLV75533 OUT → `3V3` (USB dev rail). Ensure firmware disables radios when on USB‑only.
- No backfeed to `5V` or `VBAT_PROT`.

---

## MCU (ESP32‑S3‑WROOM‑1)
Refs: U1=ESP32‑S3‑WROOM‑1, ESDUSB

- USB: `USB_D-` → GPIO19; `USB_D+` → GPIO20.
- SPI to DRV/LCD: `SPI_SCK`=GPIO18, `SPI_MOSI`=GPIO17, `SPI_MISO`=GPIO21, `SPI_CS_DRV`=GPIO22, `SPI_CS_LCD`=GPIO16; LCD MISO NC.
- PWM: MCPWM HS U/V/W → GPIO38/39/40; LS U/V/W → GPIO41/42/43.
- ADCs: `CSA_U_ADC`=GPIO5, `CSA_V_ADC`=GPIO6, `CSA_W_ADC`=GPIO7; `BAT_ADC`=GPIO1; `BTN_SENSE`=GPIO4; `NTC_ADC`=GPIO10; `IPROPI_ADC`=GPIO2.
- Digital IO: `START_DIG`=GPIO23; `STOP_NC_DIG`=GPIO24; `FEED_SENSE`=GPIO14; `BUZZER`/`LED1`/`LED2`/`LED3`=GPIO25/26/27/28.

---

## Motor_Driver (DRV8353RS + MOSFET bridge)
Refs: U2=DRV8353RS, Q1..Q6=60 V MOSFETs, RS_U/RS_V/RS_W=2 mΩ shunts

- SPI: `SPI_SCK`/`SPI_MOSI`/`SPI_MISO`/`SPI_CS_DRV` to DRV8353 pins.
- PWM inputs: map GPIO38..43 to UH/UL/VH/VL/WH/WL.
- Power: DRV8353 VM → `VBAT_PROT`; decoupling close to pins (CPL‑CPH 47 nF; VCP/VGLS/DVDD 1 µF).
- Current shunts: each phase low‑side shunt to `GND`; CSA outputs to corresponding ADC nets with 56–100 Ω + 470 pF at MCU.

---

## Actuator (DRV8873‑Q1)
Refs: U3=DRV8873‑Q1, R_ILIM=1.58 kΩ, R_IPROPI=1.00 kΩ, TVS2=SMBJ33A

- Power: VM → `VBAT_PROT` (24 V default). TVS2 from VM to `GND` near connector.
- Control: PH → GPIO30; EN → GPIO31 (use nets `kActuatorPh/kActuatorEn`).
- Outputs: OUT1/OUT2 to actuator connector `J_ACT`.
- Current: IPROPI → `IPROPI_ADC` (GPIO2) and test pad.
- Limits: R_ILIM to set ≈3.3 A; R_IPROPI = 1.00 kΩ for ADC scaling.

---

## LCD_Connector (GC9A01)
Refs: J_LCD, R_SCK, R_MOSI, Q_LED

- SPI: `SPI_SCK`, `SPI_MOSI`, `SPI_CS_LCD`; `LCD_DC`, `LCD_RST` as dedicated nets; MISO NC.
- Backlight: `LEDK_PWM` sinks 10–20 mA via Q_LED or series resistor.
- Series resistors: R_SCK, R_MOSI (22–33 Ω) at MCU side.

---

## IO_UI (buttons + buzzer/LEDs)
Refs: J_UI, R19=10k, R20=100k, R21=5k, R11=10k, C19=100 nF, R_BTN_SER=100–220 Ω

- Ladder: R19 (10k) to `3V3`; R20 (100k) to `3V3`; R21 (5k) to `GND` via Start NO; R11 (10k) to `GND` via Stop NC; node → R_BTN_SER (100–220 Ω) → `BTN_SENSE`; C19 100 nF from `BTN_SENSE` (at MCU side) to `GND`.
- Redundant lines: `START_DIG`, `STOP_NC_DIG` to J_UI; `BUZZER`, `LED1`, `LED2` as needed.

---

## Connectors (power + devices)
- Battery: `J_BAT` → `VBAT` and `GND`.
- Motor: phase connectors from FET bridge; grounds return to star.
- Actuator: `J_ACT` → DRV8873 OUT1/OUT2 and `GND`.
- UI/LCD: `J_UI`, `J_LCD` per `hardware/Connectors_J_LCD_J_UI.md`.

---

Validation checklist after wiring
- ERC passes with expected No‑ERC on LCD MISO; PWR_FLAGs placed; no unconnected power pins.
- Nets match `hardware/Net_Labels.csv`.
- Run `python3 scripts/check_docs_index.py` and update `docs/SESSION_STATUS.md` with ERC results.
