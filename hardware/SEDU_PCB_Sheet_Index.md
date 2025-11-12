# SEDU_PCB Sheet Index (First Spin, 24 V Actuator Default)

- Power_In
  - LM5069-1 hot-swap; RSENSE 3.0 mΩ (≥3 W, 4-terminal), CdV/dt = 33 nF start, TVS SMBJ33A, reverse FET.
  - UV turn-on ≈ 19.0 V (RUV 140k/10k); OV trip ≈ 29.2–29.6 V (ROV 221k/10k); star ground near shunt.
  - Star join: explicit NetTie_2 to join PGND↔LGND at the Mecca star near sense resistor.
- Bucks
  - LMR33630ADDAR 24→3.3 V @ 400 kHz (single-stage); L = 10-22 µH; COUT = 4×22 µF X7R (≥10 V); CIN ≥10 µF + 220 nF. **(5V rail eliminated for simpler design)**
- USB_Prog
  - TPS22919 → TLV75533; USB-only 3.3 V; radios OFF; never powers tool; ESD + 22–33 Ω on D±.
  - Type‑C UFP: CC1/CC2 pulldowns (R_CC1 = R_CC2 = 5.1 kΩ to GND).
  - Optional ESD on CC pins (DNI): 2‑line TVS array placed next to CC1/CC2.
- MCU
  - ESP32-S3-WROOM-1-N16R8; pins per SSOT; keep GPIO-JTAG disabled; add test pads for 3V3/24V/RX/TX/BTN_SENSE/IPROPI.
  - ADC anti-alias: series + shunt RCs at GPIO1/2/5/6/7 per README (CSA, BAT, IPROPI).
- Motor_Driver
  - DRV8353RS + 6× 60 V MOSFETs; 3× 2 mΩ 2512 Kelvin shunts; decoupling: CPL-CPH 47 nF; VCP, VGLS, DVDD 1 µF.
  - Optional RC snubbers (DNI): per phase to PGND; R=10 Ω (0603) in series with C=1–4.7 nF (0603), placed close to bridge.
  - See hardware/README.md “Gate Drive Guidance” for gate R values/placement and ±2 mm matching.
- Actuator
  - DRV8873-Q1 PH/EN; VM tied to protected 24 V; R_ILIM = 1.58 kΩ; R_IPROPI = 1.00 kΩ; IPROPI → ADC1_CH1 (GPIO2) + test pad.
- LCD_Connector
  - GC9A01 SPI; SCK=GPIO18; MOSI=GPIO17; CS_LCD=GPIO16; MISO NC; DC/RST pins; LEDK sink 10–20 mA via FET or resistor.
  - Optional LEDK ferrite bead (DNI) near J_LCD for EMI if needed during bring‑up.
- IO_UI
  - Button ladder: R19=10 k, R20=100 k, R21=5 k (Start NO), R11=10 k (Stop NC), C19=100 nF; BTN_SENSE RC at MCU (1–4.7 k + 0.1 µF).
  - START_DIG=GPIO23; STOP_NC_DIG=GPIO24; buzzer/LEDs per SSOT.
  - ESD: 4‑line TVS array (ESD_UI) placed next to J_UI with short ground return.
  - Series resistors: 100 Ω at START_DIG and STOP_NC_DIG near J_UI (limit ESD surge/edge rates).

Refer to `docs/SEDU_Single_PCB_Parity_Corrected_RevC4a_Final.md` for the canonical pin table and connector pinouts.
