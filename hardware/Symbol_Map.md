# Symbol & Footprint Map (Drop‑In Suggestions)

> Goal: let you place symbols fast with minimal searching. These use KiCad’s stock libraries where possible; for vendor‑specific ICs use a close placeholder symbol, then assign the recommended footprint. We’ll swap to exact vendor symbols right before ERC/DRC if desired.

## Power_In
- U6 (LM5069‑1)
  - Symbol: `Power_Management:HotSwap_Controller` (placeholder) or create local.
  - Footprint: `Package_SO:MSOP-10_3x3mm_P0.5mm` or `Package_DFN_QFN:WSON-10-1EP_3x3mm_P0.5mm` (check MPN).
- RS_IN (3.0 mΩ)
  - Symbol: `Device:R_Small`
  - Footprint: `Resistor_SMD:R_2512_6332Metric` (Kelvin style will be picked during layout if available).
- CDVDT (33 nF)
  - Symbol: `Device:C_Small`
  - Footprint: `Capacitor_SMD:C_0603_1608Metric`.
- TVS1 (SMBJ33A)
  - Symbol: `Device:D_Small` (placeholder)
  - Footprint: `Diode_SMD:D_SMB`.
- QREV (Reverse FET)
  - Symbol: `Device:Q_NMOS_DGS`
  - Footprint: `Package_TO_SOT_SMD:PowerPAK_SO-8_Single` or `Package_SO:SO-8_3.9x4.9mm_P1.27mm` (placeholder).

## Bucks
- U4 (LMR33630AF)
  - Symbol: `Regulator_Switching:LMR33630` (if absent, use `Regulator_Switching:StepDown_Generic`)
  - Footprint: `Package_DFN_QFN:VQFN-12-1EP_3x3mm_P0.5mm` (RNX) or SOIC variant if chosen.
- L4 (10 µH), C4x, C4IN
  - Symbols: `Device:L`, `Device:C`
  - Footprints: `Inductor_SMD:L_1008_2520Metric` (or chosen size), `Capacitor_SMD:C_0603_1608Metric` / `C_0805_2012Metric`.
- U5 (TPS62133)
  - Symbol: `Regulator_Switching:TPS62133` (or `StepDown_Generic`)
  - Footprint: `Package_DFN_QFN:QFN-16-1EP_3x3mm_P0.5mm`.
- L5, C5x
  - As above (choose sizes per availability).

## USB_Prog
- U7 (TPS22919)
  - Symbol: `Switch:Load_Switch` (placeholder)
  - Footprint: `Package_SON:WSON-6-1EP_1.5x1.5mm_P0.5mm`.
- U8 (TLV75533)
  - Symbol: `Regulator_Linear:TLV75533` (or `Regulator_Linear:Generic_LDO`)
  - Footprint: `Package_TO_SOT_SMD:SOT-23-5` (or WSON variant if stocked).
- ESD for USB
  - Symbol: `Device:D_TVS_x2_AAC` (or `ESD_Protection` placeholder)
  - Footprint: `Diode_SMD:SOT-23` or `SOT-323` per part.

- ## MCU
- U1 (ESP32‑S3‑WROOM‑1‑N16R8)
  - Symbol: `RF_Module:ESP32-S3-WROOM-1`
  - Footprint: `RF_Module:ESP32-S3-WROOM-1` (package is common across flash/PSRAM variants)
- ESDUSB
  - As above (USB_Prog ESD notes)

## Motor_Driver
- U2 (DRV8353RS)
  - Symbol: `Driver_Motor:GateDriver_3Phase` (placeholder)
  - Footprint: `Package_DFN_QFN:VQFN-48-1EP_7x7mm_P0.5mm_EP5.15x5.15mm` (correct per datasheet).
- Q1..Q6 (60 V MOSFETs)
  - Symbol: `Device:Q_NMOS_DGS`
  - Footprint: `Package_SO:PowerPAK_SO-8_Single` (or vendor SuperSO8).
- RS_U/RS_V/RS_W (2 mΩ 2512)
  - Symbol: `Device:R_Small`
  - Footprint: `Resistor_SMD:R_2512_6332Metric` (Kelvin later if available).
- Pump/decoupling caps
  - Symbol: `Device:C`
  - Footprint: `Capacitor_SMD:C_0603_1608Metric` (VCP/VGLS may be 0603/0805 depending on voltage).

## Actuator
- U3 (DRV8873‑Q1)
  - Symbol: `Driver_Motor:DRV887x` (if absent use `Driver_Motor:H-bridge`)
  - Footprint: `Package_SO:HTSSOP-28-1EP_9.7x4.4mm_P0.65mm_ThermalPad`.
- R_ILIM (1.58 kΩ), R_IPROPI (1.00 kΩ)
  - Symbol: `Device:R_Small`
  - Footprint: `Resistor_SMD:R_0603_1608Metric`.
- TVS2 (SMBJ33A)
  - As Power_In TVS.

## LCD_Connector
- J_LCD (8p)
  - Symbol: `Connector_Generic:Conn_01x08`
  - Footprint: `Connector_JST:JST_GH_BM08B-GHS-TBT_1x08-1MP_P1.25mm_Vertical`.
- R_SCK, R_MOSI (22–33 Ω)
  - `Device:R_Small` / `Resistor_SMD:R_0402_1005Metric` or `R_0603_1608Metric`.
- Q_LED (backlight sink)
  - `Device:Q_NMOS_GSD` / `Package_TO_SOT_SMD:SOT-23`.

## IO_UI
- J_UI (8p)
  - Symbol: `Connector_Generic:Conn_01x08`
  - Footprint: `Connector_JST:JST_GH_BM08B-GHS-TBT_1x08-1MP_P1.25mm_Vertical`.
- Ladder parts
  - Symbols: `Device:R_Small`, `Device:C_Small`
  - Footprints: `R_0603_1608Metric`, `C_0603_1608Metric`.

Footprint notes
- If a footprint isn’t present in your KiCad install, place the symbol and assign “no footprint” for now; we’ll swap from the seed BOM before routing.
