# GitHub Issues from 5-Agent Board Analysis (2025-11-12)

## 🔴 CRITICAL PRIORITY (Must Fix Before PCB Order)

### Issue #1: [CRITICAL] Verify CSS2H-2512R-L200F power rating or substitute
**Labels**: `hardware`, `critical`, `blocking-pcb-order`

#### Problem
BOM line 5 claims 5W rating for CSS2H-2512**K** but specifies CSS2H-2512**R**-L200F. Must obtain datasheet to verify pulse power rating ≥3W.

#### Analysis
- **Applied stress at 20A peak**: P = 20² × 0.002Ω = 0.8W
- **Required rating with 50% derating**: >1.5W continuous
- **At 25A fault**: P = 25² × 0.002Ω = 1.25W (requires >2.5W rating)
- **Standard 2512 packages**: Typically 1-2W rated

#### Risk
If incorrect part ordered (R suffix instead of K), shunt resistors may fail during 20A motor peaks, causing open circuit and disabling DRV8353 current sensing.

#### Acceptance Criteria
- [ ] Obtain Bourns datasheet for CSS2H-2512R-L200F OR CSS2H-2512K-L200F
- [ ] Verify pulse power rating ≥3W for <1s bursts
- [ ] If <3W, substitute with Vishay WSLP3921 (4W, 3921 size)
- [ ] Update BOM_Seed.csv line 5 with confirmed MPN

#### Files
- `hardware/BOM_Seed.csv:5`
- `docs/POWER_BUDGET_MASTER.md:122-144`

#### References
- Found by all 5 agents in parallel analysis (2025-11-12)
- POWER_BUDGET_MASTER.md lines 461: Blocking issue before PCB order

---

### Issue #2: [CRITICAL] Add DRV8353 SPI configuration verification
**Labels**: `firmware`, `safety`, `critical`

#### Problem
DRV8353 CSA gain is written to 20V/V via SPI but not verified. If SPI communication fails (wiring fault, damaged IC), gain remains at default 10V/V, causing motor current readings to be **50% of actual value**. This breaks motor/actuator safety interlock.

#### Impact
- Interlock allows motor at 1000 RPM (firmware reads as 500 RPM)
- Simultaneous motor + actuator load exceeds LM5069 18.3A limit
- Potential circuit breaker trip or hot-swap FET thermal damage
- Safety interlock compromised

#### Current Implementation
```cpp
// firmware/src/spi_drv8353.cpp:36-42
void configure() {
  const uint16_t csa_ctrl = (0b10 << 6) | (0b111 << 3);  // Gain=20V/V
  writeRegister(0x06, csa_ctrl);
  delay(1);
  // NO READBACK VERIFICATION ❌
}
```

#### Proposed Solution
Add `readRegister()` function and verify configuration:
```cpp
uint16_t readback = readRegister(0x06);
if ((readback >> 6) & 0b11 != 0b10) {
  Serial.println("[FATAL] DRV8353 CSA gain config failed!");
  while(1) { delay(100); }  // Halt until debugged
}
```

#### Acceptance Criteria
- [ ] Add `readRegister(uint8_t addr)` function to spi_drv8353.cpp
- [ ] Verify register 0x06 bits [7:6] = 0b10 (20V/V) after write
- [ ] If verification fails, halt firmware with error message
- [ ] Add verification to bring-up checklist

#### Files
- `firmware/src/spi_drv8353.cpp:36-56`
- `firmware/include/spi_drv8353.h`

#### References
- Found by Agents 1, 2, 4, 5 in parallel analysis
- Identified as TOP CRITICAL ISSUE by Agent 4

---

### Issue #3: [CRITICAL] Document TLV75533 USB LDO temperature limitation
**Labels**: `hardware`, `documentation`, `critical`

#### Problem
TLV75533 USB LDO junction temperature reaches **187°C** at 85°C ambient (62°C over 125°C max rating). This is acceptable for development-only use but must be clearly documented.

#### Thermal Analysis
- **Package**: SOT-23-5, Rθ(j-a) = 200°C/W (no heatsink)
- **Power dissipation**: (5V - 3.3V) × 0.3A = 0.51W
- **Junction temp at 85°C ambient**: Tj = 85°C + (0.51W × 200°C/W) = **187°C**
- **At 50°C ambient**: Tj = 50°C + 102°C = **152°C** (marginal but acceptable)

#### Mitigation
USB programming only occurs during development in lab environment (<50°C). Tool never operates from USB in field.

#### Risk
Assembly technician or field engineer attempts USB programming in hot environment (e.g., 85°C tool enclosure during maintenance), exceeding LDO rating and causing failure.

#### Acceptance Criteria
- [ ] Update `hardware/BOM_Seed.csv` line 20 with temperature warning
- [ ] Add to assembly instructions: "USB programming must occur at room temperature"
- [ ] Consider adding firmware detection (battery ADC <10V = USB mode) with temperature warning

#### Files
- `hardware/BOM_Seed.csv:20`
- `docs/POWER_BUDGET_MASTER.md:336-374`

#### References
- Found by all 5 agents (unanimous)
- POWER_BUDGET_MASTER.md documents mitigation strategy

---

## ⚠️ HIGH PRIORITY (Fix Before First Testing)

### Issue #4: [WARNING] Add firmware warning for IPROPI ADC near saturation
**Labels**: `firmware`, `enhancement`, `high-priority`

#### Problem
At 3.3A actuator current, IPROPI voltage reaches 3.0V (91% of 3.3V ADC range). Limited headroom for current overshoot reduces diagnostic capability.

#### Calculation
```
At 3.3A: I_IPROPI = 3.3A / 1100 = 3.0mA
V_IPROPI = 3.0mA × 1000Ω = 3.0V
ADC reading = 3.0V / 3.3V × 4095 = 3723 counts (91%)
Margin to saturation: 9%
```

#### Impact
- If actuator stalls or ILIM increases, ADC saturates at 3.3V
- Cannot measure true current beyond 3.6A
- Diagnostic capability reduced during faults

#### Proposed Solution
Add saturation warning in `firmware/src/sensors.cpp`:
```cpp
if (vipropi > 0.90f * vref) {
  Serial.println("[WARNING] IPROPI ADC near saturation");
}
```

#### Optional Enhancement
Consider reducing R_IPROPI from 1.00kΩ to 820Ω:
- New V_IPROPI at 3.3A: 2.46V (75% of range)
- Margin increases from 9% to 25%

#### Acceptance Criteria
- [ ] Add saturation check in `ipropiAmpsFromRaw()`
- [ ] Log warning message to Serial when >90% full-scale
- [ ] Rate-limit warnings to 1/second to avoid spam
- [ ] Document in code comments

#### Files
- `firmware/src/sensors.cpp:58-63`
- `docs/POWER_BUDGET_MASTER.md:199-203`

#### References
- Found by Agents 1, 3, 4, 5
- POWER_BUDGET_MASTER.md line 203 recommends this enhancement

---

### Issue #5: [WARNING] Add sanity checks to motor current calculation
**Labels**: `firmware`, `safety`, `high-priority`

#### Problem
Motor current calculated without sanity checks. If DRV8353 CSA outputs rail (0V or 3.3V) due to hardware fault, firmware calculates nonsense values (e.g., 82A per phase) without detecting failure.

#### Example Fault Scenario
- CSA fault: All outputs stuck at 3.3V
- Calculated current: 3.3V / (0.002Ω × 20V/V) = **82.5A per phase**
- Average: 82.5A (clearly impossible, but not flagged)
- Interlock uses bogus data, could allow unsafe operation

#### Current Implementation
```cpp
// firmware/src/sensors.cpp:72-79
float motorCurrentAmpsFromRaw(...) {
  const float iu = fabsf(csaPhaseAmpsFromRaw(raw_u, vref, fullscale));
  const float iv = fabsf(csaPhaseAmpsFromRaw(raw_v, vref, fullscale));
  const float iw = fabsf(csaPhaseAmpsFromRaw(raw_w, vref, fullscale));
  return (iu + iv + iw) / 3.0f;  // No sanity checking
}
```

#### Proposed Solution
Add hardware fault detection:
```cpp
constexpr float kMaxPhysicalCurrent = 30.0f;  // Above 25A LM5069 trip
if (iu > kMaxPhysicalCurrent || iv > kMaxPhysicalCurrent || iw > kMaxPhysicalCurrent) {
  Serial.println("[ERROR] Motor CSA out of range - hardware fault");
  return 0.0f;  // Return safe value
}
```

#### Acceptance Criteria
- [ ] Add sanity check for any phase >30A
- [ ] Log error message with phase values
- [ ] Return 0.0f to prevent interlock from using bogus data
- [ ] Consider latching fault and disabling motor outputs

#### Files
- `firmware/src/sensors.cpp:72-79`

#### References
- Found by Agents 1, 2, 5
- Less critical than Issue #2 because DRV8353 has internal fault detection

---

### Issue #6: [WARNING] Verify 8× thermal vias under DRV8873 PowerPAD
**Labels**: `hardware`, `thermal`, `high-priority`

#### Problem
DRV8873 reaches **217°C** junction temperature at continuous 3.3A (67°C over 150°C rating). Thermal calculations assume Rθ(j-a) = 30°C/W, which requires proper thermal via implementation.

#### Thermal Analysis (POWER_BUDGET_MASTER.md:207-236)
- **Continuous operation**: 4.4W dissipation → Tj = 217°C ❌
- **With 10s timeout (17% duty)**: 0.75W avg → Tj = 108°C ✅
- **Requires**: 8× 0.3mm thermal vias under U3 PowerPAD to internal ground plane

#### Risk
If thermal vias are missing or inadequate:
- Rθ(j-a) could be 60-100°C/W instead of 30°C/W
- Even with 10s timeout: Tj = 85°C + (0.75W × 60°C/W) = **130°C**
- Repeated thermal cycling degrades reliability

#### Mitigation Status
✅ Firmware 10s timeout implemented (`main.ino:140-151`)
⚠️ PCB thermal design NOT VERIFIED (requires KiCad inspection)

#### Acceptance Criteria
- [ ] Open `hardware/SEDU_PCB.kicad_pcb` in KiCad
- [ ] Verify 8× 0.3mm vias under U3 (DRV8873) thermal pad
- [ ] Verify vias connect to internal ground plane (not just top copper)
- [ ] Verify via placement per datasheet recommendations
- [ ] Document via pattern in PCB layout notes

#### Files
- PCB layout: `hardware/SEDU_PCB.kicad_pcb`
- Reference: `docs/POWER_BUDGET_MASTER.md:207-237`
- Firmware: `firmware/src/main.ino:140-151` (timeout enforcement)

#### References
- Found by all 5 agents (unanimous)
- TOP CRITICAL ISSUE #1 per Agent 4 and Agent 5

---

## 🟡 MEDIUM PRIORITY (Enhancements)

### Issue #7: [BUG] Fix Unicode encoding errors in verification scripts
**Labels**: `scripts`, `bug`, `medium-priority`

#### Problem
`verify_power_calcs.py` and `check_ladder_bands.py` crash on Windows due to Unicode checkmark (✓) and arrow (↔) characters that cannot be encoded with cp1252 codec.

#### Error
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2713' in position 3
```

#### Impact
Scripts fail to run on Windows systems, but design calculations are correct (verified manually).

#### Proposed Solution
**Option A**: Replace Unicode symbols with ASCII equivalents:
- `✓` → `[OK]` or `PASS`
- `↔` → `<->` or `to`
- `×` → `x`

**Option B**: Add UTF-8 encoding wrapper:
```python
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

#### Acceptance Criteria
- [ ] Replace Unicode symbols in verify_power_calcs.py
- [ ] Replace Unicode symbols in check_ladder_bands.py
- [ ] Re-run scripts on Windows and verify they complete successfully
- [ ] All verification output readable in Windows Command Prompt

#### Files
- `scripts/verify_power_calcs.py` (line ~32)
- `scripts/check_ladder_bands.py`

#### References
- Found by all 5 agents (unanimous)
- Scripts are functionally correct, display issue only

---

### Issue #8: [BUG] Fix false positive for banned strings in documentation
**Labels**: `scripts`, `bug`, `low-priority`

#### Problem
`check_policy_strings.py` flags "TLV757" in CLAUDE.md, but this is intentional documentation of what NOT to use (anti-drift rule).

#### Context from CLAUDE.md
```markdown
**Never reintroduce**:
- TLV757xx parts (wrong LDO for USB rail)
```

This documents the CORRECT part (TLV75533) vs the banned part (TLV757xx family).

#### Proposed Solution
Exclude CLAUDE.md from banned string checks, or add context awareness to detect "avoid TLV757" patterns.

#### Acceptance Criteria
- [ ] Exclude CLAUDE.md from policy string checks (it's allowed to document banned strings)
- [ ] Or add comment in script output: "Found in CLAUDE.md (anti-drift documentation - OK)"
- [ ] Re-run script and verify exit code 0

#### Files
- `scripts/check_policy_strings.py`
- `CLAUDE.md:291` (contains intentional anti-drift documentation)

#### References
- Found by all 5 agents
- False positive, not a design issue

---

### Issue #9: [ENHANCEMENT] Implement NTC temperature monitoring
**Labels**: `firmware`, `enhancement`, `future`

#### Problem
GPIO10 (ADC1_CH9) is allocated for NTC temperature sensing but not implemented. Adding thermal monitoring would provide validation of thermal calculations and enable over-temperature shutdown.

#### Benefits
- Validate DRV8873 thermal via design during testing
- Provide early warning of thermal issues
- Enable temperature-based USB programming restriction
- Improve field diagnostics

#### Proposed Implementation
1. Add NTC reading function to `sensors.cpp`
2. Add temperature warning at >80°C
3. Add thermal shutdown at >95°C
4. Document NTC part number and beta coefficient in SSOT

#### Acceptance Criteria
- [ ] Specify NTC part number (suggest: 10kΩ @ 25°C, β=3950K)
- [ ] Document voltage divider resistor value in SSOT
- [ ] Implement `ntcTemperatureFromRaw()` function
- [ ] Add temperature thresholds to main loop
- [ ] Test during board bring-up

#### Files
- `firmware/src/sensors.cpp` (add NTC function)
- `firmware/include/pins.h:32` (GPIO10 already defined)
- `docs/SEDU_Single_PCB_Parity_Corrected_RevC4a_Final.md` (add NTC spec)

#### References
- All 5 agents noted NTC as allocated but unused
- CLAUDE.md line 279 documents as "Missing Feature"
- Would help validate Issue #6 (DRV8873 thermal) during testing

---

### Issue #10: [DOCUMENTATION] Update DOCS_INDEX.md with unindexed files
**Labels**: `documentation`, `low-priority`

#### Problem
75 files exist but are not tracked in `docs/DOCS_INDEX.md`, making it difficult to locate documentation and track completeness.

#### Missing Categories
- All firmware source files (11 files)
- All hardware files: KiCad schematics, footprints (46 files)
- Verification scripts (9 files)
- Archive datasheets (5 files)
- Other documentation (4 files)

#### Impact
- Difficult to locate documentation
- No version tracking for key documents
- Unclear which docs are authoritative vs archived

#### Acceptance Criteria
- [ ] Add all firmware source files to DOCS_INDEX.md
- [ ] Add all hardware files (KiCad, BOM) to index
- [ ] Add all verification scripts to index
- [ ] Mark deprecated files with [ARCHIVED] tag
- [ ] Re-run `check_docs_index.py` until it passes (exit code 0)

#### Files
- `docs/DOCS_INDEX.md`
- Output from `scripts/check_docs_index.py`

#### References
- Found by all 5 agents
- Documentation hygiene issue, doesn't block development

---

## Summary Statistics

**Total Issues**: 10
**Critical (blocking PCB order)**: 3
**High Priority**: 3
**Medium Priority**: 4

**By Category**:
- Hardware: 3 (Issues #1, #3, #6)
- Firmware: 4 (Issues #2, #4, #5, #9)
- Scripts: 2 (Issues #7, #8)
- Documentation: 1 (Issue #10)

**Unanimous Findings** (all 5 agents agreed):
- Issue #1: Phase shunt verification
- Issue #3: TLV75533 temperature warning
- Issue #6: DRV8873 thermal vias
- Issue #7: Script encoding errors

---

**Generated**: 2025-11-12 by 5-agent parallel analysis
**Commit**: 429f1b4 (Initial commit: SEDU Single-PCB Feed Drill)
