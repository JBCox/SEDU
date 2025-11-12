#!/usr/bin/env python3
"""Verify that the canonical spec pin map matches firmware/include/pins.h."""
from __future__ import annotations

import pathlib
import re
import sys
from typing import Dict, List, Sequence

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs" / "SEDU_Single_PCB_Parity_Corrected_RevC4a_Final.md"
PINS_PATH = REPO_ROOT / "firmware" / "include" / "pins.h"

# Mapping between doc table rows and pins.h constant names
CANONICAL_GROUPS = {
    "USB D− / D+": ("kUsbDm", "kUsbDp"),
    "MCPWM HS U/V/W": ("kMcpwmHsU", "kMcpwmHsV", "kMcpwmHsW"),
    "MCPWM LS U/V/W": ("kMcpwmLsU", "kMcpwmLsV", "kMcpwmLsW"),
    "DRV8353 SPI": ("kSpiSck", "kSpiMosi", "kSpiMiso", "kSpiCsDrv"),
    "CSA ADCs": ("kAdcCsaU", "kAdcCsaV", "kAdcCsaW"),
    "Battery ADC": ("kAdcBattery",),
    "Button ladder ADC": ("kAdcLadder",),
    "LCD (GC9A01 SPI)": ("kSpiSck", "kSpiMosi", "kSpiCsLcd"),
    "Actuator DRV8873 PH/EN": ("kActuatorPh", "kActuatorEn"),
    "Actuator IPROPI ADC": ("kAdcIpropi",),
    "Start / Stop digital": ("kStartDigital", "kStopDigital"),
    "Halls A/B/C": ("kHallA", "kHallB", "kHallC"),
    "FEED_SENSE": ("kFeedSense",),
}


def parse_doc_pins(path: pathlib.Path) -> Dict[str, List[int]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    result: Dict[str, List[int]] = {}
    collecting = False
    for line in lines:
        if line.startswith("## 4. Canonical GPIO / Signal Map"):
            collecting = True
            continue
        if collecting and line.startswith("## "):
            break
        if not collecting:
            continue
        stripped = line.strip()
        if not stripped.startswith("|") or stripped.lower().startswith("| function"):
            continue
        cols = [col.strip() for col in stripped.strip("|").split("|")]
        if len(cols) < 2:
            continue
        func, pins = cols[0], cols[1]
        func = re.sub(r"\\*", "", func).strip()
        gpio_values = [int(n) for n in re.findall(r"GPIO(\d+)", pins)]
        if gpio_values:
            result[func] = gpio_values
    return result


def parse_header_constants(path: pathlib.Path) -> Dict[str, int]:
    # Capture both numeric constants and aliases (kX = kY)
    const_pattern = re.compile(r"constexpr\s+\w+\s+(k\w+)\s*=\s*([\w\d]+)")
    raw: Dict[str, str] = {}
    for name, rhs in const_pattern.findall(path.read_text(encoding="utf-8")):
        raw[name] = rhs

    resolved: Dict[str, int] = {}

    def resolve(name: str, seen: set[str]) -> int | None:
        if name in resolved:
            return resolved[name]
        if name not in raw:
            return None
        if raw[name].isdigit():
            resolved[name] = int(raw[name])
            return resolved[name]
        target = raw[name]
        if target in seen:
            return None
        seen.add(target)
        val = resolve(target, seen)
        if val is not None:
            resolved[name] = val
        return val

    for key in list(raw.keys()):
        resolve(key, set())
    return resolved


def main() -> int:
    doc_map = parse_doc_pins(DOC_PATH)
    header_consts = parse_header_constants(PINS_PATH)
    errors = []
    for label, const_names in CANONICAL_GROUPS.items():
        doc_pins = doc_map.get(label)
        if not doc_pins:
            errors.append(f"Doc missing entry for '{label}'")
            continue
        header_pins = [header_consts.get(name) for name in const_names]
        if None in header_pins:
            missing = [name for name, val in zip(const_names, header_pins) if val is None]
            errors.append(f"pins.h missing constants: {', '.join(missing)}")
            continue
        if sorted(doc_pins) != sorted(header_pins):
            errors.append(
                f"Mismatch for '{label}': doc {doc_pins} vs pins.h {header_pins}"
            )
    if errors:
        for msg in errors:
            print(f"[pinmap] {msg}")
        return 1
    print("[pinmap] Canonical spec matches pins.h")
    return 0


if __name__ == "__main__":
    sys.exit(main())
