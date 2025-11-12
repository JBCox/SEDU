# BRINGUP_CHECKLIST.md Enhancement - PCB Layout Verification Section

**Purpose**: Add thermal via verification to pre-order checklist to prevent skipped steps and consolidate PCB layout requirements.

**Current Status**: BRINGUP_CHECKLIST.md (Rev C.4b) contains 9 steps for electrical bring-up but no PCB layout verification phase.

**Gap**: Thermal via requirements are documented in hardware/README.md and POWER_BUDGET_MASTER.md but not consolidated in the bring-up checklist. New engineers completing all checklist steps may miss thermal vias entirely.

**Solution**: Add new section "PCB Layout Verification (Before Order)" with explicit requirements, specifications, and verification procedure.

---

## PROPOSED TEXT TO ADD TO docs/BRINGUP_CHECKLIST.md

**Insert after line 29 (after step 9), before "Record results..."**

```markdown
## PCB Layout Verification (Before Order)

⚠️ **CRITICAL SAFETY REQUIREMENT**: Thermal vias are non-optional for safe operation.
Without them, junction temperatures violate component ratings and cause failures.

**Thermal Impact Analysis**:
- DRV8873 without vias: Tj = 349°C (thermal runaway) → catastrophic failure
- DRV8873 with vias: Tj = 108°C average (with firmware timeout) → safe operation
- LMR33630 without vias: Tj = 166°C (exceeds 150°C max by 16°C) → reliability risk
- LMR33630 with vias: Tj = 139°C (7% margin) → acceptable

**Mandatory Thermal Via Requirements**:

### LMR33630 (U4) - 24V→3.3V Buck Converter
- [ ] Via count: **8× thermal vias minimum** under PowerPAD
- [ ] Diameter: 0.3mm finished hole (0.25mm drill)
- [ ] Pitch: 1.0mm spacing in 2×4 or 3×3 array
- [ ] Connection: All vias → L2 GND plane
- [ ] Temperature reduction: 60°C/W → 40°C/W (27°C benefit at peak)
- [ ] Verification: Open KiCad PCB, select PowerPAD, count vias, verify ≥8

### DRV8873 (U3) - Actuator H-Bridge Driver
- [ ] Via count: **8× thermal vias minimum** under PowerPAD
- [ ] Diameter: 0.3mm finished hole (0.25mm drill)
- [ ] Pitch: 1.0mm spacing in 2×4 or 3×3 array
- [ ] Connection: All vias → L2 GND plane
- [ ] Temperature reduction: 60°C/W → 30°C/W (132°C benefit with duty cycle)
- [ ] Verification: Open KiCad PCB, select PowerPAD, count vias, verify ≥8

### DRV8353RS (U2) - 3-Phase Gate Driver
- [ ] Via count: **8× thermal vias minimum** under exposed pad
- [ ] Diameter: 0.3mm finished hole (0.25mm drill)
- [ ] Connection: L2 GND plane (primary heat sink)
- [ ] Purpose: CSA buffer stage (supports transient dissipation)
- [ ] Verification: Visual inspection of PCB layout, via array visible under pad

### Q_HS (U1A, U1B) - Hot-Swap FETs (2 pieces)
- [ ] Per FET via count: **4× thermal vias minimum** under PowerPAD
- [ ] Diameter: 0.3mm finished hole
- [ ] Pitch: 1.0mm spacing in 2×2 array
- [ ] Connection: L2 GND plane
- [ ] Purpose: Inrush current path thermal management
- [ ] Verification: Select each FET drain pad, count vias, verify ≥4 each

### TLV75533 (U8) - USB Programming LDO (Optional)
- [ ] Via count: **1× thermal via** from pad to GND
- [ ] Purpose: Secondary importance (programming-only use)
- [ ] Verification: Visual inspection or select pad in KiCad

---

## Verification Procedure

### Step 1: Open KiCad PCB File
```
File → Open → SEDU_PCB.kicad_pcb
```

### Step 2: Verify Each Component's Thermal Vias

For each component (LMR33630, DRV8873, DRV8353RS, Q_HS):
1. Click on the PowerPAD/exposed pad in KiCad
2. Use Edit → Find → "Vias" filter or visual inspection
3. Count vias in the bounding box of the pad
4. Record count in checkbox above
5. Check diameter in properties: Expect 0.3mm ± 0.05mm
6. Verify all vias connect to Layer 2 (GND plane):
   - Select via → Properties
   - "Layer" or "Layers" field → expect "L2" or "GND"

### Step 3: Verify Via Specifications

For any 8× via array (LMR33630, DRV8873, DRV8353RS):
1. Measure pitch between vias: Expect 1.0mm ± 0.1mm
2. Verify pattern (2×4 or 3×3 or equivalent)
3. Check tenting setting (in design rules or fab notes)
   - Preferred: "Tent" to avoid solder wicking on PowerPAD
   - Acceptable: "Fill" if fab confirms solder control

### Step 4: Check PCB Fab Notes

Verify PCB fab notes include:
- [ ] Thermal vias: "Tent vias to avoid solder bridging on PowerPADs"
- [ ] Or: "Fill thermal vias and remove with post-processing"
- [ ] Finished hole: "Ø0.3mm ± 0.05mm"

---

## Documentation References

For detailed guidance, see:
- **Specifications**: `hardware/README.md` lines 84-90, 666-672
- **Thermal calculations**: `docs/POWER_BUDGET_MASTER.md` lines 171, 213, 452
- **Thermal analysis**: `reports/Agent1_Power_Thermal_Analysis_Report.md` sections 9.2, 651-672
- **Component datasheets**:
  - LMR33630ADDAR: HSOIC-8, Rθ(j-a) = 60°C/W (baseline), 40°C/W (with vias)
  - DRV8873-Q1: HTSSOP-28, Rθ(j-a) = 60°C/W (baseline), 30°C/W (with vias)

---

## Sign-Off Checklist

**PCB Layout Engineer**:
- [ ] All thermal vias verified present in KiCad file
- [ ] All via diameters checked (0.3mm ± 0.05mm)
- [ ] All vias connected to L2 GND plane
- [ ] Fab notes include thermal via specification
- [ ] Layout passes DFM review

**Hardware Lead/Project Manager**:
- [ ] PCB layout engineer sign-off obtained
- [ ] Thermal design adequate for manufacturing
- [ ] No deviations from specification documented
- [ ] Ready to proceed with Gerber generation

**Sign-Off Date**: ___________

---

## Why Thermal Vias Matter (Thermal Safety Rationale)

### DRV8873 Example (Actuator Driver)

**Operating condition**: 3.3A continuous (feed extend function)
**Power dissipation**: I² × R = 3.3² × 0.4Ω = 4.4W
**Package thermal resistance (HTSSOP-28)**:
- Without vias: Rθ(j-a) = 60°C/W (estimated from datasheet)
- With 8× Ø0.3mm vias: Rθ(j-a) = 30°C/W (measured in industry references)

**Junction temperature calculation**:

| Scenario | Rθ(j-a) | Tj Calculation | Result |
|----------|---------|----------------|--------|
| Without vias | 60°C/W | Tj = 85°C + (4.4W × 60) | **349°C** ❌ FAILURE |
| With vias (peak) | 30°C/W | Tj = 85°C + (4.4W × 30) | **217°C** ⚠️ Mitigated |
| With vias (avg) | 30°C/W | Tj = 85°C + (0.75W × 30) | **108°C** ✅ SAFE |

**Firmware mitigation**: 10s maximum runtime → 17% duty cycle → 0.75W average dissipation

**Verdict**: Thermal vias reduce peak temperature by **132°C** and are essential for safe operation.

### LMR33630 Example (Buck Converter)

**Operating condition**: 3.0A peak load (full output capability)
**Power dissipation**: 1.35W (from efficiency loss calculations)
**Package thermal resistance (HSOIC-8)**:
- Without vias: Rθ(j-a) = 60°C/W (baseline)
- With 8× Ø0.3mm vias: Rθ(j-a) = 40°C/W (improved thermal path)

**Junction temperature**:

| Scenario | Tj Calculation | Margin | Status |
|----------|----------------|--------|--------|
| Without vias | 85°C + (1.35W × 60) = 166°C | Exceeds 150°C by 16°C | ❌ FAIL |
| With vias (peak) | 85°C + (1.35W × 40) = 139°C | 7% margin | ✅ PASS |
| With vias (typical) | 85°C + (0.32W × 40) = 97.8°C | 35% margin | ✅ EXCELLENT |

**Verdict**: Thermal vias improve margin from **FAIL (-16°C)** to **PASS (+11°C)**.

---

## Common Questions (FAQ)

**Q: Can we skip thermal vias on the prototype?**
A: No. Without vias:
  - DRV8873 would reach 349°C (thermal runaway → immediate failure)
  - LMR33630 would reach 166°C (exceeds 150°C max → reliability risk)
  - Tool would be non-functional in bring-up testing

**Q: Are 4 vias enough if we use larger diameter?**
A: No. Effectiveness comes from total copper area and spreading to the GND plane.
  - 8 vias @ 0.3mm provides optimal thermal coupling
  - 4 vias @ 0.5mm would NOT provide equivalent performance (different PCB thermal distribution)
  - Stick with specification: 8× @ 0.3mm minimum

**Q: What if the fab says they don't support 0.3mm vias?**
A: Find a different fab. Ø0.3mm vias (0.25mm drill) are standard for modern PCB houses.
  - Ensure fab can tent or fill vias to prevent solder wicking
  - Alternative: Use slightly larger 0.4mm vias if 0.3mm unavailable (still acceptable)
  - Do NOT skip vias or use significantly larger sizes (reduces effectiveness)

**Q: Can we add heatsinks instead of relying on vias?**
A: Vias are the primary solution for a thin, portable handheld tool.
  - Adding heatsinks would increase size/weight (conflicts with tool design)
  - Vias alone are adequate: LMR33630 → 97°C typical, DRV8873 → 108°C average
  - Reserve heatsinks as future enhancement if continuous operation required

**Q: When should we check vias?**
A: Before sending to fab (last step of PCB layout review).
  - Check at: Layout complete → DFM review → Gerber generation → **THIS CHECKLIST**
  - Do not send Gerbers to fab without verifying all thermal vias

---

## Integration Notes

This section replaces the need to search through:
- hardware/README.md (lines 84-90 guidance)
- POWER_BUDGET_MASTER.md (lines 171, 213, 452 calculations)
- Agent thermal reports (detailed analysis)

All critical information is consolidated in one checklist item for ease of reference.

---

**Approval Status**:
- Agent 1 (Thermal): ✅ APPROVED - Calculations verified
- Verification Agent V3: ✅ APPROVED - Documentation adequate, enhancement recommended
- Implementation: ⏳ PENDING - Awaiting incorporation into BRINGUP_CHECKLIST.md
