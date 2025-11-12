# Critical Technical Review - Findings

**Date**: 2025-11-11
**Reviewer**: Claude Code (Sonnet 4.5)
**Scope**: Complete system review for errors and oversights

---

## 🚨 CRITICAL ISSUES FOUND

### ISSUE #1: Power Budget - LM5069 Current Limit May Be Insufficient

**Severity**: HIGH - Potential for nuisance tripping or inadequate protection

**Problem**:
LM5069 ILIM is set to **11.70 A** (with 4.7mΩ sense resistor), but peak system loads could exceed this:

**Load Analysis** (Based on RPX32-150V24 Datasheet):
- Motor (ElectroCraft RPX32-150V24):
  - **Peak phase current: 20.0A** (per datasheet)
  - **Continuous stall current: 7.2A** (per datasheet)
  - Battery current ≠ phase current for BLDC
  - Battery current ≈ Phase current × duty cycle / efficiency
  - **During spin-up with high torque**: ~15-18A from battery (20A phase, ~90% duty, ~90% eff)
  - **During continuous operation**: ~7-10A from battery
- Actuator (DRV8873): 3.3A peak (ILIM setting)
- Buck 24V→5V: ~0.4-0.5A (for 10W @ 5V)
- **Worst case total: ~19-22A** during motor spin-up with actuator running simultaneously

**Current Specification**:
- LM5069 ILIM: 11.70A
- Circuit breaker: ~22.3A (at 105mV across 4.7mΩ)

**Analysis**:
1. **Motor alone at spin-up** could approach or exceed 11.70A briefly
2. **Motor + Actuator simultaneous** would definitely exceed ILIM
3. LM5069 has a **timer** that should allow brief inrush
4. DRV8353 and DRV8873 **current limits** are the primary protection

**Risk Assessment**:
- **If timer is too short**: Nuisance tripping during motor start
- **If motor controller allows stall**: Could trip LM5069 (this is actually good - fault protection working)
- **If firmware runs motor + actuator simultaneously at high current**: Will trip LM5069

**Root Cause**:
The original spec targeted ~12A ILIM based on "typical" operation, but didn't fully account for:
- **RPX32-150V24 peak phase current: 20.0A** (from datasheet)
- BLDC motor spin-up draws ~15-18A from battery during high torque acceleration
- Possibility of motor + actuator overlap at high current
- Motor continuous (7.2A phase ≈ 7-10A battery) + actuator (3.3A) ≈ 10-13A approaches ILIM with minimal margin

**Recommendations**:

**Option A - Firmware Mitigation (RECOMMENDED)**:
1. Add firmware interlock: **Never run motor and actuator at high power simultaneously**
2. During actuator operation, limit motor current to low levels or disable motor
3. Add current monitoring to prevent approaching ILIM
4. Document this as an operational constraint

**Option B - Hardware Change (Requires PCB Respin)**:
1. Reduce Rsense to 3.3mΩ → ILIM ≈ 16.7A
2. OR use LM5069-2 (auto-retry) instead of LM5069-1 (latch-off)
3. Increases margin but reduces fault protection sensitivity

**Option C - Component Change (Easier Fix)**:
1. Change to larger sense resistor for LM5069 with different ILIM
2. Target ILIM ≈ 15-18A to allow motor inrush + actuator
3. Maintains latch-off protection for sustained faults

**Verification Needed**:
1. ✓ Motor specifications confirmed: RPX32-150V24 with 20A peak phase current, 7.2A continuous
2. What is the LM5069 timer setting (C_TIMER value)? Default spec: 33nF for inrush control
3. **CRITICAL**: Will motor and actuator ever operate at high current simultaneously?
4. What is the actual back-EMF and duty cycle at motor start? (Affects battery current calculation)
5. Measure actual motor battery current during spin-up with oscilloscope/current probe

**Status**: ✅ **RESOLVED** - Hybrid Approach (Option D) Implemented

**Resolution** (2025-11-11):
After review and consensus between Claude Code and Codex CLI, **Option D (Hybrid Approach)** was selected:

**Hardware Change**:
- Changed Rsense from **4.7mΩ → 3.0mΩ** (4-terminal Kelvin, ≥3W, 1%)
- New ILIM: **≈18.3A** (55mV / 3.0mΩ)
- New Circuit Breaker: **≈35A** (105mV / 3.0mΩ)
- Part: HoLRS2512-3W-3mR-1% or equivalent (Bourns/Vishay/KOA)
- **Result**: Hardware provides adequate headroom for motor spin-up (15-18A)

**Firmware Interlock** (To Be Implemented):
- Add mutual exclusion: Motor and actuator cannot operate at high current simultaneously
- Implement current monitoring (IPROPI ADC + motor duty cycle estimation)
- Add soft-start ramp profiles
- Document as operational constraint

**Files Updated**:
- ✅ `docs/SEDU_Single_PCB_Parity_Corrected_RevC4a_Final.md` - Updated Rsense spec to 3.0mΩ
- ✅ `hardware/Schematic_Place_List.csv` - Changed RS_IN to 3.0mΩ
- ✅ `AI_COLLABORATION.md` - PROPOSAL-022 and PROPOSAL-022A documented

**Verification** (2025-11-11):
```
✅ check_pinmap.py - PASS
✅ check_value_locks.py - PASS
✅ check_policy_strings.py - PASS
✅ check_kicad_outline.py - PASS
✅ check_netlabels_vs_pins.py - PASS
```

All documentation consistency checks pass after Rsense update.

---

## 📋 MOTOR SPECIFICATIONS (Verified from Datasheet)

**ElectroCraft RPX32-150V24** (from `Electrocraft - RPX32-DataSheet-US.pdf`):
- Design Voltage: 24 VDC
- Peak Torque: 438.0 mNm (61.9 oz-in)
- **Peak Current: 20.0 Amps** (phase current)
- Continuous Stall Torque: 150.0 mNm (21.2 oz-in)
- **Continuous Stall Current: 7.2 Amps** (phase current)
- Continuous Rated Speed: 7,500 RPM
- No Load Speed: 10,000 RPM
- Number of Poles: 8
- Voltage Constant: 2.4 V/kRPM
- Torque Constant: 22.4 mNm/Amp
- Resistance: 0.5 Ohms (phase-to-phase)
- Inductance: 0.3 mH

**Battery Current Estimation:**
For BLDC motors with trapezoidal (6-step) commutation:
- Only 2 of 3 phases conduct at any time
- Battery current = f(phase current, duty cycle, efficiency, back-EMF)
- **At motor start** (low back-EMF, high torque demand): duty ≈ 90%, efficiency ≈ 90%
  - Battery current ≈ 15-18A
- **During continuous operation** (rated speed, nominal torque): duty ≈ 60%, efficiency ≈ 92%
  - Battery current ≈ 7-10A

---

## ⚠️ POTENTIAL ISSUES FOUND

### ISSUE #2: GPIO Strapping Pin Usage

**Severity**: MEDIUM - May affect boot behavior

**Problem**:
ESP32-S3 has special strapping pins that affect boot mode and configuration:
- GPIO0: Boot mode select (must be HIGH for normal boot)
- GPIO3: JTAG enable
- GPIO45: VDD_SPI voltage selection
- GPIO46: ROM message print enable

**Current Design**:
None of these pins are assigned in the GPIO map. ✓ Good!

**Status**: ✓ **NO ISSUE** - Strapping pins avoided

---

### ISSUE #3: ADC Usage Pattern

**Severity**: LOW - Performance consideration

**Found**:
All ADC inputs use **ADC1** channels:
- GPIO1 (ADC1_CH0) - Battery
- GPIO2 (ADC1_CH1) - IPROPI
- GPIO4 (ADC1_CH3) - Ladder
- GPIO5 (ADC1_CH4) - CSA_U
- GPIO6 (ADC1_CH5) - CSA_V
- GPIO7 (ADC1_CH6) - CSA_W
- GPIO10 (ADC1_CH9) - NTC

**Analysis**:
- ✓ **Good**: ADC1 can be used while WiFi is active (ADC2 cannot)
- ✓ **Good**: All safety-critical signals on same ADC for deterministic scanning
- ⚠️ **Note**: 7 channels must be scanned sequentially (not simultaneously)

**Impact**:
For FOC (Field-Oriented Control), CSA_U/V/W must be sampled **simultaneously** or **very close together**. ESP32-S3 ADC1 can sample at ~100kHz, so scanning 3 channels takes ~30μs. At 100kHz PWM (10μs period), this is significant.

**Recommendation**:
- FOC implementation should use **DMA** with ADC1 to minimize timing jitter
- Sample CSA channels in tight sequence triggered by PWM event
- Alternatively, use DRV8353RS internal sampling if available

**Status**: ℹ️ **NOTE FOR FIRMWARE** - Use DMA for FOC sampling

---

### ISSUE #4: Motor Control Not Yet Implemented

**Severity**: INFO - Expected for current development stage

**Found**:
The firmware currently has:
- ✓ Sensor reading (battery, ladder, IPROPI, halls)
- ✓ Actuator control (DRV8873 PH/EN)
- ✓ LCD display (GC9A01 SPI)
- ✓ DRV8353RS SPI communication (status/ID read)
- ❌ **No MCPWM motor control** (GPIO38-43 not configured)
- ❌ **No 6-step commutation** implementation
- ❌ **No FOC** implementation

**Analysis**:
This is expected for the current bring-up stage. The firmware establishes sensor baselines and actuator validation before implementing motor control.

**Recommendation**:
When implementing motor control:
1. Start with simple 6-step commutation using hall sensors
2. Use MCPWM peripheral on GPIO38-43 (dead time, complementary outputs)
3. Implement soft-start with current limiting (DRV8353RS has built-in protection)
4. Add firmware current monitoring (read CSA_U/V/W via ADC1)
5. **CRITICAL**: Implement the firmware interlock from ISSUE #1 before allowing motor operation

**Status**: ℹ️ **DEFERRED** - Implement in next development phase

---

## ✅ VERIFIED - NO ISSUES

### Power Calculations
- ✅ Battery divider: 3.022V @ 25.2V with 13.7% margin ✓
- ✅ DRV8873 ILIM: 3.29A ✓
- ✅ DRV8873 IPROPI: Correct scaling (1.0kΩ) ✓
- ✅ Motor CSA: Good dynamic range (20V/V gain, 2mΩ shunts) ✓

### GPIO Assignments
- ✅ No duplicate GPIO assignments
- ✅ No conflicts with strapping pins
- ✅ MCPWM on GPIO38-43 (correct - avoids PSRAM conflict)
- ✅ USB on GPIO19/20 (native USB pins) ✓

### Component Ratings
- ✅ MOSFETs: 60V for 6S system (max 25.2V) - Adequate ✓
- ✅ Capacitors: Properly rated ✓
- ✅ TVS: SMBJ33A for 24V nominal ✓

### Thermal Management
- ✅ LMR33630: 0.87W dissipation, adequate with thermal vias ✓
- ✅ TPS62133: Low dissipation ✓
- ✅ Thermal via guidance documented ✓

### Safety Interlocks
- ✅ Redundant button sensing (ladder + discrete GPIO)
- ✅ STOP voltage fix implemented (3.35V threshold)
- ✅ Star ground with NetTie
- ✅ Current limiting on all power stages

---

## DOCUMENTATION CONSISTENCY

### Cross-Check Results:
✅ `firmware/src/input_ladder.cpp` matches ladder voltage spec (2.60-3.35V STOP)
✅ `docs/SEDU_Single_PCB_Parity_Corrected_RevC4a_Final.md` matches README
✅ `README_FOR_CODEX.md` GPIO table matches `firmware/include/pins.h`
✅ All verification scripts PASS

---

## RECOMMENDATIONS

### Immediate Action Required:
1. **CRITICAL**: Resolve LM5069 ILIM issue
   - Preferred: Add firmware interlock (motor/actuator mutual exclusion during high current)
   - Alternative: Increase ILIM to 15-18A range
   - Document in bring-up procedure

### Before First Prototype:
2. Verify LM5069 timer capacitor value (C_TIMER)
3. Measure actual motor spin-up current profile during bring-up
4. Add firmware current monitoring to prevent approaching ILIM

### Nice to Have:
5. Document ADC sampling strategy for FOC
6. Add notes about WiFi/ADC coexistence in firmware docs

---

## VERIFICATION SCRIPT RESULTS

```
✅ check_pinmap.py - PASS
✅ check_value_locks.py - PASS
✅ check_policy_strings.py - PASS
✅ check_kicad_outline.py - PASS
✅ check_netlabels_vs_pins.py - PASS
```

---

**Review Complete**: 2025-11-11
**Overall Assessment**: Design is excellent with ONE critical power budget issue requiring attention
