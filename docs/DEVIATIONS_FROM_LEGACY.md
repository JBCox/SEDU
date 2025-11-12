# Deviations from Legacy SEDU Harness

These items differ from the original VESC + ESP32-C6 dev board + DRV8871 wiring. Call them out in schematics, BOM notes, and design reviews.

1. **Actuator Driver Upgrade:** DRV8873-Q1 (PH/EN) replaces DRV8871. Provides configurable ILIM, integrated diagnostics, and automotive rating. Control signals still originate from the ESP32 but include redundant discrete Start/Stop GPIO lines.
2. **Integrated Motor Stage:** DRV8353RS gate driver + onboard MOSFETs replace the external VESC 4.12 module. No UART-only VESC fallback connector is populated.
3. **GPIO Reassignment:** MCPWM outputs moved to GPIO38–43 (IO35–37 unavailable with PSRAM modules). Button ladder ADC now uses GPIO4, battery ADC uses GPIO1, and dedicated Start/Stop digital GPIOs (23/24) supplement the ladder for redundancy.
4. **Programming Power Path:** USB-C (if populated) uses TPS22919 + TLV75533 for a 3.3 V dev rail with radios disabled. Tool operation always uses the battery rail; the legacy design sometimes powered logic directly from the VESC 5 V output.
5. **Display Lock:** GC9A01 240×240 SPI panel is the required LCD. Document its connector pinout, current draw, and 3.3 V requirement; MISO remains NC.

Any further deviations must be appended here with date, rationale, and impacted documents.
