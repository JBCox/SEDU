# SEDU Technical Audit Report

**Date**: 2025-11-11
**Auditor**: Claude Code (Sonnet 4.5)
**Scope**: Complete system review - math, components, routing, safety
**Project State**: Rev C.4b, pre-layout

---

## Executive Summary

**Overall Assessment**: System is well-designed with professional-grade documentation and component selection. **ONE CRITICAL SAFETY ISSUE** identified that must be resolved before first prototype.

**Verification Status**:
- ✅ All automated checks passing
- ✅ Power calculations verified
- ✅ Component ratings appropriate
- ❌ **Button ladder STOP voltage out of spec** (CRITICAL)

---

## 🔴 CRITICAL ISSUES

### ISSUE #1: Button Ladder STOP Voltage Specification Mismatch

**Severity**: **CRITICAL** - Safety System Failure
**Status**: 🔴 **MUST FIX BEFORE PROTOTYPE**
**Location**: `firmware/src/input_ladder.cpp` + hardware ladder circuit

#### Problem Description:

The STOP button, when pressed, produces a voltage **outside the firmware's accepted range**, causing it to be classified as a FAULT instead of a valid STOP command.

#### Technical Analysis:

**Hardware Reality**:
- STOP button is Normally-Closed (NC)
- When pressed: NC contact opens
- BTN_SENSE pulled to VCC through R19 || R20 = 9.09 kΩ
- **Actual voltage when STOP pressed**: **3.30 V**

**Firmware Specification**:
```cpp
const float kLadderStopMin   = 2.60f;
const float kLadderStopMax   = 3.20f;  // ← Problem!
const float kLadderFaultHigh = 3.20f;
```

**Classifier Logic**:
```cpp
if (v >= kLadderStopMin && v <= kLadderStopMax)  return LadderState::kStop;  // 2.60-3.20V
return LadderState::kFaultHigh;  // > 3.20V
```

#### Calculated Voltages:

| State | Calculated | Spec Range | Status |
|---|---|---|---|
| IDLE (NC closed) | 1.73 V | 1.55-2.10 V | ✅ PASS |
| START pressed | 0.89 V | 0.75-1.00 V | ✅ PASS |
| **STOP pressed** | **3.30 V** | **2.60-3.20 V** | ❌ **FAIL** |
| FAULT_LOW | < 0.20 V | < 0.20 V | ✅ (by design) |
| FAULT_HIGH | > 3.20 V | > 3.20 V | ✅ (by design) |

#### Impact:

🚨 **When operator presses emergency STOP**:
- BTN_SENSE = 3.30 V
- Classifier returns `LadderState::kFaultHigh`
- System enters FAULT state instead of controlled STOP
- **Safety interlock behavior undefined**
- **Operator cannot safely stop the drill**

#### Root Cause:

VCC is nominally 3.3 V (ESP32-S3 operating voltage). When the NC STOP button opens, there is no voltage divider - BTN_SENSE is pulled directly to VCC. The spec incorrectly assumes STOP voltage will be ≤ 3.20 V.

#### Recommended Solutions:

**Option A: Firmware Fix (RECOMMENDED - Low Risk)**
- Change `kLadderStopMax` to **3.35 V** (allows for VCC tolerance)
- Change `kLadderFaultHigh` threshold to **> 3.35 V**
- Rationale: VCC can vary 3.0-3.6V per ESP32-S3 spec; 3.35V provides margin

**Option B: Hardware Fix (Higher Risk - Requires PCB Change)**
- Add voltage divider on STOP path to bring 3.3V down to ~3.0V
- Example: 10kΩ / 100kΩ divider
- Rationale: Keeps voltage within original spec, but adds components

**Option C: Hybrid (BEST - Defense in Depth)**
- Firmware: Expand STOP band to 2.60-3.35V
- Documentation: Note that STOP = high voltage near VCC
- Testing: Verify across VCC range (3.0-3.6V) during bring-up

---

## ✅ VERIFIED - NO ISSUES

### Power Calculations

#### LM5069-1 Hot-Swap Controller
```
Target ILIM:           12 A
Calculated Rsense:     4.58 mΩ
Actual Rsense:         4.7 mΩ (1%, 4-terminal Kelvin)
Actual ILIM:           11.70 A ✓
Circuit breaker trip:  ~22.3 A @ 105 mV ✓
Power rating:          ≥3 W ✓
```
**Status**: ✅ Correctly sized with margin

#### Battery Divider (49.9kΩ / 6.80kΩ, 0.1%)
```
6S Max Voltage:  25.2 V
ADC @ 25.2V:     3.022 V
ADC Full-Scale:  ~3.5 V (12dB atten)
Margin:          13.7% ✓
```
**Status**: ✅ Adequate margin for ADC range

#### DRV8873-Q1 Actuator Driver
```
R_ILIM:     1.58 kΩ (1%)
ILIM:       3.29 A ✓
Spec:       110-120% of continuous (target ~3.0-3.6A)
```
**Status**: ✅ Conservative current limit

```
R_IPROPI:   1.00 kΩ (1%)
@ 2.0 A:    V_IPROPI = 1.818 V ✓
@ 2.5 A:    V_IPROPI = 2.273 V ✓
@ 3.0 A:    V_IPROPI = 2.727 V ✓
@ 3.3 A:    V_IPROPI = 3.000 V ✓
ADC FS:     ~3.5 V (margin OK)
```
**Status**: ✅ Good scaling for ADC monitoring

#### LMR33630AF 24V→5V Buck
```
Vin:        24 V
Vout:       5 V
Iout:       2 A
Efficiency: 92%
Ploss:      0.87 W (matches datasheet ✓)
Thermal:    Requires thermal vias + copper pour
```
**Status**: ✅ Thermal design adequate with proper layout

#### DRV8353RS Motor CSA
```
Shunt:      2 mΩ (2512, pulse-rated)
CSA Gain:   20 V/V (locked)
@ 10 A:     V_CSA = 0.40 V ✓
@ 15 A:     V_CSA = 0.60 V ✓
@ 20 A:     V_CSA = 0.80 V ✓
@ 25 A:     V_CSA = 1.00 V ✓
ADC FS:     ~3.5 V → ±25A range ✓
```
**Status**: ✅ Good dynamic range for FOC

### Component Ratings

#### Voltage Ratings
- ✅ MOSFETs: 60V (6S max 25.2V + transients = ~35V max) - **Good margin**
- ✅ Capacitors: Rated ≥ 1.5× operating voltage
- ✅ TVS (SMBJ33A): 33V standoff for 24V nominal - **Appropriate**
- ✅ DRV8353RS: 100V rating - **Excellent headroom**
- ✅ DRV8873-Q1: 38V max (37V operating) - **Adequate for 24V**

#### Current Ratings
- ✅ LM5069 sense resistor: ≥3W @ 11.7A - **Adequate**
- ✅ Motor shunts: 2512 pulse-rated - **Appropriate**
- ✅ Buck inductors: ≥4A RMS rating specified - **Good**

#### Decoupling (DRV8353RS) - **Locked Values Verified**
- ✅ CPL-CPH: 47 nF (≥100V X7R)
- ✅ VCP-VDRAIN: 1 µF (≥16V)
- ✅ VGLS-GND: 1 µF (≥16-25V)
- ✅ DVDD: 1 µF (≥6.3V)

### GPIO Assignments

✅ **All GPIO assignments verified against ESP32-S3-WROOM-1-N16R8 constraints**:
- ✅ MCPWM on GPIO38-43 (IO35-37 avoided - PSRAM conflict)
- ✅ ADC1 channels used exclusively (ADC1_CH0/1/3/4/5/6/9)
- ✅ SPI pins non-conflicting (SCK=18, MOSI=17, MISO=21, CS_DRV=22, CS_LCD=16)
- ✅ USB on GPIO19/20 (native USB D±)
- ✅ GPIO-JTAG disabled to free MCPWM pins

### Safety Interlocks

✅ **Multiple layers verified**:
- ✅ Redundant button sensing (ladder ADC + discrete GPIO23/24)
- ✅ Fault latching (firmware requires IDLE before allowing motion)
- ✅ LM5069 latch-off on overcurrent
- ✅ DRV8353 OCP/OVP/UVLO/OT protection
- ✅ DRV8873 current limiting + fault reporting
- ⚠️ **STOP button fault classification** (see CRITICAL ISSUE #1)

---

## ⚠️ RECOMMENDATIONS

### High Priority (Before First Prototype)

1. **FIX CRITICAL**: Resolve button ladder STOP voltage issue (see above)
2. **Test Plan**: Add explicit STOP button voltage measurement to bring-up checklist
3. **Tolerance Analysis**: Document VCC tolerance effects on ladder voltages

### Medium Priority (Before Layout)

1. **Trace Width Calculations**:
   - Motor phase traces: Size for 25A peak @ 10°C rise
   - 24V power: Size for 12A continuous
   - 5V/3.3V: Standard calculator for 2A/1A

2. **Thermal Analysis**:
   - LMR33630: Thermal vias under PowerPAD (datasheet recommendation)
   - MOSFETs: Copper area for heat spreading
   - LM5069 FET: Verify SOA during inrush

3. **High-Current Return Paths**:
   - Verify star ground at LM5069 sense resistor
   - Motor phase returns direct to star point
   - Actuator return direct to star point
   - Logic ground single-point tie near LM5069

4. **EMI/ESD**:
   - Series resistors on SPI lines (22-33Ω) near MCU
   - ESD diodes on external connectors (J_UI, J_LCD)
   - Keep motor phase traces away from sensitive analog

### Low Priority (Nice to Have)

1. Add test points for all critical voltages (already specified)
2. Consider fuse on battery input (in addition to LM5069)
3. Add LED for "USB programming mode" indicator

---

## Layout Guidance (Not Yet Started)

### 4-Layer Stackup (Recommended)
```
L1: Signals + local pours (top)
L2: Solid GND plane
L3: Power planes (5V, 3.3V, 24V split) + stitching
L4: Signals + returns (bottom)
```

### Critical Routing
- **Motor phases**: Short, wide, symmetric traces; 6-8 mil min spacing
- **Gate drives**: Short loops from DRV8353 to MOSFET gates
- **CSA sense**: True Kelvin routing from shunts to DRV8353
- **ADC inputs**: RC filter at MCU pin (56-100Ω + 470pF)
- **USB D±**: 90Ω differential pair; 22-33Ω series near MCU
- **Antenna keep-out**: 15mm per datasheet

### High-Current Paths
- Battery input → LM5069 sense → protected bus: **40+ mils**
- Motor phases (U/V/W): **60+ mils** for 25A peak
- Actuator supply: **40+ mils** for 3.3A
- 5V rail: **20 mils** (2A)
- 3.3V rail: **15 mils** (1A)

---

## Verification Status

| Check | Tool/Method | Result |
|---|---|---|
| Pin map consistency | `check_pinmap.py` | ✅ PASS |
| Value locks | `check_value_locks.py` | ✅ PASS |
| Policy strings | `check_policy_strings.py` | ✅ PASS |
| Board outline | `check_kicad_outline.py` | ✅ PASS (80×60mm) |
| Net labels | `check_netlabels_vs_pins.py` | ✅ PASS |
| Power calculations | Manual (this audit) | ✅ PASS |
| **Ladder voltages** | **Manual (this audit)** | ❌ **FAIL - STOP out of spec** |
| Component ratings | Manual (this audit) | ✅ PASS |

---

## Next Steps

1. ⚠️ **IMMEDIATE**: Create proposal in `AI_COLLABORATION.md` for STOP voltage fix
2. ⚠️ **IMMEDIATE**: Get Codex + Gemini approval on fix approach
3. Implement approved fix (firmware and/or hardware)
4. Re-verify ladder voltages with tolerance analysis
5. Continue with PCB layout once resolved

---

**Audit Complete**: 2025-11-11
**Signature**: Claude Code (Sonnet 4.5)
**Status**: 🔴 **CRITICAL ISSUE IDENTIFIED - DO NOT PROCEED TO PROTOTYPE WITHOUT FIX**
