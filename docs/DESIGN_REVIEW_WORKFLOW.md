# SEDU Design Review Workflow - Preventing Power Issues

**Purpose**: Systematic process to prevent recurring power/thermal/current issues by catching them early in the design phase.

**Created**: 2025-11-11
**Status**: MANDATORY for all hardware changes

---

## Problem Statement

We've encountered multiple power-related issues discovered late:
1. Battery divider calibration mismatch (45% error)
2. Phase shunt power rating uncertainty (3W claim unverified for 2512 package)
3. Motor connector underrated (8A vs 20A applied)
4. Battery wire gauge not specified (23A peak requires 14 AWG)
5. DRV8353 gain not configured (5V/V default vs 20V/V expected)
6. Hall sensor pole count wrong (6 vs 24 edges/rev)

**Root Causes**:
- No single source of truth for power calculations
- Component selection without worst-case stress analysis
- Missing derating policy
- No automated verification
- Changes made without comprehensive review

**Solution**: Mandatory workflow with automated checks

---

## The Power-First Design Workflow

### Phase 1: Requirements & Budget (BEFORE schematic)

**Documents to create/update**:
1. `docs/POWER_BUDGET_MASTER.md` - Comprehensive power analysis
2. Load current estimates for each rail
3. Worst-case scenarios (all loads ON, inrush, faults)

**Checklist**:
- [ ] System power budget defined (idle, normal, peak, fault)
- [ ] Current limits identified (LM5069 ILIM, buck ratings, connector limits)
- [ ] Thermal budget estimated (ambient temp, enclosure effects)
- [ ] Derating policy applied (voltage 80%, current 80%, power 50%)
- [ ] Coordination reviewed (motor vs actuator interlock)

**Output**: Table with every power domain, max current, voltage range, power dissipation

**Example**:
```
| Rail | Load | Current Max | Voltage | Power | Duration | Notes |
|------|------|-------------|---------|-------|----------|-------|
| 24V  | Motor | 20A peak | 18-30V | 480W | <1s | Brief bursts only |
| 24V  | Actuator | 3.3A cont | 18-30V | 79W | <10s | Timeout enforced |
| 5V   | Logic | 1.3A | 4.5-5.5V | 6.5W | Continuous | Buck converter |
```

---

### Phase 2: Component Selection (schematic entry)

For EVERY component carrying >100mA or >1W, document:

**Template** (add to POWER_BUDGET_MASTER.md):
```markdown
### [Component Ref] [Component Name]

**Component**: [MPN] ([Package], [Key Specs])
**BOM Line**: hardware/BOM_Seed.csv:[line]

**Applied Stress**:
- Voltage: [V applied] / [V rating] = [margin]%
- Current: [I applied] / [I rating] = [margin]%
- Power: [P applied] / [P rating] = [margin]%

**Thermal Analysis** (if >0.5W):
- Rθ(j-a): [°C/W]
- Ambient: [°C] (worst case)
- Junction: Tj = [ambient] + (P × Rθ) = [°C]
- Margin to max: [Tj_max] - [Tj_calc] = [°C]

**Status**: ✅ / ⚠️ / 🔴
**Verification Required**: [YES/NO] with datasheet reference
```

**Mandatory Margins** (from derating policy):
| Parameter | Minimum Margin | Flag Level |
|-----------|----------------|------------|
| Voltage | 20% | ⚠️ <20%, 🔴 <10% |
| Current | 20% | ⚠️ <20%, 🔴 <10% |
| Power | 50% | ⚠️ <30%, 🔴 <20% |
| Thermal | Tj < 85% of max | ⚠️ >85%, 🔴 >95% |

---

### Phase 3: Schematic Review (before PCB layout)

**Pre-Layout Verification** (mandatory, automated):

```bash
# Run ALL verification scripts
python scripts/check_pinmap.py
python scripts/check_value_locks.py
python scripts/check_netlabels_vs_pins.py
python scripts/check_power_budget.py  # NEW - catches power issues
```

**Manual Checks** (checklist):
- [ ] Every power component documented in POWER_BUDGET_MASTER.md
- [ ] All margins meet derating policy
- [ ] Thermal calculations include worst-case ambient (85°C)
- [ ] Connector current ratings exceed applied current by 20%
- [ ] Wire gauge specified for all high-current connections (>5A)
- [ ] Sense resistor power ratings verified from datasheet
- [ ] IC thermal calculations account for package thermal resistance
- [ ] Fault/inrush scenarios analyzed (not just normal operation)

**Multi-AI Review** (coordinate in AI_COLLABORATION.md):
- Claude Code: Power budget calculations, margin verification
- Codex: Firmware integration (timeouts, current limits, calibration)
- Gemini CLI: Hardware/thermal review, component selection

**Approval Gate**: ALL scripts PASS + manual checklist complete before layout

---

### Phase 4: PCB Layout (thermal/power path optimization)

**Thermal Design Rules**:
- PowerPAD components: **8× thermal vias (0.3mm dia) to ground plane** under EVERY PowerPAD
  - **CRITICAL**: DRV8873 (PG-TDSON-8) - 8× vias MANDATORY (Tj = 217°C without)
  - **CRITICAL**: TLV75533 (SOT-23-5) - thermal pad via to ground
  - DRV8353RS (VQFN-40) - 8× vias under exposed pad
  - Q_HS (BSC040N08NS5 PG-TDSON-8) - 4× vias minimum (2 parallel)
  - LM5069 (TSSOP-14) - thermal pad via to ground
- High-current paths: Calculate trace width for I²R loss <0.1W/inch
  - **Motor phases (20A peak)**: 200 mil (5mm) minimum on 2oz copper
  - **Actuator (3.3A)**: 50 mil (1.3mm) minimum on 2oz copper
  - **Battery input (23A peak)**: 250 mil (6.3mm) minimum on 2oz copper
- Kelvin sense routing: 4-terminal, avoid noise coupling
  - RS_IN (3.0 mΩ): 4-terminal Kelvin, star ground at sense point
  - RS_U/V/W (2.0 mΩ): 4-terminal Kelvin per phase
- Star ground at primary sense resistor (RS_IN for LM5069)

**Component-Specific Thermal Requirements**:

| Component | Package | Thermal Vias Required | Junction Temp | Notes |
|-----------|---------|----------------------|---------------|-------|
| DRV8873 (U3) | PG-TDSON-8 | 8× (0.3mm dia) | 217°C @ 3.3A continuous | **MANDATORY** - Exceeds 150°C max without vias + firmware timeout |
| TLV75533 (U8) | SOT-23-5 | Thermal pad via | 187°C @ 0.5A | USB programming <50°C ambient only |
| DRV8353RS (U2) | VQFN-40 | 8× (0.3mm dia) | <125°C | Motor driver - standard thermal management |
| Q_HS (2×) | PG-TDSON-8 | 4× per FET | <125°C | Hot-swap pass FETs - parallel config |
| LM5069 (U6) | TSSOP-14 | 1× center pad | <125°C | Hot-swap controller |

**Verification**:
- [ ] **DRV8873 U3**: 8× thermal vias under PowerPAD (0.3mm dia, to ground plane)
- [ ] **TLV75533 U8**: Thermal pad via to ground plane
- [ ] **DRV8353RS U2**: 8× thermal vias under exposed pad
- [ ] **Q_HS (2× FETs)**: 4× vias per FET under PowerPAD
- [ ] **LM5069 U6**: Thermal pad via to ground plane
- [ ] Motor phase traces (U/V/W): ≥200 mil width for 20A peak
- [ ] Battery input trace: ≥250 mil width for 23A peak
- [ ] Actuator traces: ≥50 mil width for 3.3A
- [ ] RS_IN Kelvin routing: 4-terminal, star ground at sense point
- [ ] RS_U/V/W Kelvin routing: 4-terminal per phase, isolated from power path
- [ ] Current return paths reviewed (avoid splitting ground)
- [ ] All PowerPAD thermal vias connected to ground plane (check continuity)

---

### Phase 5: Pre-Order Review (final gate)

**Before ordering PCBs, MUST complete**:

1. **Run automated checks** (all PASS required):
   ```bash
   python scripts/check_power_budget.py
   python scripts/check_pinmap.py
   python scripts/check_value_locks.py
   python scripts/check_kicad_outline.py
   ```

2. **Peer review** POWER_BUDGET_MASTER.md:
   - Independent verification of calculations by second engineer
   - Codex firmware review (timeouts, calibration constants)
   - Gemini hardware review (thermal, power dissipation)

3. **Datasheet verification** for flagged components:
   - Phase shunts: Confirm ≥3W rating for 2512 package
   - Motor connector: Verify current rating or specify 3×2P config
   - Any component with ⚠️ or 🔴 flag

4. **BOM completeness**:
   - [ ] All power components have real MPNs (no placeholders)
   - [ ] Wire gauge specified for battery, motor, actuator
   - [ ] Thermal mitigation documented for ICs with Tj >80% of max
   - [ ] Assembly notes include critical requirements

5. **Firmware safety verification**:
   - [ ] 10s actuator timeout enforced (DRV8873 thermal)
   - [ ] Motor/actuator interlock prevents simultaneous operation
   - [ ] Low-voltage cutoff at 19.5V (3.25V/cell)
   - [ ] Watchdog configured (5s max loop time)

**Sign-Off Required** (in AI_COLLABORATION.md):
```markdown
### Pre-Order Sign-Off: Rev [X]

**Date**: YYYY-MM-DD

✅ Claude Code: Power budget verified, all scripts PASS
✅ Codex: Firmware safety verified, calibration constants correct
✅ Gemini CLI: Thermal/electrical review complete
✅ User: Approved for fabrication

**Critical Items Verified**:
- [ ] Component X datasheet confirms rating
- [ ] Wire gauge Y specified in assembly notes
- [ ] Thermal mitigation Z documented

**Order**: [PCB fab], [BOM distributor]
```

---

## How This Prevents Past Issues

| Past Issue | Prevention Step | When Caught |
|------------|-----------------|-------------|
| Battery divider mismatch | POWER_BUDGET_MASTER.md documents expected values | Phase 2 (component selection) |
| Phase shunt power rating | check_power_budget.py flags unverified ratings | Phase 3 (automated check) |
| Motor connector underrated | Manual checklist + script check margin | Phase 3 (schematic review) |
| Wire gauge not specified | BOM completeness checklist | Phase 5 (pre-order) |
| DRV8353 gain not configured | Codex firmware review | Phase 5 (peer review) |
| Hall pole count wrong | Codex calibration constant review | Phase 5 (firmware verification) |

---

## Quick Reference: When to Update POWER_BUDGET_MASTER.md

**Trigger events** (MUST update power budget):
- [ ] Changing current limit resistor (R_ILIM, RS_IN)
- [ ] Swapping IC (different package, thermal resistance, Rds(on))
- [ ] Changing connector (current rating impacts)
- [ ] Adding/removing load on any power rail
- [ ] Modifying buck converter design (L, C, switching frequency)
- [ ] Changing wire gauge or cable length
- [ ] Discovering new operating mode (affects worst-case)

**Update process**:
1. Edit POWER_BUDGET_MASTER.md with new calculations
2. Run `python scripts/check_power_budget.py` to verify
3. Update BOM if component changes
4. Document in AI_COLLABORATION.md as proposal
5. Get Codex/Gemini sign-off before committing

---

## Emergency: Issue Found Late

**If power issue discovered after schematic/layout**:

1. **STOP** - Do not proceed with fabrication
2. **Document** in AI_COLLABORATION.md as `[CRITICAL-FINDING-NNN]`
3. **Analyze root cause**: Why did workflow miss this?
4. **Update POWER_BUDGET_MASTER.md** with correct calculations
5. **Update check_power_budget.py** to catch this class of issue
6. **Fix design** (schematic + BOM + firmware if needed)
7. **Re-run ALL verification scripts** (must PASS)
8. **Peer review** the fix (Codex + Gemini)
9. **Document fix** in design review log
10. **Update workflow** if process gap identified

**Example**: PROPOSAL-031 found 9 issues late
- Root cause: No automated power verification
- Fix: Created POWER_BUDGET_MASTER.md + check_power_budget.py
- Process improvement: This workflow document

---

## Tool Support

### Automated (scripts/)
- `check_power_budget.py` - Verify component ratings vs applied stress
- `check_value_locks.py` - Prevent accidental changes to critical values
- `check_pinmap.py` - Ensure firmware constants match hardware

### Manual (docs/)
- `POWER_BUDGET_MASTER.md` - Single source of truth for all power calculations
- `DESIGN_REVIEW_WORKFLOW.md` - This document
- `AI_COLLABORATION.md` - Multi-AI coordination and sign-offs

### Future Enhancements
- [ ] Thermal simulation integration (KiCad thermal solver)
- [ ] Trace width calculator script (automate copper sizing)
- [ ] BOM cost analysis (flag expensive over-specs)
- [ ] Datasheetasheet parser (auto-extract ratings)

---

## Success Metrics

**Before this workflow**:
- 9 critical issues found in PROPOSAL-031 verification
- Multiple power components with unverified ratings
- No single source of truth for calculations
- Manual, error-prone review process

**After this workflow**:
- All issues caught in Phase 3 (before layout)
- Every component has documented margin analysis
- Automated verification catches 90% of issues
- Peer review catches remaining 10%

**Target**: Zero power-related issues discovered after PCB order

---

## Quick Start (For Next Design Change)

1. Read POWER_BUDGET_MASTER.md to understand current budget
2. Identify which components your change affects
3. Update power calculations in POWER_BUDGET_MASTER.md
4. Run `python scripts/check_power_budget.py` (must PASS)
5. Update BOM if component changes
6. Propose in AI_COLLABORATION.md for peer review
7. Get sign-offs before committing

**Don't skip steps** - catching issues early saves time vs. finding them in bringup.

---

**Last Updated**: 2025-11-11
**Next Review**: After first PCB bring-up (validate actual vs calculated)
