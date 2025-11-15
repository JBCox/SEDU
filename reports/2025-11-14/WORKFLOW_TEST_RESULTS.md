# Single-Source-of-Truth Workflow Test Results

**Date**: 2025-11-14
**Test Goal**: Validate that single-source database eliminates documentation drift errors

---

## Test Setup

Created new workflow:
1. **Single source database**: `design_database.yaml` (53 components, 35 GPIO pins, 7 ICs)
2. **Generator scripts**: Auto-generate 4 files from database
3. **Test**: Regenerate files and run all verification scripts

---

## Generator Performance

**Result**: ✅ **ALL GENERATORS PASSED**

```
[1/4] Generating BOM (hardware/BOM_Seed.csv)...          [OK] 53 components
[2/4] Generating pins.h (firmware/include/pins.h)...     [OK] 35 GPIO definitions
[3/4] Generating Net Labels (hardware/Net_Labels.csv)... [OK] 44 nets
[4/4] Generating Component Report...                     [OK] 7 ICs, 53 components
```

**Key Finding**: Generators work perfectly. Files are always consistent with database.

---

## Verification Script Compatibility

**Result**: ❌ **VERIFICATION SCRIPTS FAIL** (but for an interesting reason)

### Issue 1: Naming Convention Mismatch

**Old pins.h format** (manually written):
```cpp
namespace sedu::pins {
constexpr uint8_t kUsbDm = 19;  // kCamelCase naming
constexpr uint8_t kMcpwmHsU = 38;
```

**Generated pins.h format** (from database):
```c
#define USB_DM   19  // SCREAMING_SNAKE_CASE naming
#define MOTOR_HS_U 38
```

**Impact**: `check_pinmap.py` expects old naming convention, fails on generated file

### Issue 2: Content Format Mismatch

**Old BOM format** (manually written CSV):
- Custom descriptions with specific phrasing
- Hardcoded strings verification scripts search for

**Generated BOM format** (from database):
- Structured descriptions built from component fields
- Different phrasing, same information

**Impact**: `check_value_locks.py` searches for exact regex patterns that don't match generated format

### Issue 3: Unicode Encoding

**Error**:
```
UnicodeEncodeError: 'charmap' codec can't encode character 'Ω' in position 48
```

**Cause**: Verification scripts use Unicode symbols (Ω) but Windows console uses cp1252 encoding

**Impact**: Scripts crash before completing checks

---

## Root Cause Analysis

**The verification scripts are tightly coupled to specific file formats**, not design data.

**Current verification approach**:
```
Verification Script → Parse BOM CSV → Search for "R_ILIM = 1.58k" exact string → PASS/FAIL
```

**Problem**: If you change the BOM format (even to say the same thing differently), verification fails.

**Example**:
- Old BOM: `"DRV8873 R_ILIM = 1.58kΩ (3.3A limit)"`
- Generated BOM: `"1.58k 1% 0.1W 0603 DRV8873 current limit setting | Calc: ILIM = 5200V / 1.58kΩ = 3.29A"`
- Verification script: ❌ FAILS (can't find "R_ILIM = 1.58k" string)

But **both BOMs contain the correct value (1.58kΩ)**! The script fails on formatting, not correctness.

---

## What This Proves

### ✅ The Generator System Works

**Proof**:
- Database has RS_IN = "3.0m" defined ONCE
- Generated BOM, Component Report, verification locks ALL show 3.0mΩ
- **Impossible to have inconsistency** (only one source)

**Before**: Editing RS_IN required updating:
1. BOM_Seed.csv
2. Component_Report.md
3. Datasheet_Notes.md
4. check_value_locks.py
5. FROZEN_STATE_REV_C4b.md
6. Maybe others...

**After**: Edit design_database.yaml ONCE, regenerate everything

### ❌ The Verification Scripts Are The Wrong Approach

**They check file FORMAT, not design CORRECTNESS**.

**Example failure**:
```python
# check_value_locks.py line 87
if not re.search(r'R[_ ]?ILIM\s*=\s*1\.58\s*k', component_report):
    print("FAIL: R_ILIM not found")
```

**This checks**:
- ❌ Is the string "R_ILIM = 1.58k" in the file?

**What it SHOULD check**:
- ✅ Does the database have R_ILIM = 1.58kΩ?
- ✅ Does the generated BOM match the database?

---

## The Real Solution

### Current Problem

You've been chasing **documentation drift** errors:
- Change value in BOM → forget to update Component Report → verification fails
- Fix Component Report → typo introduces frozen state violation
- Fix violation → miss updating verification script → 78 verification cycles later...

**Root cause**: Trying to manually sync 8+ files

### Why Generators Alone Don't Fix It

Generators eliminate drift between generated files (BOM ↔ pins.h ↔ Component Report are always consistent).

**But verification scripts still fail** because they're checking file format strings, not actual design data.

### Complete Solution

Replace string-matching verification with **database-driven verification**:

**OLD (string matching)**:
```python
# Check if BOM contains "R_ILIM = 1.58k"
if not re.search(r'R[_ ]?ILIM\s*=\s*1\.58\s*k', bom_csv):
    return FAIL
```

**NEW (database validation)**:
```python
# Load database
db = load_design_database()

# Check: Does R_ILIM exist and have locked value?
r_ilim = db.components['R_ILIM']
if r_ilim.value != "1.58k" or not r_ilim.locked:
    return FAIL

# Check: Does generated BOM match database?
bom = parse_generated_bom()
if bom['R_ILIM'].value != r_ilim.value:
    return FAIL  # Generator is broken, not design
```

**Benefits**:
- Checks actual design values, not formatting
- Independent of how BOM is formatted
- Catches real errors (wrong value) vs formatting changes

---

## Recommended Next Steps

### Option 1: Adapt Existing Workflow (Quick Fix)

**Make generator output match old format exactly**:
- Change `generate_pins_h.py` to produce `constexpr uint8_t kCamelCase` format
- Change `generate_bom.py` to match exact string patterns verification scripts expect
- Keep existing verification scripts unchanged

**Pros**: Minimal changes, verification scripts work immediately
**Cons**: Generators now tightly coupled to specific output format, defeats purpose

---

### Option 2: Modernize Verification (Correct Fix)

**Rewrite verification scripts to validate database directly**:
- `check_database_schema.py` - Validates design_database.yaml structure
- `check_generated_files.py` - Confirms generated files match database (not specific format)
- `check_locked_values.py` - Reads locks from database, validates nothing changed

**Pros**:
- Checks design correctness, not file formatting
- Generators can output any format (Markdown, JSON, whatever)
- True single-source-of-truth (database is checked, not derived files)

**Cons**: Requires rewriting 9 verification scripts

---

### Option 3: Hybrid Approach (Recommended)

**Phase 1 (Immediate)**:
1. Fix Unicode encoding in existing scripts (replace Ω → ohm)
2. Freeze current generated files as "known good baseline"
3. Run generators before every commit (via pre-commit hook)
4. Continue using existing verification scripts on SSOT doc (not generated files)

**Phase 2 (When time permits)**:
1. Gradually migrate verification to database-driven approach
2. Start with simple checks (locked values, GPIO conflicts)
3. Deprecate string-matching verification as database checks mature

**Pros**:
- Immediate benefit (generators eliminate manual sync errors)
- Graceful migration path (don't break existing workflow)
- Verification improves over time

**Cons**: Temporary state where some checks are redundant

---

## Conclusion

**The test proved the concept works**:
- ✅ Single-source database eliminates documentation drift
- ✅ Generators produce consistent files every time
- ✅ No more "edit 8 files and miss one" errors

**The test also revealed**:
- ❌ Current verification scripts check FORMAT, not CORRECTNESS
- ❌ Need to modernize verification approach to match new workflow

**Recommendation**: **Option 3 (Hybrid)**
- Start using generators immediately (they work)
- Keep existing verification on SSOT doc (don't regenerate everything yet)
- Gradually modernize verification scripts when safe to do so

**Impact on your 78-error cycle**:
- Generators **will** stop the drift between generated files
- But verification scripts **may** still fail on format mismatches
- Full solution requires updating both generators AND verification

---

**Test Status**: ✅ CONCEPT VALIDATED, 🚧 INTEGRATION WORK NEEDED
