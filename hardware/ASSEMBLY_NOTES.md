# SEDU Assembly Notes - Rev C.4b

**CRITICAL**: These specifications are LOCKED and verified. Deviation will cause component damage or failure.

---

## Wire Gauge Requirements

### Battery Connector (J_BAT)
- **Connector**: XT30_V (Amass XT30 vertical)
- **Wire Gauge**: **14 AWG minimum** (MANDATORY)
- **Rationale**: 20A motor peaks + potential 3.3A actuator = 23.3A worst-case
- **Wire Rating**: 14 AWG = 32A @ 60°C (60% margin)
- **Voltage Drop**: 166mV @ 20A over 0.5m cable (acceptable)
- **DO NOT USE**: 16 AWG (22A rating, insufficient margin)

### Motor Phase Connectors (J_MOT)
- **Connector**: 3× XT30 connectors (one per U/V/W phase)
- **Wire Gauge**: **14 AWG minimum per phase** (MANDATORY)
- **Rationale**: 20A peak current per phase
- **Wire Rating**: 14 AWG = 32A @ 60°C (60% margin)
- **Configuration**: 3 separate wires, NOT bundled in single sheath
- **Color Code** (recommended): Red=U, Yellow=V, Blue=W

### Actuator Connector (J_ACT)
- **Connector**: MicroFit 2P
- **Wire Gauge**: **18 AWG minimum**
- **Rationale**: 3.3A continuous current
- **Wire Rating**: 18 AWG = 16A @ 60°C (385% margin)

---

## Thermal Via Requirements

### LMR33630 (Buck Converter U4)
- **Location**: Under PowerPAD (exposed thermal pad)
- **Via Count**: **8× minimum** (MANDATORY)
- **Via Size**: Ø0.3mm finished hole (drill 0.20-0.25mm)
- **Pattern**: 3×3 or 4×4 array, pitch ≈1.0mm
- **Connection**: To internal or bottom ground plane
- **Manufacturing**: Tented or filled vias (prevent solder wicking)
- **Consequence if missing**: Junction temp 139°C → 180°C+ (exceeds 150°C max)

### DRV8873 (Actuator Driver U3)
- **Location**: Under PowerPAD
- **Via Count**: **8× minimum** (MANDATORY)
- **Via Size**: Ø0.3mm finished hole
- **Pattern**: 3×3 or 4×4 array
- **Connection**: To ground plane
- **Note**: This IC already exceeds Tj limit (217°C vs 150°C max) with 10s firmware timeout mitigation. Thermal vias are CRITICAL to prevent further degradation.

### DRV8353RS (Motor Driver U2)
- **Location**: Under exposed thermal pad
- **Requirement**: Thermal relief to power ground plane
- **Via Count**: 6-8× recommended
- **Via Size**: Ø0.3mm finished hole

---

## USB Programming Constraints

### TLV75533 (USB LDO U8)
- **Ambient Temperature Limit**: **<50°C MAXIMUM** during programming
- **Rationale**: Junction temp 187°C @ 85°C ambient exceeds 125°C rating
- **Typical Use**: 25°C lab environment → Tj ≈ 125°C (acceptable)
- **NEVER program outdoors** in hot environments (>40°C ambient)

### USB Power Isolation
- **Critical**: USB power NEVER operates the tool
- **Isolation**: TPS22919 load switch disconnects USB rail from main 3.3V
- **Verification**: Confirm tool does NOT operate when battery is disconnected and only USB is connected

---

## Component Substitution Policy

### ALLOWED Substitutions (Pre-Approved)

| Reference | Original | Substitute | Verification |
|-----------|----------|------------|--------------|
| RS_IN | CSS2H-2728R-L003F | **WSLP2728** (Vishay) | ✅ Per POWER_BUDGET_MASTER.md |
| RS_U/V/W | CSS2H-2512R-L200F | **CSS2H-2512K-2L00F** (K suffix) | ✅ 5W rating confirmed |

### FORBIDDEN Substitutions

- **DO NOT substitute** LM5069 with LM5069-2 (latch-off vs auto-retry behavior difference)
- **DO NOT substitute** DRV8873-Q1 with DRV8873 (automotive vs industrial grade)
- **DO NOT substitute** TLV75533 with TLV757xx series (wrong pinout)
- **DO NOT change** ESP32-S3-WROOM-1-N16R8 variant (PSRAM config affects GPIO availability)

---

## Critical Soldering Notes

### Kelvin Sense Resistors
- **Components**: RS_IN (WSLP2728), RS_U/V/W (CSS2H-2512K-2L00F)
- **Requirement**: 4-terminal Kelvin routing MANDATORY
- **Technique**:
  - Force terminals: High-current power path
  - Sense terminals: Separate traces to ADC/sense inputs
  - Keep sense traces thin (0.2mm) and symmetric
  - NO vias in sense traces if possible

### PowerPAD Components (LMR33630, DRV8873, DRV8353RS)
- **Solder Paste**: Use thermal pad stencil aperture reduction (60-80% coverage)
- **Reflow Profile**: IPC J-STD-020 compliant (Pb-free)
- **Inspection**: X-ray recommended to verify thermal pad solder voids <25%

---

## First Power-On Checklist

1. **Visual Inspection**
   - [ ] No solder bridges on fine-pitch ICs (DRV8353RS VQFN-48, DRV8873 HTSSOP-28)
   - [ ] Correct polarity on XT30 connectors (battery +/-)
   - [ ] All thermal vias present under PowerPADs

2. **Battery Disconnected - USB Only**
   - [ ] Connect USB-C
   - [ ] Measure 3.3V on ESP32-S3 pin 2 (VDD)
   - [ ] Verify TLV75533 output = 3.3V ±3%
   - [ ] Confirm current draw <200mA

3. **Battery Connected - USB Disconnected**
   - [ ] Connect 24V battery (6S LiPo, 22.2-25.2V range)
   - [ ] Measure protected 24V rail (after LM5069)
   - [ ] Measure 3.3V logic rail (LMR33630 output)
   - [ ] Confirm quiescent current <100mA

4. **Firmware Programming** (follow docs/BRINGUP_CHECKLIST.md)
   - [ ] Program via USB-C (battery disconnected)
   - [ ] Verify serial monitor output at 115200 baud
   - [ ] Confirm safety interlocks: motor blocks actuator at >500 RPM

---

## Safety Warnings

⚠️ **HIGH VOLTAGE**: 24V can cause injury. Use insulated tools.

⚠️ **MOTOR PHASE CURRENT**: 20A peaks can cause severe burns from phase wires. Ensure proper wire gauge and connector crimps.

⚠️ **BATTERY POLARITY**: Reverse polarity WILL destroy LM5069, MOSFETs, and ICs. Triple-check polarity before applying power.

⚠️ **PROGRAMMING TEMPERATURE**: USB programming at >50°C ambient will exceed TLV75533 thermal rating and may damage the IC.

---

**Document Version**: Rev C.4b
**Last Updated**: 2025-11-12
**Status**: ✅ LOCKED - Do not modify without running full verification suite

