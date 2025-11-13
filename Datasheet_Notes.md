# SEDU Single-PCB Feed Drill — Component Datasheet Notes

> Quick-reference notes distilled from the corresponding TI/ESP datasheets for the parts selected in Rev C.4a. Values focus on the operating region relevant to our 24 V aviation tool. Always verify against the latest datasheet revision before release.

## ESP32-S3-WROOM-1-N16R8 (Espressif)
- **MCU**: Dual-core Xtensa® LX7 @ up to 240 MHz, 512 KB SRAM on-chip plus integrated 16 MB Quad-SPI flash and 8 MB Octal-SPI PSRAM.
- **Supply**: 3.0–3.6 V (nominal 3.3 V). Typical current ~240 mA peak with Wi‑Fi TX @ 20 dBm.
- **Peripherals used**: Native USB OTG (GPIO19=D−, GPIO20=D+), MCPWM with six outputs (GPIO38‑43 usable on PSRAM modules), SPI, I²C, ADC1/ADC2, PCNT for Hall sensors.
- **RF**: Integrated PCB antenna; -1U variant offers u.FL. Keep 15 mm keep-out, no copper pour under antenna tip.
- **Boot straps**: GPIO0, GPIO3, GPIO45, GPIO46; ensure pull-ups/downs respect Espressif table when assigning peripherals.

## DRV8353RS (Texas Instruments)
- **Function**: 100 V smart gate driver for three-phase BLDC with integrated current-shunt amplifiers (CSAs).
- **Supply rails**: VM 6–100 V, DVDD 3.3 V (regulator provides 5 mA). Logic inputs accept 3.3 V levels.
- **Gate drive**: Up to 1.2 A source/2.3 A sink typical, adjustable with SPI (IDRIVE). Supports smart gate-drive options, configurable VGS clamp.
- **CSAs**: Three fully differential amplifiers with gain programmable (5/10/20/40 V/V); 0–3.3 V output range, input CM up to 3 V.
- **Protections**: Adjustable OCP (cycle-by-cycle or latched), VDS monitoring, UVLO, OT warning/shutdown, SPI fault reporting.
- **Project setting**: Gain locked to 20 V/V for 2 mΩ shunts giving ≈±25 A full-scale into ~2.0–2.5 V at ADC1_CH4/5/6.

## DRV8873-Q1 (Texas Instruments)
- **Function**: Automotive brushed DC H-bridge with integrated FETs and SPI/PWM variants; PH/EN version chosen.
- **Supply**: 4.5–37 V (absolute max 40 V). Handles 3.5 A continuous, 6.5 A peak with adequate thermal design. VM may be tied to 12 V (via dedicated buck) or 24 V depending on actuator variant.
- **Current regulation**: External resistor on ILIM pin sets peak current limit (I_lim ≈ 5200 V / R_ILIM per datasheet). Mirror output (IPROPI) provides analog current proportional to motor current for MCU monitoring if needed.
- **Control**: PH input selects direction; EN input enables PWM/slow decay control. nFAULT pin asserts low on thermal/UV/OC events.
- **Protections**: UVLO, OCP, OVP, OT, open-load detection, watchdog for stuck inputs.

## LM5069MM-1/NOPB (Texas Instruments)
- **Function**: 9–80 V hot-swap / eFuse controller driving an external N-channel FET for inrush limiting and fault disconnect.
- **Key pins**: UV/OV comparator (program window), TIMER for fault retry (type -1 automatically retries), GATE controls external MOSFET, SENSE monitors current via shunt (ILIM = 50 mV / R_SENSE typ).
- **dv/dt control**: CAP pin programs gate slew to limit inrush charging of downstream bulk caps; pick C_DV/DT to keep inrush < ~0.5×ILIM.
- **Protections**: Fast short-circuit trip (~250 ns), power limiting, thermal shutdown, load-dump tolerance with appropriate FET.
- **Project target**: ILIM ≈18 A using 3.0 mΩ 4-terminal shunt; TIMER sized to tolerate BLDC spin-up pulse while tripping on sustained overload.

## LMR33630AF (Texas Instruments)
- **Function**: Synchronous buck converter, 3.8–36 V input, 3 A output.
- **Switching**: ~400 kHz (A version). Internal high/low‑side FETs lower BOM count.
- **Efficiency**: >90 % at 24 V→5 V/2 A with proper layout (short loop between VIN, SW, catch diode plane).
- **Design notes**: Start with **8 µH** inductor (≥4 A RMS) for 5 V; **10–15 µH** for a 12 V rail. Output caps: **≥2×22 µF X7R** (rating matches output voltage). Input caps: **≥10 µF** bulk + **220 nF** HF. Provide thermal vias under PowerPAD.

## TPS62133 (Texas Instruments) - ❌ REMOVED
- **Status**: Component removed in Rev C.4a. 5V rail eliminated in favor of single-stage 24V→3.3V conversion.
- **Replacement**: None needed. LMR33630ADDAR now performs direct 24V→3.3V conversion.
- **Rationale**: Simpler design (1 IC vs 2), fewer components, better reliability.
- **Reference**: See `5V_RAIL_ELIMINATION_SUMMARY.md`

## TPS22919 (Texas Instruments)
- **Function**: 5 V 2 A load switch with controlled slew-rate and reverse-current blocking when disabled.
- **Use case**: Disconnect USB VBUS-derived rail from main 5 V domain; avoids backfeeding the 24 V buck when only USB is present.
- **Specs**: VIN 1.62–5.5 V, R_ON ≈ 71 mΩ @ 5 V, rise time ≈ 130 µs with default slew control.

## TLV75533 (Texas Instruments)
- **Function**: 500 mA low-dropout regulator, VIN 2.0–5.5 V, VOUT fixed 3.3 V with 1 % accuracy. Intended for the USB-only programming rail.
- **Thermals**: θJA ≈ 73 °C/W in WSON/DBV-class packages; needs a modest copper pour but stays within limits at ≤250 mA programming load.
- **Protection**: Built-in current limit and thermal shutdown; enable pin is driven by the TPS22919 output so the LDO only wakes when USB is the sole power source.
- **Datasheet**: See TI product page for TLV755P/TLV75533.

## LMR/TLV Buck-LDO Interaction (USB Mode)
- **Sequence**: When 24 V is absent and USB is connected, TPS22919 enables TLV75533 to power the ESP32 (radios kept off to stay <250 mA). When 24 V is present, the USB path is disabled, preventing dual-feed.

## Battery Divider (ESP32‑S3 ADC1)
- **Locked values:** 140 kΩ (high, ERA-3AEB1403V) / 10.0 kΩ (low, ERA-3AEB1002V), 1%. 6S max 25.2 V → 1.68 V at ADC with 12 dB attenuation.
- **RC at pin:** 1–4.7 kΩ series + 0.1 µF to GND placed at the MCU pin.
- **Firmware:** Store 2‑point calibration in NVS and use multisampling to reduce noise.

## LM5069 Variant Note
- Confirm MM‑1 (latch) vs MM‑2 (auto‑retry). Use Rsense ≈ 55 mV / ILIM; e.g., ILIM 18 A → Rsense ≈ 3.0 mΩ (~3.0 mΩ stuffed). Circuit breaker ~105 mV/Rsense; select dv/dt cap to limit inrush ≤ ~0.5·ILIM.

## Supporting Components
- **SMBJ33A TVS**: 33 V standoff bidirectional TVS rated 600 W for battery surge suppression.
- **Shunts**: 2 mΩ, 2512 metal-element resistors (Bourns CSS2H-2512 or equivalent) rated ≥5 W pulse for BLDC phase sensing; 3.0 mΩ 4-terminal shunt for LM5069 sense.

These notes ensure each critical IC's operating window, control pins, and project-specific constraints are documented before schematic capture.
