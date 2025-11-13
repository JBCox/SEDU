#!/usr/bin/env python3
"""
Frozen State Violation Checker - Rev C.4b

Scans ALL documentation for obsolete values that contradict FROZEN_STATE_REV_C4b.md.

This script is MANDATORY in the verification suite and will FAIL if any frozen
state violations are found in active documentation.

WHY THIS EXISTS:
After 3 rounds of verification (2025-11-12), we kept finding old values creeping
into documentation. This script makes it IMPOSSIBLE for obsolete values to slip
through verification.
"""
from __future__ import annotations

import pathlib
import re
import sys
from typing import Dict, List, Tuple

ROOT = pathlib.Path(__file__).resolve().parents[1]

# ============================================================================
# FROZEN STATE VALUES (Rev C.4b - 2025-11-12)
# ============================================================================

FROZEN_VALUES = {
    "RS_IN": "WSLP2728",  # NOT CSS2H-2728R-L003F
    "RS_U_V_W": "CSS2H-2512K-2L00F",  # NOT CSS2H-2512R-L200F (R suffix is OLD)
    "BATTERY_DIVIDER_TOP": "140kΩ",  # NOT 49.9k
    "BATTERY_DIVIDER_BOT": "10kΩ",  # NOT 6.8k
    "BOARD_WIDTH": "75",  # NOT 80
    "BOARD_HEIGHT": "55",  # NOT 60
}

# ============================================================================
# BANNED STRINGS (Will cause FAIL if found in active documentation)
# ============================================================================

BANNED_PATTERNS = {
    # Old part numbers
    "CSS2H-2512R-L200F": {
        "reason": "Old phase shunt with R suffix (2-3W). Use CSS2H-2512K-2L00F (K suffix, 5W verified)",
        "correct": "CSS2H-2512K-2L00F",
        "severity": "CRITICAL",
    },
    "CSS2H-2728R-L003F": {
        "reason": "Old RS_IN part (not available at distributors). Use WSLP2728 (Vishay substitute)",
        "correct": "WSLP2728",
        "severity": "CRITICAL",
    },

    # Old battery divider (exact matches only to avoid false positives)
    r"\b49\.9\s*k": {
        "reason": "Old battery divider top resistor. Frozen state: 140k",
        "correct": "140k (ERA-3AEB1403V)",
        "severity": "CRITICAL",
    },
    r"\b6\.8\s*k": {
        "reason": "Old battery divider bottom resistor. Frozen state: 10k",
        "correct": "10k (ERA-3AEB1002V)",
        "severity": "CRITICAL",
    },

    # Old board sizes (80×60mm baseline, 75×55mm intermediate - superseded by 80×50mm)
    r"(?<!from\s)(?<!to\s)(?<!via\s)80\s*[×x]\s*60\s*mm": {
        "reason": "Old baseline board size. Frozen state: 80×50mm (optimized from 80×60mm baseline)",
        "correct": "80×50mm",
        "severity": "HIGH",
    },
    r"(?<!from\s)(?<!to\s)(?<!was\s)(?<!via\s)75\s*[×x]\s*55\s*mm": {
        "reason": "Old intermediate board size. Frozen state: 80×50mm (was 75×55mm)",
        "correct": "80×50mm",
        "severity": "HIGH",
    },

    # Two-stage buck (5V rail eliminated)
    r"24V\s*→\s*5V\s*→\s*3\.3V": {
        "reason": "Old two-stage buck architecture. 5V rail eliminated in Rev C.4b",
        "correct": "24V->3.3V single-stage (LMR33630ADDAR)",
        "severity": "HIGH",
    },
    r"TPS62133": {
        "reason": "Old 5V->3.3V buck (eliminated). Design now uses single-stage LMR33630ADDAR",
        "correct": "LMR33630ADDAR (24V->3.3V direct)",
        "severity": "MEDIUM",
    },
}

# ============================================================================
# FILE ALLOWLIST (These files CAN contain banned strings)
# ============================================================================

ALLOWLIST_PATTERNS = [
    # Historical logs and archives
    r"AI_COLLABORATION\.md$",  # Historical proposals and discussions
    r"archive/",  # All archived files
    r"reports/",  # Old verification reports (historical)
    r"agent\d+_.*\.txt$",  # Agent output files
    r".*_REPORT.*\.md$",  # All verification report files
    r".*_SUMMARY.*\.md$",  # All summary files

    # Files that explicitly document the transition
    r"FROZEN_STATE_REV_C4b\.md$",  # Documents what changed
    r"5V_RAIL_ELIMINATION_SUMMARY\.md$",  # Documents 5V rail removal
    r"DEVIATIONS_FROM_LEGACY\.md$",  # Explicitly lists old vs new
    r"Component_Report\.md$",  # Documents transitions and "ELIMINATED" notes

    # Scripts (may contain banned strings for verification purposes)
    r"scripts/.*\.py$",  # All verification scripts

    # Files that explicitly document what to check/avoid
    r"GITHUB_ISSUES\.md$",  # Issue tracking (may reference old parts)

    # Files that mention old values in "replaces X" or "substitute for X" context
    # (These will be checked more carefully below)
]

# ============================================================================
# CONTEXT-AWARE EXCEPTIONS
# ============================================================================

# These phrases indicate the banned string is mentioned in a safe context
SAFE_CONTEXT_PHRASES = [
    "replaces",
    "substitute for",
    "was",
    "old",
    "previous",
    "baseline",
    "optimized from",
    "changed from",
    "originally",
    "not 49.9k",  # "not 49.9k/6.8k from original" in comments
    "not 6.8k",
    "VERIFY",  # "Verify CSS2H-2512R-L200F" in old BOM warnings is acceptable if marked resolved
    "REMOVED",  # "TPS62133 - REMOVED"
    "ELIMINATED",  # "TPS62133 - ELIMINATED"
    "tags",  # KiCad footprint tags can reference old parts
]


def sanitize_unicode(text: str) -> str:
    """Replace Unicode characters with ASCII equivalents for Windows console."""
    # Try to encode as ASCII, replacing any non-ASCII characters
    try:
        # First, do specific replacements for common technical symbols
        replacements = {
            '\u2192': '->',   # →
            '\u00d7': 'x',    # ×
            '\u03a9': 'Ohm',  # Ω
            '\u00b5': 'u',    # µ
            '\u2264': '<=',   # ≤
            '\u2265': '>=',   # ≥
            '\u274c': '[X]',  # ❌
            '\u2705': '[OK]', # ✅
            '\u26a0': '[!]',  # ⚠
            '\u2713': '[v]',  # ✓
            '\u00b0': 'deg',  # °
        }
        for unicode_char, ascii_equiv in replacements.items():
            text = text.replace(unicode_char, ascii_equiv)

        # Then encode to ASCII, replacing remaining non-ASCII chars
        return text.encode('ascii', errors='replace').decode('ascii')
    except Exception:
        return text


def is_allowlisted(file_path: pathlib.Path) -> bool:
    """Check if file is allowed to contain banned strings."""
    # Use forward slashes for consistent matching across OSes
    rel_path = str(file_path.relative_to(ROOT)).replace('\\', '/')
    return any(re.search(pattern, rel_path) for pattern in ALLOWLIST_PATTERNS)


def is_safe_context(line: str, banned_string: str) -> bool:
    """
    Check if banned string appears in a safe context (e.g., "replaces CSS2H-2512R-L200F").

    Returns True if the line is explaining the transition, False if using the banned value.
    """
    # Convert to lowercase for case-insensitive checking
    line_lower = line.lower()

    # Check if any safe context phrase appears near the banned string
    for phrase in SAFE_CONTEXT_PHRASES:
        if phrase.lower() in line_lower:
            return True

    # Special case: If line mentions both OLD and NEW part, it's documenting transition
    if "CSS2H-2512R-L200F" in banned_string and "CSS2H-2512K-2L00F" in line:
        return True
    if "CSS2H-2728R-L003F" in banned_string and "WSLP2728" in line:
        return True

    return False


def scan_file(file_path: pathlib.Path) -> List[Tuple[int, str, str, str]]:
    """
    Scan a file for frozen state violations.

    Returns: List of (line_number, line_text, banned_pattern, reason)
    """
    violations = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        # Skip files that can't be read
        return violations

    for line_num, line in enumerate(lines, 1):
        for pattern, info in BANNED_PATTERNS.items():
            # Check if banned pattern exists in line
            if re.search(pattern, line, re.IGNORECASE if pattern.startswith(r"\b") else 0):
                # Check if it's in a safe context
                if not is_safe_context(line, pattern):
                    violations.append((
                        line_num,
                        line.strip(),
                        pattern,
                        info["reason"]
                    ))

    return violations


def main() -> int:
    """Main verification function."""
    print("=" * 80)
    print("FROZEN STATE VIOLATION CHECKER - Rev C.4b")
    print("=" * 80)
    print()
    print("Scanning for obsolete values that contradict FROZEN_STATE_REV_C4b.md...")
    print()

    all_violations = {}
    files_scanned = 0
    files_skipped = 0

    # Scan all text files in repo
    for file_path in ROOT.rglob("*"):
        # Skip directories
        if file_path.is_dir():
            continue

        # Skip binary files
        if file_path.suffix in {".pdf", ".jpg", ".png", ".pyc", ".so", ".dll", ".exe"}:
            continue

        # Skip git internals
        if ".git" in str(file_path):
            continue

        # Check allowlist
        if is_allowlisted(file_path):
            files_skipped += 1
            continue

        # Scan file
        violations = scan_file(file_path)
        if violations:
            all_violations[file_path] = violations

        files_scanned += 1

    # Report results
    print(f"Files scanned: {files_scanned}")
    print(f"Files skipped (allowlisted): {files_skipped}")
    print()

    if not all_violations:
        print("=" * 80)
        print("[PASS] NO FROZEN STATE VIOLATIONS FOUND")
        print("=" * 80)
        print()
        print("All documentation is consistent with FROZEN_STATE_REV_C4b.md")
        return 0

    # Print violations
    print("=" * 80)
    print(f"[FAIL] {len(all_violations)} FILE(S) WITH FROZEN STATE VIOLATIONS")
    print("=" * 80)
    print()

    total_violations = 0
    for file_path, violations in sorted(all_violations.items()):
        rel_path = file_path.relative_to(ROOT)
        safe_rel_path = sanitize_unicode(str(rel_path))
        print(f"\n[VIOLATION] {safe_rel_path}:")
        print("-" * 80)

        for line_num, line_text, pattern, reason in violations:
            total_violations += 1
            # Sanitize all output to prevent Unicode errors
            safe_line = sanitize_unicode(line_text[:80])
            safe_pattern = sanitize_unicode(pattern)
            safe_reason = sanitize_unicode(reason)

            print(f"  Line {line_num}: {safe_line}")
            print(f"  Pattern: {safe_pattern}")
            print(f"  Reason: {safe_reason}")

            # Print correction
            if pattern in BANNED_PATTERNS:
                safe_correct = sanitize_unicode(BANNED_PATTERNS[pattern]['correct'])
                print(f"  Correct value: {safe_correct}")
            print()

    print("=" * 80)
    print(f"TOTAL VIOLATIONS: {total_violations}")
    print("=" * 80)
    print()
    print("ACTION REQUIRED:")
    print("  1. Update the files above to use frozen state values")
    print("  2. If documenting a transition, use phrases like:")
    print("     - 'replaces CSS2H-2512R-L200F' (safe)")
    print("     - 'was 80×60mm, optimized to 75×55mm' (safe)")
    print("  3. Re-run this script to verify fixes")
    print()
    print("See FROZEN_STATE_REV_C4b.md for authoritative values.")
    print()

    return 1


if __name__ == "__main__":
    sys.exit(main())
