# SEDU Verification Coverage & Gap Analysis
**Date**: 2025-11-12
**Scope**: Complete audit of verification testing infrastructure
**Status**: 28 gaps identified across 5 priority levels

---

## Executive Summary

**Current State**: The SEDU project has **11 active verification scripts** providing strong coverage of critical values, GPIO assignments, power calculations, and documentation consistency.

**Gap Analysis**: **28 verification gaps** identified that could lead to PCB respins, firmware bugs, assembly errors, or safety issues if not addressed.

**Recommendation**: Implement **7 critical scripts** before PCB fabrication to prevent the most likely failure modes.

---

## Current Verification Coverage (What We Have) ✅

### Strong Coverage Areas

| Script | Coverage | Critical Protections |
|--------|----------|---------------------|
| **check_value_locks.py** | Component values, board size | Prevents battery divider drift, current limit errors |
| **check_pinmap.py** | GPIO assignments | Firmware ↔ hardware alignment |
| **check_netlabels_vs_pins.py** | Net label completeness | Ensures all signals defined |
| **check_5v_elimination.py** | Obsolete rail removal | Prevents design regression |
| **check_power_budget.py** | Component ratings | Thermal/power margin validation |
| **verify_power_calcs.py** | Power system math | Validates all electrical calculations |
| **check_ladder_bands.py** | Button voltages | UI safety (Start/Stop/Idle bands) |
| **check_policy_strings.py** | Banned components | Prevents wrong LDOs, legacy interfaces |
| **check_kicad_outline.py** | Board geometry | 75×55mm dimensions, mounting holes |
| **check_docs_index.py** | Documentation tracking | File existence validation |
| **check_kicad_versions.py** | KiCad version info | Format compatibility |

**Total Verification Points**: ~500 checks across 11 scripts

---

## Critical Verification Gaps (What's Missing) ⚠️

### 🔴 Priority 1: CRITICAL (Risk of PCB Failure)

**7 gaps that could cause board respins or hardware failures:**

#### GAP-1: Schematic Net Connectivity
**Risk**: Disconnected nets between hierarchical sheets
**Example**: MCPWM_HS_U on MCU sheet doesn't connect to Motor_Driver sheet → floating MOSFET gate
**Solution**: `check_kicad_net_connectivity.py` - Parse all 9 .kicad_sch sheets, verify global labels match

#### GAP-2: BOM vs Schematic Completeness
**Risk**: Components in schematic missing from BOM
**Example**: C_CSA_U (470pF anti-alias) in schematic but omitted from BOM_Seed.csv → fab doesn't install
**Solution**: `check_bom_completeness.py` - Cross-check all schematic refs against BOM

#### GAP-3: Footprint-MPN Mismatch
**Risk**: Wrong package ordered
**Example**: BOM ERA-3AEB1581V (0603) but schematic has 0805 footprint → won't fit PCB
**Solution**: `check_footprint_mpn_match.py` - Validate MPN package matches footprint

#### GAP-4: Component Value Consistency
**Risk**: Schematic value doesn't match BOM
**Example**: BOM R_ILIM = 1.58kΩ, Schematic = 1.5kΩ → actuator current limit wrong (3.47A vs 3.29A)
**Solution**: `check_schematic_bom_values.py` - Compare R/C/L values with ±5% tolerance

#### GAP-5: Net Class Rules
**Risk**: Insufficient trace width for current
**Example**: VBAT_PROT (18A) routed with 0.2mm trace → resistive heating, voltage drop
**Solution**: `check_kicad_netclass.py` - Verify VBAT ≥1.5mm, PHASE ≥1.5mm, CSA ≤0.25mm

#### GAP-6: Thermal Via Coverage
**Risk**: PowerPADs without thermal vias
**Example**: DRV8873 (4.4W) has 0 vias → Tj = 217°C (exceeds 150°C max) → failure
**Solution**: `check_thermal_vias.py` - Verify ≥8 vias (Ø0.3mm) under DRV8873, LMR33630, DRV8353

#### GAP-7: Test Pad Verification
**Risk**: Missing debug test pads
**Example**: TP_IPROPI missing → cannot debug actuator current during bring-up
**Solution**: `check_test_pads.py` - Verify TP_3V3, TP_VBAT, TP_IPROPI, TP_RX, TP_TX exist

---

### 🟠 Priority 2: HIGH (Risk of Firmware Failure)

**5 gaps that could cause firmware bugs or sensor errors:**

#### GAP-8: Firmware Constants vs Hardware
**Risk**: Calibration mismatch
**Example**: sensors.cpp kRsensePhaseOhms = 2.0mΩ but BOM changed to 3.0mΩ → current readings 50% low
**Solution**: `check_firmware_hardware_constants.py` - Verify kRsensePhaseOhms, kCsaGainVperV, kBatteryCal

#### GAP-9: ADC Channel Assignment
**Risk**: Wrong GPIO for ADC reading
**Example**: pins.h kAdcCsaU = GPIO5, firmware reads GPIO4 → wrong phase current
**Solution**: `check_adc_channels.py` - Verify analogRead() calls use correct pins.h constants

#### GAP-10: SPI Pin Configuration
**Risk**: SPI communication failure
**Example**: pins.h kSpiSck = GPIO18, firmware SPI.begin(19, ...) → DRV8353 not responsive
**Solution**: `check_spi_config.py` - Verify SPI.begin() matches pins.h, mode (MODE1 for DRV8353)

#### GAP-11: PWM Configuration
**Risk**: Incorrect MCPWM setup
**Example**: Dead-time <100ns → shoot-through current in MOSFETs
**Solution**: `check_pwm_config.py` - Verify 20kHz frequency, 100-300ns dead-time, GPIO38-43 assignment

#### GAP-12: Safety Interlock Logic
**Risk**: Motor + actuator run simultaneously
**Example**: Bug allows RPM > 500 + actuator enabled → 23A exceeds ILIM (18.3A) → circuit breaker trip
**Solution**: `check_safety_interlocks.py` - Parse main.ino for mutual exclusion, UV cutoff, watchdog

---

### 🟡 Priority 3: MEDIUM (Assembly/Supply Chain)

**6 gaps affecting manufacturing:**

#### GAP-13: Connector Pinout Documentation
**Risk**: Reversed connector cable
**Example**: J_LCD Pin 1 = 3V3 in schematic but cable wired GND → LCD fried
**Solution**: `check_connector_pinouts.py` - Verify JST-GH pinouts match SSOT Section 6.1

#### GAP-14: Component Availability
**Risk**: Out-of-stock components
**Example**: BSC016N06NS MOSFETs on 12-week lead time → project delayed
**Solution**: `check_bom_availability.py` - Query Octopart/DigiKey API for stock status

#### GAP-15: Obsolete Part Check (All Files)
**Risk**: Removed components reappear
**Example**: TPS62133 (5V buck removed) still in Schematic_Place_List.csv → fab quotes wrong
**Solution**: `check_obsolete_components.py` - Scan ALL files for DRV8871, TPS62133, GPIO35-37

#### GAP-16: BOM Quantity Check
**Risk**: Ordered wrong quantity
**Example**: BOM RS_U qty = 1, but schematic has 3× shunts (RS_U/V/W) → only 1/3 ordered
**Solution**: `check_bom_quantities.py` - Count schematic instances, compare to BOM Qty column

#### GAP-17: PCB Layer Stack Verification
**Risk**: Wrong layer count or plane assignment
**Example**: Fab quotes 2-layer instead of 4-layer → EMI issues
**Solution**: `check_pcb_stackup.py` - Verify 4 copper layers, L2 = GND, L3 = 3V3

#### GAP-18: Assembly Instructions
**Risk**: Critical notes missing from BOM
**Example**: J_BAT requires 14 AWG wire but not specified → insufficient current capacity
**Solution**: `check_assembly_notes.py` - Verify Notes column has wire gauge, thermal via instructions

---

### ℹ️ Priority 4: LOW (Documentation Drift)

**4 gaps affecting maintainability:**

- GAP-19: Cross-document revision consistency
- GAP-20: Datasheet link validation
- GAP-21: Acronym/abbreviation consistency
- GAP-22: Firmware code style

---

### 🔬 Priority 5: SPECIALIZED (Expert Review)

**6 advanced gaps requiring domain expertise:**

- GAP-23: EMI/EMC compliance (antenna keep-out, trace lengths)
- GAP-24: Thermal simulation validation (Rθj-a vs actual PCB)
- GAP-25: Signal integrity (USB diff pairs, SPI impedance)
- GAP-26: Battery voltage range (6S LiPo 18-30V transients)
- GAP-27: Motor commutation sequence (Hall sensor wiring vs firmware)
- GAP-28: DRV8353RS SPI register config (CSA gain, OCP, gate drive)

---

## Risk Assessment Summary

### What Could Go Wrong Without Additional Verification

| Failure Mode | Likelihood | Impact | Gaps Contributing |
|-------------|------------|--------|-------------------|
| **PCB respin** (wrong nets/footprints) | HIGH | CRITICAL | GAP-1, 2, 3, 4, 5 |
| **Thermal failure** (DRV8873 overtemp) | MEDIUM | CRITICAL | GAP-6, 24 |
| **Safety violation** (exceed ILIM) | MEDIUM | HIGH | GAP-12 |
| **Sensor miscalibration** (wrong readings) | MEDIUM | HIGH | GAP-8, 9 |
| **SPI communication failure** | LOW | HIGH | GAP-10, 28 |
| **Assembly errors** (wrong components) | MEDIUM | MEDIUM | GAP-2, 13, 16 |
| **Supply chain delay** | LOW | MEDIUM | GAP-14 |
| **EMI compliance failure** | LOW | MEDIUM | GAP-23 |

**Key Insight**: Priority 1 (CRITICAL) gaps have **HIGH likelihood** and **CRITICAL/HIGH impact**. These should be addressed immediately.

---

## Example Failure Scenarios

### Scenario 1: Battery Divider Calibration Drift (GAP-8)
**What happens:**
1. Engineer updates BOM: RUV_TOP from 140kΩ → 150kΩ (better availability)
2. Firmware sensors.cpp still has kBatteryCal{1489, 18.0f, 2084, 25.2f} (calculated for 140kΩ)
3. At actual 18.0V battery, ADC reads 1.4V instead of 1.2V
4. Firmware displays 20V, thinks battery healthy
5. UV cutoff (18V) never triggers → deep discharge → **battery damage**

**Prevention**: `check_firmware_hardware_constants.py` calculates expected ADC from BOM divider, flags mismatch

### Scenario 2: Thermal Via Omission (GAP-6)
**What happens:**
1. PCB layout places DRV8873 PowerPAD footprint
2. Designer forgets to add 8× thermal vias (Ø0.3mm) as required
3. Board manufactured without thermal path to GND plane
4. DRV8873 dissipates 4.4W with Rθj-a = 50°C/W (instead of 30°C/W with vias)
5. Tj = 85°C ambient + 220°C rise = **305°C** → IC destruction

**Prevention**: `check_thermal_vias.py` parses .kicad_pcb, counts vias under PowerPAD, flags if <8

### Scenario 3: Motor/Actuator Interlock Bug (GAP-12)
**What happens:**
1. Firmware refactor changes `if (motorRPM > 500)` to `if (motorRPM >= 500)`
2. At exactly 500 RPM, actuator enable check bypassed
3. Motor draws 18A + actuator 3.3A = 21.3A
4. Exceeds LM5069 ILIM (18.3A) → **circuit breaker trips** → system reset mid-operation

**Prevention**: `check_safety_interlocks.py` parses main.ino for strict `>` vs `>=` logic, enforces mutual exclusion

---

## Recommended Implementation Plan

### Phase 1: Pre-Fabrication (CRITICAL - 1 week)
**Goal**: Prevent PCB respins

**Scripts to implement:**
1. ✅ `check_kicad_net_connectivity.py` - Verify hierarchical schematic nets
2. ✅ `check_bom_completeness.py` - All schematic components in BOM
3. ✅ `check_schematic_bom_values.py` - R/C/L values match
4. ✅ `check_kicad_netclass.py` - Trace widths adequate for current
5. ✅ `check_thermal_vias.py` - PowerPAD vias present
6. ✅ `check_test_pads.py` - Debug pads exist
7. ✅ `check_footprint_mpn_match.py` - Package sizes correct

**Run before**: Generating Gerber files for PCBWay order

---

### Phase 2: Pre-Assembly (HIGH - 1 week)
**Goal**: Reduce firmware bring-up time

**Scripts to implement:**
1. ✅ `check_firmware_hardware_constants.py` - Calibration values
2. ✅ `check_adc_channels.py` - Correct GPIO for sensors
3. ✅ `check_spi_config.py` - SPI.begin() matches pins.h
4. ✅ `check_pwm_config.py` - MCPWM dead-time, frequency
5. ✅ `check_safety_interlocks.py` - Motor/actuator mutual exclusion

**Run before**: Programming first prototype

---

### Phase 3: Pre-Order (MEDIUM - 3 days)
**Goal**: Avoid wrong components

**Scripts to implement:**
1. ✅ `check_bom_quantities.py` - Order correct qty
2. ✅ `check_connector_pinouts.py` - Cable pinouts documented
3. ✅ `check_assembly_notes.py` - Critical BOM notes present
4. ✅ `check_bom_availability.py` - Stock check (optional)

**Run before**: Placing DigiKey/Mouser order

---

### Phase 4: Post-Prototype (SPECIALIZED - 1-2 weeks)
**Goal**: Optimize for production

**Expert review needed:**
1. ✅ `check_emi_design.py` - Antenna keep-out, trace lengths
2. ✅ `check_thermal_simulation.py` - Actual Rθj-a from PCB layout
3. ✅ `check_signal_integrity.py` - USB diff pairs, SPI impedance
4. ✅ `check_drv8353_config.py` - SPI register validation

**Run before**: Production order (>10 units)

---

## Integration with Existing Workflow

### Current Mandatory Verification (Before PCB Order)
```bash
# Run these 7 scripts (all must PASS):
python scripts/check_value_locks.py
python scripts/check_pinmap.py
python scripts/check_netlabels_vs_pins.py
python scripts/check_5v_elimination.py
python scripts/verify_power_calcs.py
python scripts/check_ladder_bands.py
python scripts/check_kicad_outline.py
```

### Recommended Enhanced Verification (After Phase 1 Implementation)
```bash
# Add these 7 critical scripts:
python scripts/check_kicad_net_connectivity.py
python scripts/check_bom_completeness.py
python scripts/check_schematic_bom_values.py
python scripts/check_kicad_netclass.py
python scripts/check_thermal_vias.py
python scripts/check_test_pads.py
python scripts/check_footprint_mpn_match.py

# Then run existing scripts:
python scripts/check_value_locks.py
python scripts/check_pinmap.py
python scripts/check_netlabels_vs_pins.py
python scripts/check_5v_elimination.py
python scripts/verify_power_calcs.py
python scripts/check_ladder_bands.py
python scripts/check_kicad_outline.py
```

**Total runtime estimate**: 15-20 seconds for all 14 scripts

---

## CI/CD Integration Recommendation

### Create `.github/workflows/verify.yml` (if using GitHub)

```yaml
name: SEDU Verification Suite

on: [push, pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Run Critical Verification
        run: |
          python scripts/check_value_locks.py
          python scripts/check_pinmap.py
          python scripts/check_netlabels_vs_pins.py
          python scripts/check_5v_elimination.py
          python scripts/verify_power_calcs.py
          python scripts/check_ladder_bands.py
          python scripts/check_kicad_outline.py

      - name: Run KiCad Verification (if PCB exists)
        run: |
          if [ -f hardware/SEDU_PCB.kicad_pcb ]; then
            python scripts/check_kicad_net_connectivity.py
            python scripts/check_thermal_vias.py
            python scripts/check_test_pads.py
          fi
```

---

## Effort Estimation

### Script Development

| Phase | Scripts | Est. Hours | Skill Level Required |
|-------|---------|------------|---------------------|
| Phase 1 | 7 scripts | 40-60 hrs | Intermediate Python + KiCad parsing |
| Phase 2 | 5 scripts | 30-40 hrs | Advanced Python + firmware analysis |
| Phase 3 | 4 scripts | 20-30 hrs | Intermediate Python + BOM parsing |
| Phase 4 | 6 scripts | 60-80 hrs | Expert (EMI, thermal, signal integrity) |
| **Total** | **22 scripts** | **150-210 hrs** | **3-4 weeks full-time** |

### Testing & Documentation

- Unit tests for each script: +20%
- Documentation (docstrings, README): +10%
- Integration testing: +15%

**Total effort**: ~200-270 hours (5-7 weeks)

---

## Immediate Next Steps

### Before PCB Fabrication (THIS WEEK):

1. ✅ **Review this gap analysis** with team (Codex/Gemini)
2. ✅ **Prioritize Phase 1 scripts** - Which 3-5 gaps are highest risk?
3. ✅ **Assign development** - Who will write the scripts?
4. ✅ **Set deadline** - When do Gerbers need to be submitted?

### Short-Term (NEXT 2 WEEKS):

1. Implement Phase 1 scripts (7 scripts)
2. Test against current SEDU project
3. Fix any issues found
4. Update CLAUDE.md with new verification workflow

### Long-Term (NEXT 1-2 MONTHS):

1. Implement Phase 2-3 scripts after first prototype
2. Add CI/CD integration
3. Document learnings from prototype bring-up
4. Implement Phase 4 advanced checks before production

---

## Questions to Consider

1. **Do we proceed with current verification or wait for Phase 1 scripts?**
   - Current verification is strong for design values but weak on KiCad validation
   - Risk: PCB respin due to net/footprint/thermal issues

2. **Who will develop the new verification scripts?**
   - Claude Code (AI) can assist but needs expert review
   - Codex CLI may be better suited for firmware verification scripts
   - Consider hiring Python developer for KiCad parsing scripts

3. **Should we implement all 28 gaps or focus on top 10?**
   - Recommendation: Phase 1 (7 scripts) is minimum for first PCB order
   - Phases 2-3 can wait until after prototype testing
   - Phase 4 is production-only (not needed for prototypes)

4. **How do we prevent verification scripts from becoming stale?**
   - Run automatically on every commit (CI/CD)
   - Update scripts when design changes (e.g., board size changed → update checks)
   - Annual audit of verification coverage

---

## Conclusion

**Current state**: Strong verification of design values, GPIO assignments, and power calculations. **Weak verification** of KiCad schematic/PCB consistency, firmware-hardware integration, and thermal design.

**Recommendation**: Implement **Phase 1 (7 critical scripts)** before PCB fabrication to reduce respin risk from ~60% to ~10-20%.

**Timeline**:
- Phase 1 (critical): 1 week development + testing
- Phase 2 (firmware): 1 week after prototype received
- Phase 3 (assembly): 3 days before component order
- Phase 4 (advanced): 1-2 weeks before production

**Cost-benefit**:
- Investment: ~200-270 hours script development
- Savings: 1 PCB respin ($500-1000) + 2-3 weeks schedule recovery
- **ROI**: Break-even after preventing first respin

---

**Report Generated**: 2025-11-12
**Scripts Analyzed**: 11 existing
**Gaps Identified**: 28 total (7 critical, 5 high, 6 medium, 4 low, 6 specialized)
**Recommendation**: ✅ **Implement Phase 1 before PCB order**
