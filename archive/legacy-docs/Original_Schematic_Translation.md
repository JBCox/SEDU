# SEDU Positive-Feed Drill — Original Harness Translation

**Sources used**
- `SEDU_PFD_Wiring_and_Function_v0.1.md`
- `Old_Wiring_Diagram.jpg`, `Old_Wiring_Diagram_Buttons.jpg` *(image contents not directly viewable in this CLI; descriptions below derive from the textual wiring file)*

## 1. Block-Level Topology

| Path | Description | Notes |
|---|---|---|
| Battery → VESC 4.12 | 24 V pack feeds the existing VESC controller, which powers the ElectroCraft RPX32 BLDC. | VESC also sources a regulated 5 V rail used downstream. |
| VESC 5 V → ESP32‑C6 dev board | Dev board accepts 5 V input and generates its own 3.3 V domain. | UART to VESC, SPI to LCD, GPIO to actuator H-bridge. |
| Battery → DRV8871 → Linear actuator | Pack voltage directly powers the DRV8871, which drives a 24 V linear actuator (feed lever). | Control pins from ESP32; IN1/IN2 default low via pull-downs so actuator is off at boot. |
| ESP32 3.3 V → GC9A01 LCD | SPI-connected circular LCD for UI (status, telemetry). | Logic/backlight assumed 3.3 V. |
| Buttons → ESP32 ADC | Two-button ladder (NC Stop + NO Start) mapped to one ADC input with RC filtering. | Provides discrete Start/Stop and ladder value for diagnostics. |

## 2. Power & Ground

- **Single star ground:** Battery negative, VESC ground, ESP32 ground, DRV8871 ground, and LCD ground are tied; routing guidance stresses returning high-current actuator and VESC currents directly to the star point to reduce logic noise.
- **Logic rail dependency:** ESP32 relies on the VESC’s 5 V regulator. ESP resets during drilling were observed; mitigation includes adding bulk capacitance (470–1000 µF) near the ESP32 and potentially adding a dedicated buck in future revisions.
- **Actuator supply:** DRV8871 sits on raw 24 V with local bulk capacitance to handle inrush and cable inductance.

## 3. Control Interconnects

| Signal | From | To | Implementation Notes |
|---|---|---|---|
| Motor control | ESP32 UART TX/RX | VESC UART RX/TX | Firmware uses UART commands; VESC App Timeout configured (100–200 ms) so loss of comms stops the motor. |
| Actuator drive | ESP32 GPIOs | DRV8871 IN1/IN2 | Direction + enable control; GPIOs pulled low at reset for safety. |
| LCD SPI | ESP32 SPI bus | GC9A01 | Write-only interface (SCK/MOSI/CS/DC/RST); no MISO line. |
| Button ladder | Ladder network | ESP32 ADC channel | Resistor ladder plus RC filter yields four valid voltage windows (Start, None, Stop, Fault). |

### Button Ladder Component Values

- R19 = 10 kΩ (pull-up), R20 = 100 kΩ (aux pull-up), R21 = 5 kΩ (Start NO leg), R11 = 10 kΩ (Stop NC leg), C19 = 100 nF (RC debounce).
- Ladder thresholds (at 3.3 V ADC):
  - Start: < 0.75 V
  - None: 1.55–2.10 V
  - Stop: > 2.6 V (Stop button released = closed NC path)
  - Fault: < 0.20 V or > 3.40 V for longer than the firmware debounce window

### Firmware State Machine Summary

1. **Idle**: STOP NC continuity verified, LCD shows battery %, actuator retracted.
2. **Arm** (Start pressed): ESP32 commands VESC to ramp RPM, drives actuator forward.
3. **Run**: Drill engages; telemetry shown.
4. **Retract**: Actuator retracts soon after engagement while motor maintains RPM if required.
5. **Complete**: Motor spin-down, system returns to Idle.
6. **Fault**: Any abnormal button voltage, UART timeout, or power issue forces motor stop and actuator disable.

## 4. Items Visible in the Legacy Drawings (by description)

- **Harness depiction:** Battery input feeding both the VESC block and a branch to the DRV8871 module, with shared ground returns. Exact connector part numbers were not annotated in the text; assumed screw or spade lugs per existing hardware.
- **Button PCB/wiring:** One diagram focuses on the resistor ladder board showing the two physical buttons, ladder resistor values, and the single wire returning to the ESP32 ADC; this is consistent with the value table in the wiring document.
- **LCD interconnect:** Cable from ESP32 dev board to the GC9A01 module carrying 3.3 V, GND, and SPI lines; no level shifting required.

## 5. Known Gaps vs. Available Drawings

- The JPEG files could not be rendered in this CLI session, so any mechanical dimensions, connector callouts, or wire color codes that might be present in the original images are not captured here.
- If additional attributes (wire gauges, labels, or harness routing) are needed, please provide either text annotations or exported data from the images so they can be incorporated accurately.

This document now serves as the textual “schematic” translation of the legacy multi-board system and will act as the reference when mapping functionality onto the new single-board design.
