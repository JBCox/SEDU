# SEDU Quick Start Guide

## When Starting a New Session (After Context Clear)

### 1. Run Verification Suite ⚡
```bash
python scripts/run_all_verification.py
```

**What it does:** Runs all 9 verification scripts and reports PASS/FAIL status.

**Expected result:** All 9 scripts should PASS if system is in good state.

### 2. Read Context Documents 📚

**Essential files to review:**

1. **`VERIFICATION_SYSTEM_COMPLETE.md`**
   - Overview of database-driven verification system
   - What bugs were found and fixed
   - System architecture

2. **`FROZEN_STATE_REV_C4b.md`**
   - All locked design values (do NOT change without verification)
   - Component values: RS_IN, R_ILIM, battery divider, etc.
   - Board size: 80×50mm

3. **`design_database.yaml`**
   - THE single source of truth
   - All 117 components, 35 GPIO pins, 7 ICs
   - ONLY file you should manually edit

4. **`docs/SESSION_STATUS.md`**
   - Current development state
   - What changed recently
   - Next planned actions

### 3. Understand the Architecture 🏗️

**Single-Source-of-Truth Workflow:**

```
design_database.yaml (EDIT THIS)
         ↓
python scripts/generate_all.py
         ↓
    ┌────────┴─────────┐
    ↓                  ↓
BOM_Seed.csv    pins.h (firmware)
Component_Report.md
Net_Labels.csv
```

**Key Rules:**
- ✅ **DO** edit `design_database.yaml`
- ❌ **DON'T** edit generated files (BOM, pins.h, etc.)
- ✅ **DO** run verification scripts after any change
- ❌ **DON'T** commit if any script fails

---

## Common Tasks

### Adding a New Component

1. Edit `design_database.yaml` - add to `components:` section
2. Run `python scripts/generate_all.py`
3. Run `python scripts/run_all_verification.py` (must PASS)
4. Commit if all pass

### Changing a GPIO Pin

1. Edit `design_database.yaml` - update `gpio_pins:` section
2. Run `python scripts/generate_all.py`
3. Run `python scripts/run_all_verification.py` (must PASS)
4. Update firmware code if needed
5. Commit if all pass

### Modifying a Locked Value (CAREFUL!)

**Locked values** (in `verification_rules.locked_values`):
- Battery divider: 140kΩ / 10kΩ
- LM5069 RS_IN: 3.0mΩ
- DRV8873 R_ILIM: 1.58kΩ
- Board size: 80×50mm

**Process:**
1. Edit value in `design_database.yaml`
2. Update lock in `verification_rules.locked_values`
3. Update `FROZEN_STATE_REV_C4b.md` with justification
4. Run `python scripts/generate_all.py`
5. Run `python scripts/run_all_verification.py` (must PASS)
6. Document in `AI_COLLABORATION.md`
7. Get multi-AI approval if safety-critical
8. Commit only after approval

---

## Verification Scripts (Individual)

Run individually if you need to debug a specific area:

```bash
# Database schema validation
python scripts/check_database_schema.py

# Critical component values
python scripts/check_value_locks.py

# GPIO pin mapping (firmware ↔ database)
python scripts/check_pinmap.py

# Net label completeness
python scripts/check_netlabels_vs_pins.py

# Board geometry (80×50mm, M3 holes)
python scripts/check_kicad_outline.py

# 5V rail elimination
python scripts/check_5v_elimination.py

# Button ladder voltage bands
python scripts/check_ladder_bands.py

# Power calculations
python scripts/verify_power_calcs.py

# BOM completeness (critical IC support components)
python scripts/check_bom_completeness.py
```

---

## Understanding the Database Structure

**Key sections in `design_database.yaml`:**

```yaml
metadata:           # Project info, revision, frozen state
power_rails:        # 5 rails: VBAT, VBAT_PROT, 3V3, USB_5V, GND
ics:                # 7 ICs with full specs
components:         # 117 passive components
gpio_pins:          # 35 GPIO assignments
firmware_constants: # Calculation constants
verification_rules:
  locked_values:    # 17 critical values
  board_geometry:   # 80×50mm, mounting holes
button_ladder:      # Voltage bands for button classification
banned_components:  # Eliminated 5V rail components
banned_nets:        # Eliminated power rails
ic_required_components: # BOM dependency tracking
```

---

## Troubleshooting

### "Script failed - what do I do?"

1. **Read the error message** - scripts tell you exactly what's wrong
2. **Fix in database** - never edit generated files
3. **Regenerate** - `python scripts/generate_all.py`
4. **Re-verify** - `python scripts/run_all_verification.py`

### "I want to change a component but not sure if it's locked"

1. Check `FROZEN_STATE_REV_C4b.md` for locked values
2. Check `design_database.yaml` - `verification_rules.locked_values`
3. If locked, follow "Modifying a Locked Value" process above

### "How do I know what changed recently?"

1. Read `docs/SESSION_STATUS.md`
2. Check git log: `git log --oneline -20`
3. Read `VERIFICATION_SYSTEM_COMPLETE.md` for migration history

---

## System Status

**Current State:**
- ✅ All 9 verification scripts passing (100%)
- ✅ Database migration complete
- ✅ 78-error verification loop eliminated
- ✅ 2 critical bugs found and fixed
- ✅ Production ready for Rev C.4b

**Bugs Fixed During Migration:**
1. Button ladder data corruption (voltage bands incorrect)
2. 6 missing BOM components (IC support caps)

**System Benefits:**
- Zero documentation drift (impossible by design)
- Auto-updating verification (reads database directly)
- 370 lines of hardcoded data eliminated
- Proven bug detection (found 2 real issues)

---

## Key Files Reference

| File | Purpose | Edit? |
|------|---------|-------|
| `design_database.yaml` | Single source of truth | ✅ YES |
| `hardware/BOM_Seed.csv` | Bill of materials | ❌ NO (auto-generated) |
| `Component_Report.md` | Component documentation | ❌ NO (auto-generated) |
| `firmware/include/pins.h` | GPIO definitions | ❌ NO (auto-generated) |
| `hardware/Net_Labels.csv` | Net labels | ❌ NO (auto-generated) |
| `FROZEN_STATE_REV_C4b.md` | Locked design values | ✅ YES (with justification) |
| `CLAUDE.md` | Project instructions | ✅ YES (for workflow updates) |
| `INIT.md` | Session initialization | 📖 READ FIRST |

---

## Quick Commands

```bash
# Full verification suite
python scripts/run_all_verification.py

# Regenerate all files from database
python scripts/generate_all.py

# Check what's in the database
python scripts/check_database_schema.py

# Git status
git status

# Commit with verification
git add design_database.yaml
git commit -m "description"  # Pre-commit hook runs verification
git push
```

---

**Last Updated:** 2025-11-15 (Database migration complete, 9/9 scripts passing)
